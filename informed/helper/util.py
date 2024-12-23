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
from typing import Any, Optional
from loguru import logger as log
from sqlalchemy import select
from informed.db import session_maker
from informed.db_models.weather_alert import WeatherAlert
from informed.services.weather_alert_service import WeatherAlertService

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
        You are a highly skilled personal assistant that helps answers user questions.
        Your main purpose is to help the user with questions about the weather, air quality, and health,
        but you can also answer other questions as long as they have something to do with the user.

        Your role:
        - Provide personalized responses, using the provided context if available
        - Respond in the user's preferred language when specified


        Guidelines for responses:
        - Be clear, concise, and friendly
        - Prioritize user safety and health considerations
        - If required context is unavailable, acknowledge limitations in your response
        - If context is irrelevant to the user's question, ignore it
        - Pay close attention to any instructions provided
        - ALWAYS use provided tools. You should NEVER respond without using the provided tools.


        Example response:
        User: Is it safe for me to go outside today?
        <Context>
        AQI: 100
        </Context>
        answer: Based on the air quality index, it is probably better to stay indoors today.

        The current date and time is {datetime.now(UTC).isoformat()}
        """
    )
    return system_prompt


async def get_weather_data(
    weather_sources_config: WeatherSourcesConfig, zip_code: str
) -> dict[str, Any]:
    # Check for demo zip code
    if zip_code == "12345":
        return get_mock_weather_data()

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
                "location": raw_weather_data.get("location", ""),
                "current": {
                    "last_updated_epoch": raw_weather_data.get("current", {}).get(
                        "last_updated_epoch"
                    ),
                    "last_updated": raw_weather_data.get("current", {}).get(
                        "last_updated"
                    ),
                    "temp_c": raw_weather_data.get("current", {}).get("temp_c"),
                    "temp_f": raw_weather_data.get("current", {}).get("temp_f"),
                    "is_day": raw_weather_data.get("current", {}).get("is_day"),
                    "condition": raw_weather_data.get("current", {}).get(
                        "condition", {}
                    ),
                    "wind_mph": raw_weather_data.get("current", {}).get("wind_mph"),
                    "wind_degree": raw_weather_data.get("current", {}).get(
                        "wind_degree"
                    ),
                    "wind_dir": raw_weather_data.get("current", {}).get("wind_dir"),
                    "precip_in": raw_weather_data.get("current", {}).get("precip_in"),
                    "humidity": raw_weather_data.get("current", {}).get("humidity"),
                    "cloud": raw_weather_data.get("current", {}).get("cloud"),
                    "feelslike_c": raw_weather_data.get("current", {}).get(
                        "feelslike_c"
                    ),
                    "feelslike_f": raw_weather_data.get("current", {}).get(
                        "feelslike_f"
                    ),
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": forecast_day.get("date"),
                            "day": forecast_day.get("day", {}),
                            "hour": [
                                {
                                    "time": hour.get("time"),
                                    "temp_f": hour.get("temp_f"),
                                    "condition": hour.get("condition", {}),
                                    "wind_mph": hour.get("wind_mph"),
                                    "precip_in": hour.get("precip_in"),
                                    "humidity": hour.get("humidity"),
                                    "feelslike_f": hour.get("feelslike_f"),
                                }
                                for hour in forecast_day.get("hour", [])
                            ],
                        }
                        for forecast_day in raw_weather_data.get("forecast", {}).get(
                            "forecastday", []
                        )
                    ]
                },
                "alerts": raw_weather_data.get("alerts", {"alert": []}),
            }
            return weather_data
    except Exception as e:
        log.error(f"Error fetching weather data: {e}")
        return {}


def get_mock_weather_data() -> dict[str, Any]:
    """Return mock weather data for demo purposes with poor air quality conditions"""
    return {
        "location": {
            "name": "Demo City",
            "region": "Demo Region",
            "country": "Demo Country",
            "lat": 34.0522,
            "lon": -118.2437,
        },
        "current": {
            "last_updated_epoch": int(datetime.now(UTC).timestamp()),
            "last_updated": datetime.now(UTC).isoformat(),
            "temp_c": 28,  # Hot summer day
            "temp_f": 82,
            "is_day": 1,
            "condition": {"text": "Hazy"},  # Changed to reflect poor air quality
            "wind_mph": 3,  # Light wind - contributes to poor air quality
            "wind_degree": 180,
            "wind_dir": "S",
            "precip_in": 0,
            "humidity": 65,  # Higher humidity
            "cloud": 20,
            "feelslike_c": 30,  # Feels hotter due to humidity
            "feelslike_f": 86,
        },
        "forecast": {
            "forecastday": [
                {
                    "date": datetime.now(UTC).date().isoformat(),
                    "day": {
                        "maxtemp_f": 88,
                        "mintemp_f": 75,
                        "condition": {"text": "Hazy sunshine"},
                        "daily_chance_of_rain": 0,  # No rain to clear the air
                    },
                    "hour": [
                        {
                            "time": f"{h:02d}:00",
                            "temp_f": 75
                            + (h if h < 14 else 28 - h),  # Temperature curve
                            "condition": {"text": "Hazy"},
                            "wind_mph": 3
                            + (h if h < 12 else 24 - h) / 4,  # Light wind pattern
                            "precip_in": 0,
                            "humidity": 65 + (h if h < 12 else 24 - h),
                            "feelslike_f": 77 + (h if h < 14 else 28 - h),
                        }
                        for h in range(24)
                    ],
                }
            ]
        },
        "alerts": {
            "alert": [
                {
                    "headline": "Air Quality Alert",
                    "event": "Unhealthy Air Quality",
                    "desc": "The Air Quality Index is forecasted to reach unhealthy levels for sensitive groups. Children, older adults, and people with respiratory conditions should limit outdoor activities.",
                }
            ]
        },
    }


async def get_air_quality_data(
    weather_sources_config: WeatherSourcesConfig,
    latitude: float,
    longitude: float,
    zip_code: str,
) -> Optional[dict[str, Any]]:
    """Fetch air quality data from configured source."""
    # Check for demo zip code
    if zip_code == "12345":
        return get_mock_air_quality_data()

    # Hardcoded to AirNow for now
    source = "airnow"

    if source == "google":
        return await get_google_air_quality_data(
            weather_sources_config, latitude, longitude
        )
    else:
        return await get_airnow_quality_data(weather_sources_config, zip_code)


async def get_google_air_quality_data(
    weather_sources_config: WeatherSourcesConfig,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch air quality data from Google Maps API."""
    if not weather_sources_config.google or not weather_sources_config.google.api_key:
        log.warning("Google API configuration not found")
        raise ValueError("Google API configuration not found")

    url = f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={weather_sources_config.google.api_key}"
    headers = {"Content-Type": "application/json"}

    # Following the example from documentation
    payload = {
        "universalAqi": True,
        "location": {"latitude": latitude, "longitude": longitude},
        "extraComputations": [
            "HEALTH_RECOMMENDATIONS",
            "DOMINANT_POLLUTANT_CONCENTRATION",
            "POLLUTANT_CONCENTRATION",
            "LOCAL_AQI",
            "POLLUTANT_ADDITIONAL_INFO",
        ],
        "languageCode": "en",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                log.error("Unexpected response format from Google Air Quality API")
                raise ValueError(
                    "Unexpected response format from Google Air Quality API"
                )
            return data
    except Exception as e:
        log.error(f"Error fetching air quality data: {str(e)}")
        raise ValueError("Error fetching air quality data")


def build_air_quality_context(
    air_quality_data: Optional[dict[str, Any]], source: str = "airnow"
) -> str:
    """Build context string based on air quality source"""
    if not air_quality_data:
        return ""

    context = "\nDetailed Air Quality Information:\n"

    if source == "google":
        # Add Google-specific context formatting
        context += f"Time: {air_quality_data['dateTime']}\n"
        context += f"Region: {air_quality_data['regionCode']}\n"

        for idx in air_quality_data["indexes"]:
            context += f"AQI ({idx['code']}): {idx['aqi']} - {idx['category']}\n"

        if "pollutants" in air_quality_data:
            context += "\nPollutant Concentrations:\n"
            for pollutant in air_quality_data["pollutants"]:
                context += f"{pollutant['displayName']}: {pollutant['concentration']['value']} {pollutant['concentration']['units']}\n"

        if "healthRecommendations" in air_quality_data:
            context += "\nHealth Recommendations:\n"
            for group, recommendation in air_quality_data[
                "healthRecommendations"
            ].items():
                readable_group = " ".join(
                    word.capitalize() for word in group.split("_")
                )
                context += f"- {readable_group}: {recommendation}\n"
    else:
        # AirNow-specific context formatting
        context += f"Time: {air_quality_data['dateTime']}\n"
        context += f"Region: {air_quality_data['regionCode']}\n"

        # Display PM2.5 AQI and category
        pm25_index = air_quality_data["indexes"][0]  # We know this is PM2.5 now
        context += f"PM2.5 AQI: {pm25_index['aqi']} - {pm25_index['category']}\n"

        if "pollutants" in air_quality_data:
            context += "\nAll Pollutant Readings:\n"
            for pollutant in air_quality_data["pollutants"]:
                context += f"{pollutant['displayName']}: {pollutant['concentration']['value']} {pollutant['concentration']['units']}\n"

    return context


async def build_weather_query_context(
    user: User,
    weather_sources_config: WeatherSourcesConfig,
    weather_alert_service: WeatherAlertService,
) -> str:
    if not user.details or not user.details.zip_code:
        raise ValueError("User details or zip code not found")

    # Get weather data
    weather_data = await get_weather_data(
        weather_sources_config, zip_code=user.details.zip_code
    )

    # Get active weather alerts from Redis
    weather_alerts = await weather_alert_service.get_active_weather_alerts(
        user.details.zip_code
    )

    # Extract coordinates from weather data
    latitude = float(weather_data["location"]["lat"])
    longitude = float(weather_data["location"]["lon"])

    # Get air quality data
    air_quality_data = await get_air_quality_data(
        weather_sources_config,
        latitude=latitude,
        longitude=longitude,
        zip_code=user.details.zip_code,
    )

    context = ""

    if weather_data:
        location = weather_data.get("location", {})
        current = weather_data.get("current", {})
        forecast_days = weather_data.get("forecast", {}).get("forecastday", [])

        if forecast_days:
            forecast = forecast_days[0].get("day", {})

            context += f"Location: {location.get('name', 'Unknown')}, {location.get('region', '')}, {location.get('country', '')}\n"
            context += f"Current Weather: {current.get('temp_f', 'N/A')}°F (feels like {current.get('feelslike_f', 'N/A')}°F), {current.get('condition', {}).get('text', 'N/A')}\n"
            context += f"Wind: {current.get('wind_mph', 'N/A')} mph from {current.get('wind_dir', 'N/A')}\n"
            context += f"Humidity: {current.get('humidity', 'N/A')}%, Precipitation: {current.get('precip_in', 'N/A')} inches\n"

            context += f"Today's Forecast:\n"
            context += f"High: {forecast.get('maxtemp_f', 'N/A')}°F, Low: {forecast.get('mintemp_f', 'N/A')}°F\n"
            context += (
                f"Condition: {forecast.get('condition', {}).get('text', 'N/A')}\n"
            )
            context += (
                f"Chance of Rain: {forecast.get('daily_chance_of_rain', 'N/A')}%\n"
            )

        # Add any weather alerts if present
        alerts = weather_data.get("alerts", {}).get("alert", [])
        if alerts:
            context += "\nWeather Alerts:\n"
            for alert in alerts:
                context += (
                    f"Alert: {alert.get('event', 'N/A')}; {alert.get('desc', 'N/A')}\n"
                )

    # Add air quality context
    context += build_air_quality_context(air_quality_data, source="airnow")

    # Add weather alerts to context if any exist
    if weather_alerts:
        context += "\nActive Weather Alerts:\n"
        for weather_alert in weather_alerts:
            context += f"- {weather_alert['message']} (expires: {weather_alert['expires_at']})\n"

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


async def get_airnow_quality_data(
    weather_sources_config: WeatherSourcesConfig,
    zip_code: str,
) -> Optional[dict[str, Any]]:
    """Fetch current air quality data from AirNow API, focusing on PM2.5."""
    if not weather_sources_config.airnow or not weather_sources_config.airnow.api_key:
        log.warning("AirNow API configuration not found")
        return None

    url = f"https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode={zip_code}&distance=25&API_KEY={weather_sources_config.airnow.api_key}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            # Find PM2.5 reading
            pm25_data = next(
                (item for item in data if item["ParameterName"] == "PM2.5"), None
            )
            if not pm25_data:
                return None

            # Format datetime string
            observation_datetime = f"{pm25_data['DateObserved']} {pm25_data['HourObserved']:02d}:00 {pm25_data['LocalTimeZone']}"

            return {
                "dateTime": observation_datetime,
                "regionCode": f"{pm25_data['StateCode']}-{pm25_data['ReportingArea']}",
                "indexes": [
                    {
                        "code": "PM2.5",
                        "aqi": pm25_data["AQI"],
                        "category": pm25_data["Category"]["Name"],
                    }
                ],
                "pollutants": [
                    {
                        "displayName": item["ParameterName"],
                        "concentration": {"value": item["AQI"], "units": "AQI"},
                    }
                    for item in data
                ],
            }
    except Exception as e:
        log.error(f"Error fetching AirNow air quality data: {str(e)}")
        return None


def get_mock_air_quality_data() -> dict[str, Any]:
    """Return mock air quality data showing poor conditions"""
    return {
        "dateTime": datetime.now(UTC).isoformat(),
        "regionCode": "DEMO-Region",
        "indexes": [{"code": "PM2.5", "aqi": 98, "category": "Bad"}],
        "pollutants": [
            {"displayName": "PM2.5", "concentration": {"value": 158, "units": "AQI"}},
            {
                "displayName": "O3",
                "concentration": {
                    "value": 125,  # Unhealthy for Sensitive Groups (101-150)
                    "units": "AQI",
                },
            },
            {
                "displayName": "PM10",
                "concentration": {"value": 95, "units": "AQI"},  # Moderate (51-100)
            },
        ],
    }
