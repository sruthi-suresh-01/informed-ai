from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from informed.db_models.shared_types import EnumAsString, JSONBFromPydantic


class QueryState(Enum):
    CREATED = "created"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QuerySource(BaseModel):
    source: str
    description: str | None = None


class Query(SQLModel, table=True):
    __tablename__ = "queries"  #  type: ignore

    query: str = Field(nullable=False)
    query_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    sources: list[QuerySource] = Field(
        sa_column=Column(JSONBFromPydantic(QuerySource)), default_factory=list
    )
    state: QueryState = Field(
        default=QueryState.CREATED,
        sa_column=Column(EnumAsString(QueryState), nullable=False),
    )
    findings: list[str] = Field(sa_column=Column(JSONB), default_factory=list)
