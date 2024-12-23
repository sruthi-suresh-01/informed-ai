import asyncio
import contextlib
from typing import Callable, Awaitable
from uuid import UUID

from loguru import logger as log
from informed.db_models.query import Query
from informed.query.manager import QueryManager
from informed.chat.manager import ChatManager
from informed.db_models.chat import (
    ChatThread,
    Message,
    UserMessage,
    AssistantMessage,
    MessageSource,
)
from informed.llm.client import LLMClient
from informed.config import WeatherSourcesConfig
from informed.services.weather_alert_service import WeatherAlertService
from informed.users.manager import UserManager
from informed.agents.query_agent.query_runner import QueryRunner
from informed.db_models.chat import MessageResponseType
from informed.db_models.users import Language


class ChatAgent:
    def __init__(
        self,
        chat_thread_id: UUID,
        query_manager: QueryManager,
        user_manager: UserManager,
        chat_manager: ChatManager,
        llm_client: LLMClient,
        weather_sources_config: WeatherSourcesConfig,
        weather_alert_service: WeatherAlertService,
        chat_termination_callback: Callable[[], Awaitable[None]],
    ):
        self.chat_thread_id = chat_thread_id

        self.query_manager = query_manager
        self.user_manager = user_manager
        self.chat_manager = chat_manager
        self.llm_client = llm_client
        self.weather_sources_config = weather_sources_config
        self.weather_alert_service = weather_alert_service
        self._chat_termination_callback = chat_termination_callback

        # only one query agent will be running at a time
        self._query_runner: QueryRunner = QueryRunner(
            query_monitor_timeout=120.0,
            user_manager=self.user_manager,
            query_manager=self.query_manager,
            llm_client=self.llm_client,
            update_callback=self._process_query_state_change,
            agent_done_callback=self._query_done_callback,
            weather_sources_config=self.weather_sources_config,
            weather_alert_service=self.weather_alert_service,
        )

        self._run_task: asyncio.Task | None = None
        self._termination_event: asyncio.Event = asyncio.Event()

    async def start(self, timeout: float = 120.0) -> None:
        if not self._run_task:
            self._run_task = asyncio.create_task(self._run())
            log.info("chat agent started")
            # try:
            #     await asyncio.wait_for(self._wait_for_acknowledge_event(), timeout)
            # except TimeoutError:
            #     log.debug("chat agent timed out waiting for acknowledge event")
            #     await self.stop()

    # async def _wait_for_acknowledge_event(self) -> None:
    #     await self._acknowledge_event.wait()
    #     self._acknowledge_event.clear()

    async def wait_for_termination_event(self) -> None:
        await self._termination_event.wait()
        self._termination_event.clear()
        log.info("chat agent terminated")

    async def stop(self) -> None:
        if self._run_task:
            self._run_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                if not self._run_task.done():
                    await self._run_task
            self._run_task = None
            log.info("chat agent stopped")

    async def _run(self, message_interval_timeout_seconds: float = 1200.0) -> None:
        try:
            while True:
                pending_messages = await self._pending_messages()
                log.info(
                    "chat agent run loop, pending messages: {}",
                    len(pending_messages),
                )
                if pending_messages:
                    await self._handle_pending_messages(pending_messages)
                else:
                    await self._wait_for_new_message(message_interval_timeout_seconds)
        except TimeoutError:
            log.info("chat agent run loop timed out waiting for new user message")
        except asyncio.CancelledError:
            log.info("chat agent run loop cancelled")
        except Exception as e:
            log.exception("chat agent run loop error: {}", str(e))
        finally:
            await self._chat_termination_callback()
            await self._log_chat_thread()

    async def _handle_pending_messages(
        self, pending_messages: list[UserMessage]
    ) -> None:  # noqa: C901
        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"thread {self.chat_thread_id} not found")

        await self._acknowledge_pending_messages(pending_messages)

        if self._query_runner.has_running_queries():
            log.info(
                "waiting for query agent to complete before handling pending messages"
            )
            await self._query_runner.wait_on_running_queries()
        else:
            await self._create_query_agent_for_message(pending_messages[-1])

    async def _query_done_callback(self, task: asyncio.Task, query: Query) -> None:
        if (exc := task.exception()) is not None:
            log.opt(exception=exc).exception(
                "Query task exited with error: {}", str(exc)
            )
            log.debug("Query task exited with no answer")
            pending_messages = await self._pending_messages()
            if not pending_messages:
                self._termination_event.set()

    async def _create_query_agent_for_message(
        self,
        message: UserMessage,
    ) -> None:
        log.info("creating new query agent to handle pending messages")

        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"thread {self.chat_thread_id} not found")

        query_id = await self._query_runner.launch(
            query_text=message.content,
            chat_thread=chat_thread,
            instructions=self._generate_instructions_based_on_response_type(message),
        )
        chat_message = Message.model_validate(message, from_attributes=True)
        chat_message.query_id = query_id

        await self.chat_manager.update_message(chat_message)

    async def _wait_for_new_message(self, timeout: float) -> None:
        await asyncio.wait_for(
            self.chat_manager.wait_for_new_user_message(self.chat_thread_id),
            timeout=timeout,
        )
        log.info("new user message received")

    def is_running(self) -> bool:
        return bool(self._run_task and not self._run_task.done())

    async def _process_query_state_change(self, query: Query) -> None:
        if not query.state.is_terminated():
            return

        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"thread {self.chat_thread_id} not found")

        if not query.answer:
            log.debug("Query task exited with no answer")
            return

        response_type, language = (
            self._get_response_type_and_language_for_assistant_message(
                query, chat_thread.messages
            )
        )

        final_response_msg = AssistantMessage(
            content=query.answer,
            query_id=query.query_id,
            chat_thread_id=self.chat_thread_id,
            response_type=response_type,
            language=language,
        )
        await self._add_assistant_response(final_response_msg)

        pending_messages = await self._pending_messages()
        if not pending_messages:
            self._termination_event.set()

    async def _pending_messages(self) -> list[UserMessage]:
        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"thread {self.chat_thread_id} not found")
        return chat_thread.pending_messages

    async def _acknowledge_pending_messages(self, messages: list[UserMessage]) -> None:
        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"thread {self.chat_thread_id} not found")

        for msg in messages:
            await self._mark_message_acknowledged(msg)
        # self._acknowledge_event.set()

    async def _mark_message_acknowledged(self, msg: UserMessage) -> None:
        msg.acknowledged = True
        await self.chat_manager.update_message(Message.model_validate(msg))

    async def _add_assistant_response(self, msg: AssistantMessage) -> None:
        # Always add the message to the chat thread, independent of whether we send a message in Slack
        await self.chat_manager.add_assistant_message(
            self.chat_thread_id, Message.model_validate(msg, from_attributes=True)
        )

    def _generate_instructions_based_on_response_type(
        self, message: UserMessage
    ) -> str:
        if message.requested_response_type == MessageResponseType.TEXT_MESSAGE:
            return "Restrict the response to 20 words or less"
        elif message.requested_response_type == MessageResponseType.AUDIO:
            return "This response is going to be converted to audio. Please respond in a way that is easy to understand and concise. Restrict the response to 60 words or less."
        else:
            return "Restrict the response to 80 words or less."

    def _get_response_type_and_language_for_assistant_message(
        self, query: Query, messages: list[Message]
    ) -> tuple[MessageResponseType, Language]:
        # Find the user message that triggered this query
        for message in messages:
            if (
                message.source == MessageSource.WEBAPP
                and query.query_id == message.query_id
            ):
                response_type = (
                    message.requested_response_type or MessageResponseType.TEXT
                )
                language = message.language or Language.ENGLISH
                return response_type, language

        return MessageResponseType.TEXT, Language.ENGLISH

    async def _log_chat_thread(self) -> None:
        chat_thread = await self.chat_manager.get_chat_thread(self.chat_thread_id)
        if not chat_thread:
            raise ValueError(f"chat thread {self.chat_thread_id} does not exist")
        log.info("chat thread completed: {}", chat_thread)
