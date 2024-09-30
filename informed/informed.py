from informed.query.manager import QueryManager, UpdateQueryRequest
from informed.config import Config
from informed.db_models.query import Query, QueryState
from informed.api.api_types import QueryResponse
from informed.agents.query_agent.query_agent import QueryAgent
from uuid import UUID
from loguru import logger as log
import asyncio
from contextvars import ContextVar


class InformedManager:
    def __init__(self, config: Config):
        self.config = config
        self.query_manager = QueryManager()
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
        timeout = 10

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
            query.query_id,
            self.query_manager,
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
