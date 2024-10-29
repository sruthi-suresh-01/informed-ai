import ipaddress
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException
from loguru import logger

from informed.db_models.users import User
import os
from textwrap import dedent
from datetime import datetime, UTC
from informed.config import WeatherSourcesConfig
from typing import Any
from loguru import logger as log

APP_ENV = os.getenv("APP_ENV", "DEV")

headers = {"Accept": "application/geo+json", "User-Agent": "informed-app"}


zone_zip_map = {
    "92507": "CAC065",
    "92506": "CAC065",
    "92505": "CAC065",
}


def build_system_prompt() -> str:
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


def extract_user_info(user: User) -> str:
    user_info = ""
    if user and user.details:
        user_info += "User Details:\n"
        preferred_language = user.details.language
        if preferred_language and preferred_language.name:
            user_info += f"Preferred Language: {preferred_language.name}; "
        user_info += f"Age: {user.details.age};"
        if (
            user.medical_details
            and user.medical_details.weather_sensitivities
            and len(user.medical_details.weather_sensitivities) > 0
        ):
            weather_sensitivities = user.medical_details.weather_sensitivities
            user_info += "Weather Sensitivites: "
            for i, weather_sensitivity in enumerate(weather_sensitivities):
                user_info += f"sensitivity_{i+1}: {weather_sensitivity.type}, description: {weather_sensitivity.description}"
            user_info += ";"
        if (
            user.medical_details
            and user.medical_details.health_conditions
            and len(user.medical_details.health_conditions) > 0
        ):
            health_conditions = user.medical_details.health_conditions
            user_info += "Health Conditions: "
            for i, health_condition in enumerate(health_conditions):
                user_info += f"condition_{i+1}: {health_condition.condition},  severity: {health_condition.severity},  description: {health_condition.description}"
            user_info += ";"
    return user_info


async def fetch_alerts(zip: str) -> dict:
    if zip in zone_zip_map:
        zone_id = zone_zip_map[zip]
        url = f"https://api.weather.gov/alerts/active/zone/{zone_id}"
        response = {"status": "", "message": "", "data": {}}

        try:
            if APP_ENV == "DEV" or is_safe_url(url):
                async with httpx.AsyncClient(headers=headers) as client:
                    alert_response = await client.get(url)
                    if alert_response.status_code == 200:
                        data = alert_response.json()
                        if "features" in data:
                            response["data"] = data["features"]
                    else:
                        logger.warning(
                            f"Failed to fetch {url} with status code: {alert_response.status_code}"
                        )
            else:
                raise HTTPException(status_code=403, detail="Foribidden")
        except Exception as e:
            logger.warning(f"Exception occurred when fetching {url}: {e}")
        finally:
            logger.info("HTTP client operation completed.")
            return response
    else:
        return {"status": "error", "message": "Invalid Zip", "data": {}}


def extract_alert_info(alert_features: list[dict]) -> list[dict]:
    # Compile pattern to extract sentences
    allowed_keys = ["event", "headline", "description", "instruction"]
    extracted_features = []
    for feature in alert_features:
        filtered_alert_info = {
            key: feature["properties"][key]
            for key in allowed_keys
            if key in feature["properties"]
        }
        extracted_features.append(filtered_alert_info)
    return extracted_features


# Fetch content from all the document urls
async def fetch_all_docs(documents: list[str]) -> str:
    doc_content = ""
    try:
        for doc_url in documents:
            document_content = await fetch_document(doc_url)
            doc_content += document_content + "\n"
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
    return doc_content


async def fetch_document(url: str) -> str:
    headers = {"Accept": "application/json", "User-Agent": "minute-app"}
    doc_content = ""
    try:
        if APP_ENV == "DEV" or is_safe_url(url):
            async with httpx.AsyncClient(headers=headers) as client:
                response = await client.get(url)
                if response.status_code == 200 and response.headers.get(
                    "Content-Type", ""
                ).startswith("text/plain"):
                    doc_content = response.text
                else:
                    logger.warning(
                        f"Failed to fetch {url} with status code: {response.status_code}"
                    )
        else:
            raise HTTPException(status_code=403, detail="Foribidden")
    except Exception as e:
        logger.warning(f"Exception occurred when fetching {url}: {e}")
    finally:
        logger.info("HTTP client operation completed.")
        return doc_content


def is_safe_url(url: str) -> bool:
    try:
        result = urlparse(url)
        hostname = result.hostname

        if not hostname:
            return False

        # Check if the hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private and loopback addresses
            if ip.is_private or ip.is_loopback:
                return False
        except ValueError:
            # Hostname is not an IP address, check if it's localhost
            if hostname in ["localhost", "127.0.0.1", "::1"]:
                return False

        # Add more conditions to refine what URLs should be considered safe
        return True
    except ValueError:
        return False


"""
# TODO:
Can be adopted to filter dialogues, but would need a model that is fine-tuned
to business domain to extract good results without losing important context
"""
# import spacy
# nlp = spacy.load('en_core_web_sm')

# def extract_relevant_dialogues(doc, keywords, threshold=0.5):
#     # Compile pattern to extract sentences
#     pattern = re.compile(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*\n(.*?): (.*?)(?=\n\d{2}:\d{2}|\Z)', re.DOTALL)

#     matches = pattern.findall(doc)
#     relevant_dialogues = [f"{speaker}: {speech_instance}" for speaker, speech_instance in matches]
#     keyword_doc = nlp(" ".join(keywords))
#     relevant_dialogues = []
#     for speaker, speech_instance in matches:
#         speech_instance_doc = nlp(speech_instance)
#         similarity_score = speech_instance_doc.similarity(keyword_doc)
#         if similarity_score > threshold:
#             relevant_dialogues.append(speaker + ": " + speech_instance)

#     return relevant_dialogues

# # Basic NLP processing to extract keywords from the question
# def extract_keywords(question):
#     doc = nlp(question)
#     keywords = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']]
#     return keywords
