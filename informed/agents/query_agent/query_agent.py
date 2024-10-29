from uuid import UUID
from informed.query.manager import QueryManager
from informed.db_models.query import Query, QueryState
from loguru import logger as log
from informed.db import session_maker
from informed.helper.util import extract_user_info
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


class WeatherResponse(BaseModel):
    findings: list[str] = []


def _build_system_prompt() -> str:
    system_prompt = dedent(
        f"""
        You are a highly skilled AI weather advisor with expertise in analyzing weather conditions and providing personalized advice.

        Your role:
        - Analyze current weather conditions and forecasts
        - Provide personalized recommendations based on user health details and preferences
        - Consider air quality, temperature, and other weather factors when giving advice
        - Respond in the user's preferred language when specified

        Guidelines for responses:
        - Be clear, concise, and friendly
        - Prioritize user safety and health considerations
        - Provide specific, actionable advice
        - If weather data is unavailable, acknowledge limitations in your response
        - Format responses as clear, separate findings

        The current date and time is {datetime.now(UTC).isoformat()}
        """
    )
    return system_prompt


async def get_weather_data(
    weather_sources_config: WeatherSourcesConfig, zip_code: str
) -> dict[str, Any]:
    if (
        not weather_sources_config.weatherapi
        or not weather_sources_config.weatherapi.api_key
    ):
        raise ValueError("Weather API key not found")
    weather_api_key = weather_sources_config.weatherapi.api_key
    log.info(f"Fetching weather data for zip code: {zip_code}")
    weather_api_url = f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={zip_code}&days=1&aqi=yes&alerts=yes"
    weather_data = {}
    try:
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
                            "date": raw_weather_data["forecast"]["forecastday"][0][
                                "date"
                            ],
                            "day": raw_weather_data["forecast"]["forecastday"][0][
                                "day"
                            ],
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
                                for hour in raw_weather_data["forecast"]["forecastday"][
                                    0
                                ]["hour"]
                            ],
                        }
                    ]
                },
                "alerts": raw_weather_data.get("alerts", {"alert": []}),
            }
            return weather_data
    except Exception as e:
        log.error(f"Error fetching weather data: {e}")
        return {}


async def build_weather_query_context(
    user: User, weather_sources_config: WeatherSourcesConfig
) -> str:
    if not user.details or not user.details.zip_code:
        raise ValueError("User details or zip code not found")
    weather_data = await get_weather_data(
        weather_sources_config, zip_code=user.details.zip_code
    )
    # TODO: add fallback to get weather from user's location

    context = ""
    if weather_data:
        location = weather_data["location"]
        current = weather_data["current"]
        forecast = weather_data["forecast"]["forecastday"][0]["day"]

        context += f"Location: {location['name']}, {location['region']}, {location['country']}\n"
        context += f"Current Weather: {current['temp_f']}°F (feels like {current['feelslike_f']}°F), {current['condition']['text']}\n"
        context += f"Wind: {current['wind_mph']} mph from {current['wind_dir']}\n"
        context += f"Humidity: {current['humidity']}%, Precipitation: {current['precip_in']} inches\n"
        context += (
            f"Air Quality Index (US EPA): {current['air_quality']['us-epa-index']}\n\n"
        )

        context += f"Today's Forecast:\n"
        context += f"High: {forecast['maxtemp_f']}°F, Low: {forecast['mintemp_f']}°F\n"
        context += f"Condition: {forecast['condition']['text']}\n"
        context += f"Chance of Rain: {forecast['daily_chance_of_rain']}%\n"

        # Add any weather alerts if present
        if weather_data.get("alerts", {}).get("alert"):
            context += "\nWeather Alerts:\n"
            for alert in weather_data["alerts"]["alert"]:
                context += (
                    f"Alert: {alert.get('event', 'N/A')}; {alert.get('desc', 'N/A')}\n"
                )
    return context


class QueryAgent:
    def __init__(
        self,
        query_id: UUID,
        query_manager: QueryManager,
        user_manager: UserManager,
        llm_client: LLMClient,
        weather_sources_config: WeatherSourcesConfig,
    ):
        self.query_id = query_id
        self.query_manager = query_manager
        self.user_manager = user_manager
        self.llm_client = llm_client
        self.weather_sources_config = weather_sources_config

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
            system_prompt = _build_system_prompt()
            user_info = extract_user_info(user)
            context = await build_weather_query_context(
                user, weather_sources_config=self.weather_sources_config
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
