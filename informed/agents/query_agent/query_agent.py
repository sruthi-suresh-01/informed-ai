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
import httpx
from informed.config import ENV_VARS


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
        # TODO: throw error if user details are not set
        if user and user.details and user.details.zip_code:
            async with session_maker() as session:
                # TODO: fetch weather data instead of relying on db
                weather_api_key = ENV_VARS["WEATHER_API_KEY"]
                weather_api_url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={user.details.zip_code}&days=1&aqi=yes&alerts=yes"
                async with httpx.AsyncClient() as client:
                    response = await client.get(weather_api_url)
                    raw_weather_data = response.json()

                    # Extract only relevant weather information
                    weather_data = {
                        "location": raw_weather_data["location"],
                        "current": {
                            "last_updated_epoch": raw_weather_data["current"][
                                "last_updated_epoch"
                            ],
                            "last_updated": raw_weather_data["current"]["last_updated"],
                            "temp_c": raw_weather_data["current"]["temp_c"],
                            "temp_f": raw_weather_data["current"]["temp_f"],
                            "is_day": raw_weather_data["current"]["is_day"],
                            "condition": raw_weather_data["current"]["condition"],
                            "wind_mph": raw_weather_data["current"]["wind_mph"],
                            "wind_degree": raw_weather_data["current"]["wind_degree"],
                            "wind_dir": raw_weather_data["current"]["wind_dir"],
                            "precip_in": raw_weather_data["current"]["precip_in"],
                            "humidity": raw_weather_data["current"]["humidity"],
                            "cloud": raw_weather_data["current"]["cloud"],
                            "feelslike_c": raw_weather_data["current"]["feelslike_c"],
                            "feelslike_f": raw_weather_data["current"]["feelslike_f"],
                            "air_quality": raw_weather_data["current"]["air_quality"],
                        },
                        "forecast": {
                            "forecastday": [
                                {
                                    "date": raw_weather_data["forecast"]["forecastday"][
                                        0
                                    ]["date"],
                                    "day": raw_weather_data["forecast"]["forecastday"][
                                        0
                                    ]["day"],
                                    "hour": [
                                        {
                                            "time": hour["time"],
                                            "temp_f": hour["temp_f"],
                                            "condition": hour["condition"],
                                            "wind_mph": hour["wind_mph"],
                                            "precip_in": hour["precip_in"],
                                            "humidity": hour["humidity"],
                                            "feelslike_f": hour["feelslike_f"],
                                            "air_quality": hour["air_quality"],
                                        }
                                        for hour in raw_weather_data["forecast"][
                                            "forecastday"
                                        ][0]["hour"]
                                    ],
                                }
                            ]
                        },
                        "alerts": raw_weather_data.get("alerts", {"alert": []}),
                    }

            if weather_data:
                await self._process_query(query, user, weather_data)
            else:
                log.warning(
                    f"No weather data available for zip code: {user.details.zip_code}"
                )
                try:
                    await self._process_query(query, user, {})
                except Exception as e:
                    log.error(f"Error processing query: {e}")
                    query.state = QueryState.FAILED
                    await self.query_manager.persist_query(query)
                    raise e

    async def _process_query(
        self, query: Query, user: User, weather_data: dict[str, Any]
    ) -> None:
        findings = []
        try:
            if user and user.details and user.details.zip_code:
                user_info = extract_user_info(user)
                gpt_response = await generate_response(
                    query=query.query, weather_data=weather_data, user_info=user_info
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
