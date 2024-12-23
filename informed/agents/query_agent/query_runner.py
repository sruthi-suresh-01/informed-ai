import asyncio
from collections.abc import Awaitable, Callable
from typing import NamedTuple
from uuid import UUID

from loguru import logger as log

from informed.agents.query_agent.query_agent import QueryAgent
from informed.db_models.chat import (
    ChatThread,
)
from informed.db_models.query import (
    Query,
)

from informed.llm.client import LLMClient
from informed.config import WeatherSourcesConfig
from informed.services.weather_alert_service import WeatherAlertService
from informed.users.manager import UserManager
from informed.query.manager import QueryManager


class QueryAgentTasks(NamedTuple):
    agent_task: asyncio.Task
    monitor_task: asyncio.Task


class QueryRunner:

    def __init__(
        self,
        query_monitor_timeout: float,
        query_manager: QueryManager,
        user_manager: UserManager,
        llm_client: LLMClient,
        update_callback: Callable[[Query], Awaitable[None]],
        weather_sources_config: WeatherSourcesConfig,
        weather_alert_service: WeatherAlertService,
        monitor_done_callback: (
            Callable[[asyncio.Task, Query], None | Awaitable[None]] | None
        ) = None,
        agent_done_callback: (
            Callable[[asyncio.Task, Query], None | Awaitable[None]] | None
        ) = None,
    ):
        self._query_manager = query_manager
        self._user_manager = user_manager
        self._query_monitor_timeout = query_monitor_timeout
        self._llm_client = llm_client
        self._weather_sources_config = weather_sources_config
        self._weather_alert_service = weather_alert_service
        self._update_callback = update_callback
        self._monitor_done_callback = monitor_done_callback
        self._agent_done_callback = agent_done_callback
        self._all_queries_finished = asyncio.Event()
        self._running_queries: dict[UUID, QueryAgentTasks] = {}

    def _callback_with_query(
        self,
        task: asyncio.Task,
        query_id: UUID,
        callback: Callable[[asyncio.Task, Query], None | Awaitable[None]] | None,
    ) -> None:
        async def exec_callback() -> None:
            try:
                if callback is None:
                    return

                query = await self._query_manager.get_query(query_id)
                if not query:
                    raise ValueError(f"query {query_id} not found")

                if asyncio.iscoroutinefunction(callback):
                    await callback(task, query)
                else:
                    callback(task, query)
            finally:
                self._cleanup_query_if_done_or_failed(query_id)

        loop = asyncio.get_running_loop()
        asyncio.ensure_future(exec_callback(), loop=loop)  # noqa: RUF006

    async def _create_query(self, query_text: str, chat_thread: ChatThread) -> UUID:
        query = await self._query_manager.create_query(
            query=query_text,
            user_id=chat_thread.user_id,
        )
        log.info(
            "created new query",
            query_id=query.query_id,
            chat_thread_id=chat_thread.chat_thread_id,
        )

        return query.query_id

    async def _start_query_agent(
        self, query_id: UUID, instructions: str | None = None
    ) -> None:
        query_agent = QueryAgent(
            query_id=query_id,
            llm_client=self._llm_client,
            query_manager=self._query_manager,
            user_manager=self._user_manager,
            weather_sources_config=self._weather_sources_config,
            weather_alert_service=self._weather_alert_service,
            instructions=instructions,
        )

        try:
            await query_agent.run()
        except (asyncio.CancelledError, Exception) as e:
            log.opt(exception=e).exception("query agent exited with error: {}", str(e))
            raise

    async def _monitor_query_state(
        self, query_id: UUID, update_callback: Callable[[Query], Awaitable[None]]
    ) -> None:
        """
        Monitors the query state through the query manager and update the callback with the updated query.

        Any errors are captured by the asyncio Task and propagated to the caller via done callback.
        """

        # Wait on _query_manager for first iteration to avoid race condition
        query = None
        while not query or (
            not query.state.is_terminated()
            and (tasks := self._running_queries.get(query_id, None))
            and not tasks.monitor_task.done()
        ):
            query = await self._query_manager.get_updated_query(
                query_id, timeout=self._query_monitor_timeout
            )
            log.debug("monitor task got updated query, query state: {}", query.state)
            await update_callback(query)
            if query.state.is_terminated():
                log.info(
                    "exiting query monitor task due to query termination",
                    query_id=query_id,
                )
                break

    def _cleanup_query_if_done_or_failed(self, query_id: UUID) -> None:
        if not (tasks := self._running_queries.get(query_id, None)):
            return

        if (tasks.agent_task.done() and tasks.agent_task.exception()) or (
            tasks.monitor_task.done() and tasks.monitor_task.exception()
        ):
            self.cancel_query(query_id)
        elif tasks.agent_task.done() and tasks.monitor_task.done():
            self._pop_tasks(query_id)

    def _add_tasks(self, query_id: UUID, tasks: QueryAgentTasks) -> None:
        self._running_queries[query_id] = tasks
        self._all_queries_finished.clear()

    def _pop_tasks(self, query_id: UUID) -> QueryAgentTasks | None:
        task = self._running_queries.pop(query_id, None)
        if not self._running_queries:
            self._all_queries_finished.set()
        return task

    def has_running_queries(self) -> bool:
        return len(self._running_queries) > 0

    def is_running(self, query_id: UUID) -> bool:
        tasks = self._running_queries.get(query_id)
        return bool(
            tasks and (not tasks.agent_task.done() or not tasks.monitor_task.done())
        )

    async def wait_on_running_queries(self) -> None:
        await self._all_queries_finished.wait()

    async def launch(
        self,
        query_text: str,
        chat_thread: ChatThread,
        instructions: str | None = None,
    ) -> UUID:
        # trigger the query agent to start
        query_id = await self._create_query(query_text, chat_thread)

        # start the query agent in the background
        agent_task = asyncio.create_task(
            self._start_query_agent(query_id, instructions=instructions)
        )
        agent_task.add_done_callback(
            lambda task: self._callback_with_query(
                task, query_id, self._agent_done_callback
            )
        )

        # start a task to monitor the query agent's progress
        monitor_task = asyncio.create_task(
            self._monitor_query_state(query_id, self._update_callback)
        )
        monitor_task.add_done_callback(
            lambda task: self._callback_with_query(
                task, query_id, self._monitor_done_callback
            )
        )
        self._add_tasks(
            query_id, QueryAgentTasks(agent_task=agent_task, monitor_task=monitor_task)
        )
        return query_id

    def cancel_query(self, query_id: UUID) -> None:
        log.debug("cancelling active query agent")
        if tasks := self._pop_tasks(query_id):
            tasks.agent_task.cancel()
            tasks.monitor_task.cancel()
