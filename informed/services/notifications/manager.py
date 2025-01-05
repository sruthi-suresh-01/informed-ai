from typing import cast
from uuid import UUID
from sqlalchemy import ColumnElement, select, update
from informed.db import session_maker
from informed.db_models.users import User, Settings
from informed.db_models.notification import Notification, NotificationStatus
from informed.db_models.chat import AssistantMessage
from informed.db_models.query import QueryState


class NotificationsManager:
    async def get_users_with_daily_updates(self) -> list[tuple[UUID, str]]:
        """Get all users who have opted in for daily updates and their prompts."""
        async with session_maker() as session:
            #  Added the ignore because we are using JSONBFromPydantic to store configurations. It is stored as a JSONB but we are accessing it as a pydantic model which confuses mypy.
            stmt = (
                select(User, Settings)
                .join(Settings)
                .filter(
                    cast(
                        ColumnElement[bool],
                        Settings.configurations["daily_updates"].as_boolean(),  # type: ignore
                    )
                )
            )
            result = await session.execute(stmt)
            users_and_settings = result.unique().all()

            return [
                (user.user_id, settings.configurations.daily_update_prompt)
                for user, settings in users_and_settings
                if settings.configurations.daily_update_prompt
            ]

    async def get_notifications_for_user(
        self, user_id: UUID, limit: int = 10
    ) -> list[Notification]:
        async with session_maker() as session:
            result = await session.execute(
                select(Notification)
                .filter(
                    cast(
                        ColumnElement[bool],
                        Notification.user_id == user_id
                        and Notification.status
                        not in [
                            NotificationStatus.FAILED,
                            NotificationStatus.PROCESSING,
                        ],
                    )
                )
                .order_by(Notification.created_at.desc())  # type: ignore
                .limit(limit)
            )
            return list(result.scalars().all())

    async def mark_notifications_as_read(self, user_id: UUID) -> None:
        async with session_maker() as session:
            await session.execute(
                update(Notification).where(
                    cast(
                        ColumnElement[bool],
                        Notification.user_id == user_id
                        and Notification.status == NotificationStatus.READY,
                    )
                )
            )

    async def create_notification(
        self, user_id: UUID, chat_thread_id: UUID, title: str, content: str
    ) -> None:
        async with session_maker() as session:
            notification = Notification(
                user_id=user_id,
                chat_thread_id=chat_thread_id,
                status=NotificationStatus.PROCESSING,
                title=title,
                content=content,
            )
            session.add(notification)
            await session.commit()

    async def update_notification_status(
        self, notification_id: UUID, status: NotificationStatus
    ) -> None:
        async with session_maker() as session:
            await session.execute(
                update(Notification)
                .where(
                    cast(
                        ColumnElement[bool],
                        Notification.notification_id == notification_id,
                    )
                )
                .values(status=status)
            )
            await session.commit()

    async def bulk_update_notification_status(
        self, notification_ids: list[UUID], status: NotificationStatus
    ) -> None:
        async with session_maker() as session:
            await session.execute(
                update(Notification)
                .where(
                    cast(
                        ColumnElement[bool],
                        Notification.notification_id in notification_ids,
                    )
                )
                .values(status=status)
            )
            await session.commit()

    async def update_notification_from_chat_thread(
        self,
        chat_thread_id: UUID,
        message: AssistantMessage,
        query_state: QueryState,
    ) -> None:
        async with session_maker() as session:
            result = await session.execute(
                select(Notification).filter(
                    cast(
                        ColumnElement[bool],
                        Notification.chat_thread_id == chat_thread_id,
                    )
                )
            )
            notification = result.scalar_one_or_none()

            if notification:
                if query_state == QueryState.COMPLETED:
                    notification.status = NotificationStatus.READY
                    notification.content = message.content
                    notification.title = "Daily Update"
                elif query_state.is_failed():
                    notification.status = NotificationStatus.FAILED

                await session.commit()
