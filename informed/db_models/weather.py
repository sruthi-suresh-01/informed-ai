from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlmodel import Field, SQLModel


class WeatherData(SQLModel, table=True):
    __tablename__ = "weather_data"  #  type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    zip_code: str = Field(sa_column=Column(String(10), index=True, nullable=False))
    date: datetime = Field(sa_column=Column(DateTime, nullable=False))
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    weather_conditions: str = Field(sa_column=Column(Text, nullable=False))

    # You can add relationships here if needed, for example:
    # user_medical_details: List["UserMedicalDetails"] = Relationship(
    #     sa_relationship=relationship(
    #         "UserMedicalDetails",
    #         back_populates="weather_data",
    #         lazy="joined",
    #         passive_deletes="all"
    #     )
    # )
