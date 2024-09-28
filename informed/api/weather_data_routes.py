from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from informed.api.api_types import WeatherDataCreate, WeatherDataResponse
from informed.db import session_maker
from informed.db_models.weather import WeatherData

weather_router = APIRouter()


@weather_router.post("/add", response_model=WeatherDataResponse)
async def add_weather_data(weather_data: WeatherDataCreate) -> WeatherData:
    current_time = datetime.now()
    new_weather = WeatherData(
        zip_code=weather_data.zip_code,
        date=current_time,
        timestamp=current_time,
        weather_conditions=weather_data.weather_conditions,
    )
    async with session_maker() as session:
        session.add(new_weather)
        await session.commit()
        await session.refresh(new_weather)
    return new_weather


@weather_router.get("/details/{zip_code}", response_model=WeatherDataResponse)
async def get_latest_weather_data(zip_code: str) -> WeatherData:
    async with session_maker() as session:
        query = select(WeatherData).filter(WeatherData.zip_code == zip_code).order_by(WeatherData.timestamp.desc())  # type: ignore
        result = await session.execute(query)
        latest_weather = result.scalar_one_or_none()

    if not latest_weather:
        raise HTTPException(
            status_code=404, detail="Weather data not found for this zip code"
        )
    return latest_weather
