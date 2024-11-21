from uuid import UUID
from informed.query.manager import QueryManager
from informed.db_models.query import Query, QueryState
from loguru import logger as log
from informed.db import session_maker
from informed.helper.util import (
    extract_user_info,
    build_weather_query_context,
    build_system_prompt,
)
from informed.db_models.query import QuerySource
from informed.llm.schema import build_function_schema
from informed.llm.client import LLMClient
from informed.db_models.users import User
from sqlalchemy.sql import select, ColumnElement
from typing import cast, Any
import json
import asyncio
from loguru import logger as log
from fastapi import HTTPException, status
import httpx
from pydantic import BaseModel
from informed.config import WeatherSourcesConfig
from textwrap import dedent
from datetime import datetime, UTC
from informed.llm.llm import ChatState
from informed.users.manager import UserManager
from informed.services.notification_service import NotificationService

# TODO: Need to modularize this
# 1. Add more sources
# 2. Add more tools (if use case exists where we need to iterate on initial agent response)
# 3. Split into pre-process: apis + query relevance (knowledge source)
# 4. Post-process: answer formatting

# TODO: Move data models to separate file
# TODO: Move system prompt to top level file, add to system context in sub-agents
# TODO: Move each API Tool to separate file


class WeatherResponse(BaseModel):
    findings: list[str] = []


class QueryAgent:
    def __init__(
        self,
        query_id: UUID,
        query_manager: QueryManager,
        user_manager: UserManager,
        llm_client: LLMClient,
        weather_sources_config: WeatherSourcesConfig,
        notification_service: NotificationService,
    ):
        self.query_id = query_id
        self.query_manager = query_manager
        self.user_manager = user_manager
        self.llm_client = llm_client
        self.weather_sources_config = weather_sources_config
        self.notification_service = notification_service

    async def run(self) -> None:
        query = await self.query_manager.get_query(self.query_id)
        if query is None:
            raise ValueError(f"Query {self.query_id} not found")
        query.state = QueryState.PROCESSING
        await self.query_manager.persist_query(query)
        await self._run(query)

    async def _run(self, query: Query) -> None:
        user = await self.user_manager.get_user(query.user_id)
        if not user:
            raise ValueError("User not found")
        await self._process_query(query, user)

    async def _process_query(self, query: Query, user: User) -> None:
        try:
            system_prompt = build_system_prompt()
            user_info = extract_user_info(user)
            context = await build_weather_query_context(
                user,
                weather_sources_config=self.weather_sources_config,
                notification_service=self.notification_service,
            )
            user_prompt = dedent(
                f"""
                <query>
                {query.query}
                </query>
                <context>
                {context}
                </context>
                <user>
                {user_info}
                </user>
                """
            )
            chat_state = ChatState(system_prompt=system_prompt, user_prompt=user_prompt)
            output_schema = build_function_schema(
                WeatherResponse,
                description="Answer the user's question about the weather",
            )
            try:

                function = await self.llm_client.chat_completion(
                    chat_state, tools=[output_schema]
                )
                data = json.loads(function.arguments)
                weather_response = WeatherResponse.model_validate(data)

                if isinstance(weather_response, WeatherResponse):
                    log.info(f"GPT Response: {weather_response.model_dump_json()}")
                    query.state = QueryState.COMPLETED
                    query.findings = weather_response.findings
                    # TODO: Need to change after adding multiple sources
                    # Also remove this hardcoded source
                    query.sources = [QuerySource(source="https://api.weather.gov")]
                else:
                    log.error(
                        f"Unexpected response type for GPT response: {type(weather_response)}"
                    )
                    query.state = QueryState.FAILED
                    query.findings = [
                        "Sorry, I'm having some trouble answering your question. Please contact support"
                    ]

            except Exception as e:
                log.error(e)
                query.state = QueryState.FAILED
                query.findings = [
                    "Sorry, I'm having some trouble answering your question. Please contact support"
                ]

            await self.query_manager.persist_query(query)

        except asyncio.CancelledError:
            log.info("Document processing was cancelled.")
            query.state = QueryState.CANCELLED
            await self.query_manager.persist_query(query)
            raise
        except Exception as e:
            query.state = QueryState.FAILED
            await self.query_manager.persist_query(query)
            log.error(f"Error processing documents: {str(e)}")
            raise
