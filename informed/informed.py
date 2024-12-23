from informed.query.manager import QueryManager, UpdateQueryRequest
from informed.config import Config
from informed.db_models.query import Query, QueryState
from informed.api.schema import QueryResponse
from informed.agents.query_agent.query_agent import QueryAgent
from uuid import UUID
from loguru import logger as log
import asyncio
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
from informed.db_models.chat import ChatThread, Message


class InformedManager:
    def __init__(self, config: Config, llm_client: LLMClient, redis_client: Redis):
        self.config = config
        self.user_manager = UserManager(config)
        self.llm_client = llm_client
        self.weather_alert_service = WeatherAlertService(config, redis_client)
        self.query_manager = QueryManager()
        self.chat_manager = DBChatManager()
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

    # async def cancel_all_tasks(self) -> None:
    #     async with self._get_lock():
    #         for task in self._query_tasks.values():
    #             task.cancel()
    #         for task in self._user_tasks.values():
    #             task.cancel()

    # async def cancel_user_tasks(self, user_id: UUID) -> None:
    #     async with self._get_lock():
    #         task = self._user_tasks.get(user_id)
    #         if task:
    #             task.cancel()
    #             del self._user_tasks[user_id]

    # async def create_query(self, user_id: UUID, query: str) -> QueryResponse:
    #     created_query = await self.query_manager.create_query(user_id, query)
    #     log.info(f"Created query {created_query.query_id} for user {user_id}")
    #     return created_query

    # async def get_query(self, query_id: UUID) -> Query:
    #     query = await self.query_manager.get_query(query_id)
    #     if query is None:
    #         raise ValueError(f"Query {query_id} not found")
    #     log.info(f"Got query {query.query_id} for user {query.user_id}")
    #     return query

    # async def update_query(self, query: Query) -> QueryResponse:
    #     request = UpdateQueryRequest(query_id=query.query_id, state=query.state)
    #     updated_query = await self.query_manager.update_query(request)
    #     log.info(f"Updated query {query.query_id} for user {query.user_id}")
    #     return updated_query

    # async def start_query(self, query_id: UUID) -> QueryResponse:
    #     query = await self.query_manager.get_query(query_id)
    #     if query is None:
    #         raise ValueError(f"Query {query_id} not found")
    #     if query.state not in [QueryState.PENDING, QueryState.CREATED]:
    #         raise ValueError(f"Query {query_id} is not in pending state")

    #     return await self._start_query(query)

    # async def _start_query(self, query: Query) -> QueryResponse:
    #     initial_query_state = query.state
    #     query_id = query.query_id
    #     timeout = 20  # TODO: Make this configurable

    #     # Cancel all tasks for the user since we only process last query
    #     await self.cancel_user_tasks(query.user_id)

    #     async with self._get_lock():
    #         task = asyncio.create_task(self._run_query_agent(query))
    #         # self._query_tasks[query_id] = task
    #         self._user_tasks[query.user_id] = task
    #     try:
    #         await asyncio.wait_for(
    #             self._wait_for_query_start(query_id, initial_query_state), timeout
    #         )
    #     except TimeoutError:
    #         task.cancel()
    #         raise TimeoutError(
    #             f"Query {query_id} did not start within {timeout} seconds"
    #         ) from None

    #     started_query = await self.query_manager.get_query(query_id)
    #     if started_query is None:
    #         raise ValueError(f"Query {query_id} not found after starting")
    #     return QueryResponse.from_db(started_query)

    # async def _run_query_agent(self, query: Query) -> asyncio.Task:
    #     query_agent = QueryAgent(
    #         query_id=query.query_id,
    #         query_manager=self.query_manager,
    #         user_manager=self.user_manager,
    #         llm_client=self.llm_client,
    #         weather_sources_config=self.config.weather_sources_config,
    #         weather_alert_service=self.weather_alert_service,
    #     )
    #     query_task = asyncio.create_task(query_agent.run())
    #     # self._query_tasks[query_id] = query_task
    #     self._user_tasks[query.user_id] = query_task
    #     return query_task

    # async def _wait_for_query_start(
    #     self, query_id: UUID, initial_state: QueryState
    # ) -> None:
    #     while True:
    #         query = await self.query_manager.get_query(query_id)
    #         if query is None:
    #             raise ValueError(f"Query {query_id} not found")
    #         if query.state != initial_state:
    #             return
    #         await asyncio.sleep(0.5)

    # async def get_recent_query_for_user(self, user_id: UUID) -> QueryResponse | None:
    #     query = await self.query_manager.get_recent_query_for_user(user_id)
    #     if query is None:
    #         return None
    #     return QueryResponse.from_db(query)

    # async def get_query(self, query_id: UUID) -> QueryResponse | None:
    #     query = await self.query_manager.get_query(query_id)
    #     if query is None:
    #         return None
    #     return QueryResponse.from_db(query)

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
        self, chat_request: ChatRequest, user_id: UUID
    ) -> ChatThread:
        chat_thread = await self.chat_manager.create_chat_thread(chat_request, user_id)
        await self.start_chat_agent(chat_thread.chat_thread_id)
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

    async def start_chat_agent(self, chat_thread_id: UUID) -> None:
        chat_thread = await self.chat_manager.get_chat_thread(chat_thread_id)
        if chat_thread is None:
            raise Exception(f"Chat thread {chat_thread_id} not found")
        await self._ensure_running_chat_agent(chat_thread_id)

    async def _ensure_running_chat_agent(
        self,
        chat_thread_id: UUID,
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
