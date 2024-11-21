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
from typing import cast, Any
from informed.db_models.users import User
from fastapi import HTTPException, status
from informed.users.manager import UserManager


class InformedManager:
    def __init__(self, config: Config, llm_client: LLMClient):
        self.config = config
        self.query_manager = QueryManager()
        self.user_manager = UserManager(config)
        self.llm_client = llm_client
        self._lock_var: ContextVar[asyncio.Lock] = ContextVar("lock_var")
        self._query_tasks: dict[UUID, asyncio.Task] = {}
        self._user_tasks: dict[UUID, asyncio.Task] = {}

    def _get_lock(self) -> asyncio.Lock:
        lock = self._lock_var.get(None)
        if lock is None:
            lock = asyncio.Lock()
            self._lock_var.set(lock)
        return lock

    async def cancel_all_tasks(self) -> None:
        async with self._get_lock():
            for task in self._query_tasks.values():
                task.cancel()
            for task in self._user_tasks.values():
                task.cancel()

    async def cancel_user_tasks(self, user_id: UUID) -> None:
        async with self._get_lock():
            task = self._user_tasks.get(user_id)
            if task:
                task.cancel()
                del self._user_tasks[user_id]

    async def create_query(self, user_id: UUID, query: str) -> QueryResponse:
        created_query = await self.query_manager.create_query(user_id, query)
        log.info(f"Created query {created_query.query_id} for user {user_id}")
        return created_query

    async def get_query(self, query_id: UUID) -> Query:
        query = await self.query_manager.get_query(query_id)
        if query is None:
            raise ValueError(f"Query {query_id} not found")
        log.info(f"Got query {query.query_id} for user {query.user_id}")
        return query

    async def update_query(self, query: Query) -> QueryResponse:
        request = UpdateQueryRequest(query_id=query.query_id, state=query.state)
        updated_query = await self.query_manager.update_query(request)
        log.info(f"Updated query {query.query_id} for user {query.user_id}")
        return updated_query

    async def start_query(self, query_id: UUID) -> QueryResponse:
        query = await self.query_manager.get_query(query_id)
        if query is None:
            raise ValueError(f"Query {query_id} not found")
        if query.state not in [QueryState.PENDING, QueryState.CREATED]:
            raise ValueError(f"Query {query_id} is not in pending state")

        return await self._start_query(query)

    async def _start_query(self, query: Query) -> QueryResponse:
        initial_query_state = query.state
        query_id = query.query_id
        timeout = 10  # TODO: Make this configurable

        # Cancel all tasks for the user since we only process last query
        await self.cancel_user_tasks(query.user_id)

        async with self._get_lock():
            task = asyncio.create_task(self._run_query_agent(query))
            # self._query_tasks[query_id] = task
            self._user_tasks[query.user_id] = task
        try:
            await asyncio.wait_for(
                self._wait_for_query_start(query_id, initial_query_state), timeout
            )
        except TimeoutError:
            task.cancel()
            raise TimeoutError(
                f"Query {query_id} did not start within {timeout} seconds"
            ) from None

        started_query = await self.query_manager.get_query(query_id)
        if started_query is None:
            raise ValueError(f"Query {query_id} not found after starting")
        return QueryResponse.from_db(started_query)

    async def _run_query_agent(self, query: Query) -> asyncio.Task:
        query_agent = QueryAgent(
            query_id=query.query_id,
            query_manager=self.query_manager,
            user_manager=self.user_manager,
            llm_client=self.llm_client,
            weather_sources_config=self.config.weather_sources_config,
        )
        query_task = asyncio.create_task(query_agent.run())
        # self._query_tasks[query_id] = query_task
        self._user_tasks[query.user_id] = query_task
        return query_task

    async def _wait_for_query_start(
        self, query_id: UUID, initial_state: QueryState
    ) -> None:
        while True:
            query = await self.query_manager.get_query(query_id)
            if query is None:
                raise ValueError(f"Query {query_id} not found")
            if query.state != initial_state:
                return
            await asyncio.sleep(0.5)

    async def get_recent_query_for_user(self, user_id: UUID) -> QueryResponse | None:
        query = await self.query_manager.get_recent_query_for_user(user_id)
        if query is None:
            return None
        return QueryResponse.from_db(query)

    async def get_user(self, user_id: UUID) -> User:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(cast(ColumnElement[bool], User.id == user_id))
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
