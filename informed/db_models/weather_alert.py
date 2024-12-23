from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, String, Text, Boolean
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlmodel import Field, SQLModel


class WeatherAlert(SQLModel, table=True):
    __tablename__ = "weather_alerts"  #  type: ignore

    weather_alert_id: UUID = Field(default_factory=uuid4, primary_key=True)
    zip_code: str = Field(sa_column=Column(String(20), nullable=False, index=True))
    message: str = Field(sa_column=Column(Text, nullable=False))
    is_active: bool = Field(sa_column=Column(Boolean, nullable=False, default=True))
    created_by: UUID = Field(
        sa_column=Column(SQLAlchemyUuid(as_uuid=True), nullable=False)
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    cancelled_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, default=None)
    )
