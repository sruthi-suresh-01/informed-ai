from datetime import datetime, timezone
import json
from uuid import UUID
from informed.config import Config
from informed.db_models.weather_alert import WeatherAlert
from informed.db import session_maker
from sqlalchemy import select, ColumnElement
from typing import cast
from redis.asyncio import Redis


class WeatherAlertService:
    def __init__(self, config: Config, redis_client: Redis):
        self.redis_client = redis_client

    async def publish_weather_alert(self, weather_alert: WeatherAlert) -> None:
        """Publishes weather_alert to both Redis and DB"""
        # Store in Redis with expiry
        weather_alert_data = {
            "id": str(weather_alert.weather_alert_id),
            "message": weather_alert.message,
            "created_at": weather_alert.created_at.isoformat(),
            "expires_at": weather_alert.expires_at.isoformat(),
            "created_by": str(weather_alert.created_by),
            "is_active": weather_alert.is_active,
        }

        # Calculate TTL in seconds - ensure both datetimes are timezone-aware
        current_time = datetime.now(timezone.utc)
        ttl = int((weather_alert.expires_at - current_time).total_seconds())
        if ttl > 0:
            # Store in sorted set for efficient retrieval
            await self.redis_client.zadd(
                f"weather_alert:zip:{weather_alert.zip_code}",
                {json.dumps(weather_alert_data): weather_alert.expires_at.timestamp()},
            )
            # Set expiry on the sorted set
            await self.redis_client.expire(
                f"weather_alert:zip:{weather_alert.zip_code}", ttl
            )

    async def get_active_weather_alerts(self, zip_code: str) -> list[dict]:
        """Gets active weather_alerts from Redis"""
        try:
            # Get all weather_alerts from the sorted set
            weather_alerts = await self.redis_client.zrange(
                f"weather_alert:zip:{zip_code}", 0, -1
            )
            # Filter for active weather_alerts
            return [json.loads(n) for n in weather_alerts if json.loads(n)["is_active"]]
        except Exception:
            # Fallback to DB if Redis fails
            return await self._get_active_weather_alerts_from_db(zip_code)

    async def _get_active_weather_alerts_from_db(self, zip_code: str) -> list[dict]:
        """Fallback method to get weather_alerts from DB"""
        async with session_maker() as session:
            query = select(WeatherAlert).filter(
                cast(ColumnElement[bool], WeatherAlert.zip_code == zip_code),
                cast(ColumnElement[bool], WeatherAlert.is_active == True),
                cast(ColumnElement[bool], WeatherAlert.cancelled_at == None),
            )
            result = await session.execute(query)
            weather_alerts = result.scalars().all()
            return [
                {
                    "id": str(n.weather_alert_id),
                    "message": n.message,
                    "created_at": n.created_at.isoformat(),
                    "expires_at": n.expires_at.isoformat(),
                    "created_by": str(n.created_by),
                    "is_active": n.is_active,
                }
                for n in weather_alerts
            ]

    async def cancel_weather_alert(self, weather_alert_id: UUID, zip_code: str) -> None:
        """Cancels weather_alert in both Redis and DB"""
        # Remove from Redis
        weather_alerts = await self.redis_client.zrange(
            f"weather_alert:zip:{zip_code}", 0, -1
        )
        for n in weather_alerts:
            n_data = json.loads(n)
            if n_data["id"] == str(weather_alert_id):
                await self.redis_client.zrem(f"weather_alert:zip:{zip_code}", n)
                break
