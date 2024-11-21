from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from sqlalchemy import select, ColumnElement
from typing import cast
from informed.db import session_maker
from informed.db_models.notifications import WeatherNotification
from informed.db_models.users import User, AccountType
from informed.helper.utils import get_current_user


admin_router = APIRouter()


class WeatherNotificationCreate(BaseModel):
    zip_code: str
    message: str
    expires_at: datetime


class WeatherNotificationResponse(BaseModel):
    id: UUID
    zip_code: str
    message: str
    created_by: UUID
    created_at: datetime
    expires_at: datetime
    cancelled_at: Optional[datetime] = None
    is_active: bool

    @classmethod
    def from_db(
        cls, notification: WeatherNotification
    ) -> "WeatherNotificationResponse":
        notification_dict = {
            "id": notification.id,
            "zip_code": notification.zip_code,
            "message": notification.message,
            "created_by": notification.created_by,
            "created_at": notification.created_at,
            "expires_at": notification.expires_at,
            "cancelled_at": notification.cancelled_at,
            "is_active": notification.is_active,
        }
        return cls.model_validate(notification_dict)


@admin_router.post("/notifications", response_model=WeatherNotificationResponse)
async def create_notification(
    request: Request,
    notification: WeatherNotificationCreate,
    current_user: User = Depends(get_current_user),
) -> WeatherNotificationResponse:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create notifications",
        )

    async with session_maker() as session:
        db_notification = WeatherNotification(
            zip_code=notification.zip_code,
            message=notification.message,
            created_by=current_user.id,
            created_at=datetime.now(),
            expires_at=notification.expires_at,
            cancelled_at=None,
            is_active=True,
        )
        session.add(db_notification)
        await session.commit()
        await session.refresh(db_notification)

        # Publish to Redis using app manager
        await request.app.state.app_manager.notification_service.publish_notification(
            db_notification
        )

        return WeatherNotificationResponse.from_db(db_notification)


@admin_router.delete("/notifications/{notification_id}")
async def cancel_notification(
    request: Request,
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can cancel notifications",
        )

    async with session_maker() as session:
        notification = await session.get(WeatherNotification, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        notification.cancelled_at = datetime.now()
        notification.is_active = False
        await session.commit()

        # Cancel in Redis using app manager
        await request.app.state.app_manager.notification_service.cancel_notification(
            notification_id, notification.zip_code
        )


@admin_router.get("/notifications", response_model=list[WeatherNotificationResponse])
async def list_notifications(
    zip_code: Optional[str] = Query(None, description="Filter by ZIP code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
) -> list[WeatherNotificationResponse]:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can list notifications",
        )

    async with session_maker() as session:
        query = select(WeatherNotification)

        # Apply filters if provided
        if zip_code is not None:
            query = query.filter(
                cast(ColumnElement[bool], WeatherNotification.zip_code == zip_code)
            )
        if is_active is not None:
            query = query.filter(
                cast(ColumnElement[bool], WeatherNotification.is_active == is_active)
            )

        result = await session.execute(query)
        notifications = result.scalars().all()

        return [WeatherNotificationResponse.from_db(n) for n in notifications]
