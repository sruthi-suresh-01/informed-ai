from uuid import UUID
from informed.query.manager import QueryManager
from informed.db_models.query import Query, QueryState
from loguru import logger as log
from informed.db import session_maker
from informed.llm.client import generate_response
from informed.helper.util import extract_user_info
from informed.db_models.weather import WeatherData
from informed.db_models.users import User
from sqlalchemy.sql import select, ColumnElement
from typing import cast, Any
import json
import asyncio
from loguru import logger as log
from fastapi import HTTPException, status


class QueryAgent:
    def __init__(self, query_id: UUID, query_manager: QueryManager):
        self.query_id = query_id
        self.query_manager = query_manager

    async def run(self) -> None:
        query = await self.query_manager.get_query(self.query_id)
        if query is None:
            raise ValueError(f"Query {self.query_id} not found")
        query.state = QueryState.PROCESSING
        await self.query_manager.persist_query(query)
        await self._run(query)

    async def _run(self, query: Query) -> None:

        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(cast(ColumnElement[bool], User.id == query.user_id))
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Temp hardcoded user profile
        if user and user.details and user.details.zip_code:
            # print(user.details.zip_code)
            async with session_maker() as session:
                latest_weather_query = await session.execute(
                    select(WeatherData)
                    .filter(
                        cast(
                            ColumnElement[bool],
                            WeatherData.zip_code == user.details.zip_code,
                        )
                    )
                    .order_by(WeatherData.timestamp.desc())  # type: ignore
                )
                latest_weather = latest_weather_query.first()

            if latest_weather and latest_weather[0].weather_conditions:
                weather_conditions = json.loads(latest_weather[0].weather_conditions)
                await self._process_query(query, user, weather_conditions)
            else:
                log.warning(
                    f"No weather data available for zip code: {user.details.zip_code}"
                )
                try:
                    await self._process_query(query, user, [])
                except Exception as e:
                    log.error(f"Error processing query: {e}")
                    query.state = QueryState.FAILED
                    await self.query_manager.persist_query(query)
                    raise e

    async def _process_query(
        self, query: Query, user: User, weather_alerts: list[dict[str, Any]]
    ) -> None:
        findings = []
        try:
            if user and user.details and user.details.zip_code:

                user_info = extract_user_info(user)
                print("userifdo: ", user_info)
                gpt_response = await generate_response(
                    query=query.query, alerts=weather_alerts, user_info=user_info
                )
                log.info(f"GPT response processed.\n {gpt_response.model_dump_json()}")

                #  Adding extra checks due to unpredictability of LLM
                if (
                    gpt_response.findings
                    and isinstance(gpt_response.findings, list)
                    and len(gpt_response.findings) > 0
                    and not (
                        len(gpt_response.findings) == 1
                        and gpt_response.findings[0].strip() == ""
                    )
                ):
                    findings = gpt_response.findings
                else:
                    findings = [
                        "I'm sorry, I'm unable to answer your question. Can you please try again?"
                    ]

                query.state = QueryState.COMPLETED
                query.findings = findings
                if gpt_response and gpt_response.source:
                    # TODO: Need to change after adding multiple sources
                    query.sources = [gpt_response.source]
                log.info(query.findings)
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
