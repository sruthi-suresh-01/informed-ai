from typing import cast

from fastapi import APIRouter, Request

from informed.api.schema import (
    BulkUpdateNotificationStatusRequest,
    NotificationListResponse,
)
from informed.helper.utils import UserDep
from informed.informed import InformedManager

router = APIRouter()


@router.get("/")
async def get_notifications(
    request: Request, user: UserDep
) -> NotificationListResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    notifications = await app_manager.get_notifications_for_user(user.user_id)
    return NotificationListResponse.from_user_notifications(notifications)


@router.put("/")
async def mark_notifications_as_read(
    notification_request: BulkUpdateNotificationStatusRequest,
    request: Request,
    user: UserDep,
) -> NotificationListResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    await app_manager.bulk_update_notification_status(
        notification_request.notification_ids, notification_request.status
    )
    notifications = await app_manager.get_notifications_for_user(user.user_id)
    return NotificationListResponse.from_user_notifications(notifications)
