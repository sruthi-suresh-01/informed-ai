from datetime import datetime
from enum import Enum
import time
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlalchemy.types import String

from sqlalchemy.dialects.postgresql import JSONB
from informed.db_models.shared_types import EnumAsString, JSONBFromPydantic
from informed.db_models.users import Language
import time
from enum import Enum
from uuid import UUID, uuid4

import sqlalchemy as sq
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, declared_attr, relationship
from sqlalchemy.types import String
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlmodel import Boolean, Column, Field, Relationship, SQLModel, ForeignKey


class MessageResponseType(Enum):
    TEXT = "text"
    TEXT_MESSAGE = "text_message"
    AUDIO = "audio"


class MessageSource(Enum):
    WEBAPP = "webapp"
    ASSISTANT = "assistant"


class BaseMessage(SQLModel):
    message_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: float = Field(default_factory=time.time)
    content: str
    chat_thread_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("chat_thread.chat_thread_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    source: MessageSource = Field(sa_column=Column(EnumAsString(MessageSource)))
    response_type: MessageResponseType = Field(
        sa_column=Column(EnumAsString(MessageResponseType)),
        default=MessageResponseType.TEXT,
    )


class UserMessage(BaseMessage):
    user_id: UUID | None = Field(default=None)
    source: MessageSource = Field(default=MessageSource.WEBAPP)
    acknowledged: bool = Field(default=False)
    requested_response_type: MessageResponseType | None = Field(
        default=MessageResponseType.TEXT
    )

    def is_pending(self) -> bool:
        return not self.acknowledged


class AssistantMessage(BaseMessage):
    query_id: UUID | None = Field(default=None)
    language: Language = Field(default=Language.ENGLISH)
    source: MessageSource = Field(default=MessageSource.ASSISTANT)


class Message(BaseMessage, table=True):
    user_id: UUID | None = Field(default=None)
    query_id: UUID | None = Field(default=None)
    acknowledged: bool = Field(default=False)
    requested_response_type: MessageResponseType | None = Field(default=None)
    chat_thread: "ChatThread" = Relationship(back_populates="messages")
    language: Language = Field(default=Language.ENGLISH)


class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_thread"  #  type: ignore

    chat_thread_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    created_at: float = Field(default_factory=time.time)
    messages: Mapped[list[Message]] = Relationship(
        sa_relationship=relationship(
            back_populates="chat_thread",
            lazy="joined",
            innerjoin=True,
            passive_deletes="all",
            order_by="Message.created_at",
        )
    )

    @property
    def pending_messages(self) -> list[UserMessage]:
        all_user_messages = [
            UserMessage.model_validate(message, from_attributes=True)
            for message in self.messages
            if message.source == MessageSource.WEBAPP
        ]
        pending_messages = [m for m in all_user_messages if m.is_pending()]
        return pending_messages
