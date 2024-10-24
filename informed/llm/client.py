import json
from typing import Any
import tiktoken
from loguru import logger
from pydantic import BaseModel
from informed.db_models.query import QuerySource
from informed.llm.llm import getLLMResponse
from informed.config import ENV_VARS
from informed.llm.schema import build_function_schema


class GeneratedResponse(BaseModel):
    status: str
    findings: list[str] = []
    source: QuerySource | None = None


MAX_CONTEXT_SIZE = 7000
MAX_RESPONSE_TOKENS = 150
GPT_MODEL_NAME = ENV_VARS["GPT_MODEL_NAME"]


def num_tokens_from_messages(
    messages: list[dict[str, str]], model: str = "gpt-4o-mini-2024-07-18"
) -> int:
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        logger.warning(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        logger.warning(
            "Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18."
        )
        return num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        logger.warning(
            "Warning: gpt-4o and gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-2024-08-06."
        )
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        logger.warning(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}."
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class WeatherResponse(BaseModel):
    findings: list[str] = []


async def generate_response(
    query: str = "",
    weather_data: dict[str, Any] = {},
    user_info: str = "",
) -> GeneratedResponse:

    # Create a comprehensive weather context
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

    messages = [
        {
            "role": "system",
            "content": "You are a highly skilled AI tasked with analyzing Weather alerts and giving users advice based on their health details and preferences. Given a user's question, their details, and weather info, your role involves identifying the most reasonable advice to give them about their query. If no answers are possible for the question-query, simply return empty array of findings'. Example= Query: What's the Weather like? Can I go for a walk? Response: {'findings':['The weather is good','The temperature is 38 C', 'Perfect weather for a walk']}. Try to answer in their preferred language of choice. If not available, English works",
        },
        {
            "role": "user",
            "content": "\nQuestion: " + query + "\nContext: \n" + context + user_info,
        },
    ]

    try:
        num_tokens = num_tokens_from_messages(messages, model=GPT_MODEL_NAME)
        logger.info(f"Number of tokens in LLM prompt: {num_tokens}")
        if (
            num_tokens > MAX_CONTEXT_SIZE - MAX_RESPONSE_TOKENS
        ):  # To control the input text size
            return GeneratedResponse(
                status="done",
                findings=[
                    "Sorry, that's too much text for me to process. Can you reduce the number of attached files and try again?"
                ],
            )

        output_schema = build_function_schema(
            WeatherResponse, description="Answer the user's question about the weather"
        )

        # Remove the loop and asyncio.gather
        function = await getLLMResponse(messages, tools=[output_schema])
        data = json.loads(function.arguments)
        weather_response = WeatherResponse.model_validate(data)
        if isinstance(weather_response, Exception):
            logger.error(f"Error in GPT response: {weather_response}")
            return GeneratedResponse(
                findings=[
                    "Sorry, I'm having some trouble answering your question. Please contact support"
                ],
                status="done",
            )

        if not isinstance(weather_response, WeatherResponse):
            logger.error(
                f"Unexpected response type for GPT response: {type(weather_response)}"
            )
            return GeneratedResponse(
                findings=[
                    "Sorry, I'm having some trouble answering your question. Please contact support"
                ],
                status="done",
            )

        logger.info(f"GPT Response: {weather_response.model_dump_json()}")
        sentences = weather_response.findings

        if len(sentences) > 0:
            response = GeneratedResponse(
                findings=sentences,
                status="success",
                source=QuerySource(source="https://api.weather.gov"),
            )
            return response
        else:
            return GeneratedResponse(
                findings=["Sorry, I can't answer your question"], status="done"
            )

    except Exception as e:
        logger.error(e)
        return GeneratedResponse(
            findings=[
                "Sorry, I'm having some trouble answering your question. Please contact support"
            ],
            status="done",
        )
