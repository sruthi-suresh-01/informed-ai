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


class NotificationStatus(Enum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    DELIVERED = "DELIVERED"
    VIEWED = "VIEWED"
    FAILED = "FAILED"


class Notification(SQLModel, table=True):
    __tablename__ = "notification"  #  type: ignore

    notification_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    status: NotificationStatus = Field(
        sa_column=Column(EnumAsString(NotificationStatus)),
        default=NotificationStatus.PROCESSING,
    )
    title: str
    content: str
    chat_thread_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("chat_thread.chat_thread_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
