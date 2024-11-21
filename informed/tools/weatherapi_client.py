from informed.config import WeatherSourcesConfig
from typing import Any
from loguru import logger as log
import httpx


class WeatherApiClient:
    def __init__(self, config: WeatherSourcesConfig):
        if not config.weatherapi or not config.weatherapi.api_key:
            raise ValueError("WeatherAPI API key is not set")
        self.config = config.weatherapi
        self.endpoints = {
            "current": "https://api.weatherapi.com/v1/current.json",
            "forecast": "https://api.weatherapi.com/v1/forecast.json",
        }

    async def get_current_weather(self, location: str) -> Any:
        pass

    async def get_forecast(self, query: str, days: int = 1) -> Any:
        """
        Get a forecast for a given location.

        Args:
            query: str: The location query - can be US Zipcode, UK Postcode, Canada Postalcode, IP address,
                  Latitude/Longitude (decimal degree) or city name.
            days: int: The number of days to get the forecast for. Defaults to 1.
        """

        # TODO: Use another API for AQI. This one seems to give incorrect data
        url = f"{self.endpoints['forecast']}?key={self.config.api_key}&q={query}&days={days}&aqi=yes&alerts=yes"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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
                                    for hour in raw_weather_data["forecast"][
                                        "forecastday"
                                    ][0]["hour"]
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
