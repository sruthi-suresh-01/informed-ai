from datetime import datetime, timezone
import json
from uuid import UUID
from informed.config import Config
from informed.db_models.notifications import WeatherNotification
from informed.db import session_maker
from sqlalchemy import select, ColumnElement
from typing import cast
from redis.asyncio import Redis


class NotificationService:
    def __init__(self, config: Config, redis_client: Redis):
        self.redis_client = redis_client

    async def publish_notification(self, notification: WeatherNotification) -> None:
        """Publishes notification to both Redis and DB"""
        # Store in Redis with expiry
        notification_data = {
            "id": str(notification.id),
            "message": notification.message,
            "created_at": notification.created_at.isoformat(),
            "expires_at": notification.expires_at.isoformat(),
            "created_by": str(notification.created_by),
            "is_active": notification.is_active,
        }

        # Calculate TTL in seconds - ensure both datetimes are timezone-aware
        current_time = datetime.now(timezone.utc)
        ttl = int((notification.expires_at - current_time).total_seconds())
        if ttl > 0:
            # Store in sorted set for efficient retrieval
            await self.redis_client.zadd(
                f"notifications:zip:{notification.zip_code}",
                {json.dumps(notification_data): notification.expires_at.timestamp()},
            )
            # Set expiry on the sorted set
            await self.redis_client.expire(
                f"notifications:zip:{notification.zip_code}", ttl
            )

    async def get_active_notifications(self, zip_code: str) -> list[dict]:
        """Gets active notifications from Redis"""
        try:
            # Get all notifications from the sorted set
            notifications = await self.redis_client.zrange(
                f"notifications:zip:{zip_code}", 0, -1
            )
            # Filter for active notifications
            return [json.loads(n) for n in notifications if json.loads(n)["is_active"]]
        except Exception:
            # Fallback to DB if Redis fails
            return await self._get_active_notifications_from_db(zip_code)

    async def _get_active_notifications_from_db(self, zip_code: str) -> list[dict]:
        """Fallback method to get notifications from DB"""
        async with session_maker() as session:
            query = select(WeatherNotification).filter(
                cast(ColumnElement[bool], WeatherNotification.zip_code == zip_code),
                cast(ColumnElement[bool], WeatherNotification.is_active == True),
                cast(ColumnElement[bool], WeatherNotification.cancelled_at == None),
            )
            result = await session.execute(query)
            notifications = result.scalars().all()
            return [
                {
                    "id": str(n.id),
                    "message": n.message,
                    "created_at": n.created_at.isoformat(),
                    "expires_at": n.expires_at.isoformat(),
                    "created_by": str(n.created_by),
                    "is_active": n.is_active,
                }
                for n in notifications
            ]

    async def cancel_notification(self, notification_id: UUID, zip_code: str) -> None:
        """Cancels notification in both Redis and DB"""
        # Remove from Redis
        notifications = await self.redis_client.zrange(
            f"notifications:zip:{zip_code}", 0, -1
        )
        for n in notifications:
            n_data = json.loads(n)
            if n_data["id"] == str(notification_id):
                await self.redis_client.zrem(f"notifications:zip:{zip_code}", n)
                break
