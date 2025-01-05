from informed.query.manager import QueryManager, UpdateQueryRequest
from informed.config import Config
from informed.db_models.query import Query, QueryState
from informed.api.schema import QueryResponse
from informed.agents.query_agent.query_agent import QueryAgent
from uuid import UUID
from loguru import logger as log
import asyncio
from typing import Callable, Awaitable

from contextvars import ContextVar
from informed.llm.client import LLMClient
from informed.db import session_maker
from sqlalchemy.sql import select, ColumnElement
from typing import cast
from informed.db_models.users import User
from fastapi import HTTPException, status
from informed.users.manager import UserManager
from informed.services.weather_alert_service import WeatherAlertService
from redis.asyncio import Redis
from informed.chat.manager import DBChatManager
from informed.agents.chat_agent.chat_agent import ChatAgent
from informed.api.schema import ChatRequest, AddUserMessageRequest
from informed.db_models.chat import ChatThread, Message, AssistantMessage
from informed.services.notifications.manager import NotificationsManager
from informed.db_models.notification import Notification, NotificationStatus


class InformedManager:
    def __init__(self, config: Config, llm_client: LLMClient, redis_client: Redis):
        self.config = config
        self.user_manager = UserManager(config)
        self.llm_client = llm_client
        self.weather_alert_service = WeatherAlertService(config, redis_client)
        self.query_manager = QueryManager()
        self.chat_manager = DBChatManager()
        self.notifications_manager = NotificationsManager()
        self._lock_var: ContextVar[asyncio.Lock] = ContextVar("lock_var")
        self._query_tasks: dict[UUID, asyncio.Task] = {}
        self._user_tasks: dict[UUID, asyncio.Task] = {}

        self._chat_agents: dict[UUID, ChatAgent] = {}

    def _get_lock(self) -> asyncio.Lock:
        lock = self._lock_var.get(None)
        if lock is None:
            lock = asyncio.Lock()
            self._lock_var.set(lock)
        return lock

    async def get_user(self, user_id: UUID) -> User:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(cast(ColumnElement[bool], User.user_id == user_id))
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def cancel_all_tasks(self) -> None:
        async with self._get_lock():
            for chat_thread_id in list(self._chat_agents.keys()):
                chat_agent = self._chat_agents[chat_thread_id]
                await chat_agent.stop()
                del self._chat_agents[chat_thread_id]

    async def start_new_chat_thread(
        self,
        chat_request: ChatRequest,
        user_id: UUID,
        assistant_message_callback: (
            Callable[[UUID, AssistantMessage, QueryState], Awaitable[None]] | None
        ) = None,
    ) -> ChatThread:
        chat_thread = await self.chat_manager.create_chat_thread(chat_request, user_id)
        await self.start_chat_agent(
            chat_thread.chat_thread_id, assistant_message_callback
        )
        return chat_thread

    async def add_user_message(
        self,
        add_user_message_request: AddUserMessageRequest,
        user_id: UUID,
    ) -> UUID:
        message_id = await self.chat_manager.add_user_message(
            add_user_message_request, user_id
        )

        return message_id

    async def start_chat_agent(
        self,
        chat_thread_id: UUID,
        assistant_message_callback: (
            Callable[[UUID, AssistantMessage, QueryState], Awaitable[None]] | None
        ) = None,
    ) -> None:
        chat_thread = await self.chat_manager.get_chat_thread(chat_thread_id)
        if chat_thread is None:
            raise Exception(f"Chat thread {chat_thread_id} not found")
        await self._ensure_running_chat_agent(
            chat_thread_id, assistant_message_callback
        )

    async def _ensure_running_chat_agent(
        self,
        chat_thread_id: UUID,
        assistant_message_callback: (
            Callable[[UUID, AssistantMessage, QueryState], Awaitable[None]] | None
        ) = None,
    ) -> None:
        chat_agent = self._chat_agents.get(chat_thread_id, None)
        if chat_agent and chat_agent.is_running():
            return

        async def termination_callback() -> None:
            if chat_thread_id in self._chat_agents:
                del self._chat_agents[chat_thread_id]

        chat_agent = ChatAgent(
            chat_thread_id=chat_thread_id,
            query_manager=self.query_manager,
            user_manager=self.user_manager,
            chat_manager=self.chat_manager,
            llm_client=self.llm_client,
            weather_sources_config=self.config.weather_sources_config,
            weather_alert_service=self.weather_alert_service,
            chat_termination_callback=termination_callback,
            assistant_message_callback=assistant_message_callback,
        )
        self._chat_agents[chat_thread_id] = chat_agent

        await chat_agent.start()

    async def wait_for_chat_agent_to_terminate(
        self, chat_thread_id: UUID, timeout: float
    ) -> None:
        if chat_thread_id not in self._chat_agents:
            raise ValueError(f"Chat agent for chat thread {chat_thread_id} not found")
        chat_agent = self._chat_agents[chat_thread_id]
        await asyncio.wait_for(chat_agent.wait_for_termination_event(), timeout)

    async def get_chat(self, chat_thread_id: UUID) -> ChatThread:
        chat_thread = await self.chat_manager.get_chat_thread(chat_thread_id)
        if chat_thread is None:
            raise ValueError(f"Chat thread {chat_thread_id} not found")
        return chat_thread

    async def get_chat_messages(self, chat_thread_id: UUID) -> list[Message]:
        chat_thread = await self.chat_manager.get_chat_thread(chat_thread_id)
        if chat_thread is None:
            raise ValueError(f"Chat thread {chat_thread_id} not found")
        return [m for m in chat_thread.messages]

    async def get_all_chats(self, review_stage: str | None = None) -> list[ChatThread]:
        chat_threads = await self.chat_manager.get_all_chat_threads()
        return chat_threads

    async def get_message(self, message_id: UUID) -> Message:
        message = await self.chat_manager.get_message(message_id)
        if message is None:
            raise ValueError(f"Message {message_id} not found")
        return message

    async def get_notifications_for_user(
        self, user_id: UUID, limit: int = 10
    ) -> list[Notification]:
        return await self.notifications_manager.get_notifications_for_user(
            user_id, limit
        )

    async def bulk_update_notification_status(
        self, notification_ids: list[UUID], status: NotificationStatus
    ) -> None:
        return await self.notifications_manager.bulk_update_notification_status(
            notification_ids, status
        )

    async def send_daily_updates(self) -> None:
        """Send daily updates to all opted-in users."""

        async def notification_callback(
            chat_thread_id: UUID, message: AssistantMessage, query_state: QueryState
        ) -> None:
            await self.notifications_manager.update_notification_from_chat_thread(
                chat_thread_id, message, query_state
            )

        try:
            users = await self.notifications_manager.get_users_with_daily_updates()
            log.info(f"Sending daily updates to {len(users)} users")

            for user_id, prompt in users:
                try:
                    chat_request = ChatRequest(message=prompt)
                    chat_thread = await self.start_new_chat_thread(
                        chat_request=chat_request,
                        user_id=user_id,
                        assistant_message_callback=notification_callback,
                    )

                    await self.notifications_manager.create_notification(
                        user_id=user_id,
                        chat_thread_id=chat_thread.chat_thread_id,
                        title="Daily Update",
                        content="Processing your daily update...",
                    )

                    log.info(f"Created daily update chat thread for user {user_id}")
                except Exception as e:
                    log.error(
                        f"Failed to send daily update to user {user_id}: {str(e)}"
                    )
                    continue

        except Exception as e:
            log.error(f"Failed to process daily updates: {str(e)}")
