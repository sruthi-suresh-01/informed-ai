import asyncio
import time
from abc import ABC, abstractmethod
from typing import cast
from uuid import UUID

from loguru import logger as log
from sqlalchemy import ColumnElement, exists, select, text
from informed.db import session_maker

from informed.db_models.chat import ChatThread, Message
from informed.api.schema import ChatRequest, AddUserMessageRequest


class ChatManager(ABC):
    @abstractmethod
    async def create_chat_thread(
        self, chat_request: ChatRequest, user_id: UUID
    ) -> ChatThread:
        pass

    @abstractmethod
    async def add_user_message(
        self, add_user_message_request: AddUserMessageRequest, user_id: UUID
    ) -> UUID:
        pass

    @abstractmethod
    async def add_assistant_message(
        self, chat_thread_id: UUID, message: Message
    ) -> None:
        pass

    @abstractmethod
    async def get_chat_thread(self, chat_thread_id: UUID) -> ChatThread | None:
        pass

    @abstractmethod
    async def get_all_chat_threads(self) -> list[ChatThread]:
        pass

    @abstractmethod
    async def delete_chat_thread(self, chat_thread_id: UUID) -> None:
        pass

    @abstractmethod
    async def wait_for_new_user_message(self, chat_thread_id: UUID) -> None:
        pass

    @abstractmethod
    def add_user_message_event(self, chat_thread_id: UUID) -> None:
        pass

    @abstractmethod
    async def update_message(self, message: Message) -> None:
        pass

    @abstractmethod
    async def get_message(self, message_id: UUID) -> Message | None:
        pass


class DBChatManager(ChatManager):
    def __init__(self) -> None:
        self._new_message_events: dict[UUID, asyncio.Event] = {}

    async def wait_for_new_user_message(self, chat_thread_id: UUID) -> None:
        if chat_thread_id not in self._new_message_events:
            self._new_message_events[chat_thread_id] = asyncio.Event()
        await self._new_message_events[chat_thread_id].wait()
        self._new_message_events[chat_thread_id].clear()

    def add_user_message_event(self, chat_thread_id: UUID) -> None:
        if chat_thread_id not in self._new_message_events:
            self._new_message_events[chat_thread_id] = asyncio.Event()
        self._new_message_events[chat_thread_id].set()

    async def create_chat_thread(
        self, chat_request: ChatRequest, user_id: UUID
    ) -> ChatThread:
        chat_thread = ChatThread(user_id=user_id)
        message = chat_request.user_message(
            user_id, chat_thread_id=chat_thread.chat_thread_id
        )
        chat_thread.messages = [message]
        async with session_maker() as session:
            session.add(chat_thread)
            session.add(message)
            await session.commit()

        return chat_thread

    async def add_user_message(
        self, add_user_message_request: AddUserMessageRequest, user_id: UUID
    ) -> UUID:
        message = add_user_message_request.user_message(
            user_id, add_user_message_request.chat_thread_id
        )
        chat_thread = await self.get_chat_thread(
            add_user_message_request.chat_thread_id
        )
        if not chat_thread:
            raise Exception(
                f"chat thread {add_user_message_request.chat_thread_id} does not exist"
            )

        async with session_maker() as session:
            chat_thread.messages.append(message)
            session.add(chat_thread)
            await session.commit()

        self.add_user_message_event(chat_thread.chat_thread_id)

        return message.message_id

    async def add_assistant_message(
        self, chat_thread_id: UUID, message: Message
    ) -> None:
        chat_thread = await self.get_chat_thread(chat_thread_id)
        if not chat_thread:
            raise Exception(f"chat thread {chat_thread_id} does not exist")
        chat_thread.messages.append(message)
        async with session_maker() as session:
            session.add(chat_thread)
            await session.commit()

    async def get_chat_thread(self, chat_thread_id: UUID) -> ChatThread | None:
        async with session_maker() as session:
            result = await session.execute(
                select(ChatThread).filter(
                    cast(
                        ColumnElement[bool], ChatThread.chat_thread_id == chat_thread_id
                    )
                )
            )
            return result.unique().scalars().first()

    async def get_message(self, message_id: UUID) -> Message | None:
        async with session_maker() as session:
            result = await session.get(Message, message_id)
            return result

    async def get_all_chat_threads(self) -> list[ChatThread]:
        async with session_maker() as session:
            result = await session.execute(select(ChatThread))
            return list(result.unique().scalars().all())

    async def delete_chat_thread(self, chat_thread_id: UUID) -> None:
        async with session_maker() as session:
            stmt = select(ChatThread).filter(
                cast(ColumnElement[bool], ChatThread.chat_thread_id == chat_thread_id)
            )
            result = await session.execute(stmt)
            chat_thread = result.unique().scalar_one_or_none()
            if chat_thread is None:
                raise ValueError(f"chat thread {chat_thread_id} not found")
            await session.delete(chat_thread)
            await session.commit()

    async def update_message(self, message: Message) -> None:
        async with session_maker() as session:
            await session.merge(message)
            await session.commit()
