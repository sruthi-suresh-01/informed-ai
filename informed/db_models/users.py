from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlmodel import Field, Relationship, SQLModel
from typing import Any
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from informed.db_models.shared_types import JSONBFromPydantic


class AccountType(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(SQLModel, table=True):
    __tablename__ = "users"  #  type: ignore

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    is_active: bool = Field(sa_column=Column(Boolean))
    account_type: AccountType = Field(
        default=AccountType.USER, sa_column=Column(SQLAlchemyEnum(AccountType))
    )

    details: Optional["UserDetails"] = Relationship(
        sa_relationship=relationship(
            "UserDetails",
            back_populates="user",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    medical_details: Optional["UserMedicalDetails"] = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="user",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    settings: Mapped["Settings"] = Relationship(
        sa_relationship=relationship(
            back_populates="user",
            lazy="joined",
            innerjoin=True,
            passive_deletes="all",
        )
    )


class Language(str, Enum):
    ENGLISH = "english"
    SPANISH = "spanish"
    TAGALOG = "tagalog"
    # Add more languages as needed


class UserDetails(SQLModel, table=True):
    __tablename__ = "user_details"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    age: int | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = Field(default=None, sa_column=Column(String(50), nullable=True))
    state: str | None = Field(default=None, sa_column=Column(String(30), nullable=True))
    zip_code: str | None = Field(
        default=None, sa_column=Column(String(20), nullable=True)
    )
    country: str | None = Field(
        default=None, sa_column=Column(String(50), nullable=True)
    )
    phone_number: str | None = None
    ethnicity: str | None = None
    language: Language = Field(
        default=Language.ENGLISH, sa_column=Column(SQLAlchemyEnum(Language))
    )
    user: "User" = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="details",
            lazy="joined",  # Set lazy loading here
        )
    )


class UserMedicalDetails(SQLModel, table=True):
    __tablename__ = "user_medical_details"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    blood_type: str | None = Field(default=None, sa_column=Column(String(3)))
    height: float | None = None
    weight: float | None = None
    user: "User" = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="medical_details",
            lazy="joined",  # Set lazy loading here
        )
    )
    health_conditions: list["UserHealthConditions"] = Relationship(
        sa_relationship=relationship(
            "UserHealthConditions",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    medications: list["UserMedications"] = Relationship(
        sa_relationship=relationship(
            "UserMedications",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    allergies: list["UserAllergies"] = Relationship(
        sa_relationship=relationship(
            "UserAllergies",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    weather_sensitivities: list["WeatherSensitivities"] = Relationship(
        sa_relationship=relationship(
            "WeatherSensitivities",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )

    @classmethod
    def create(cls, **kwargs: Any) -> "UserMedicalDetails":
        instance = cls(**kwargs)
        instance.health_conditions = []
        instance.medications = []
        instance.allergies = []
        instance.weather_sensitivities = []
        return instance


class UserHealthConditions(SQLModel, table=True):
    __tablename__ = "user_health_conditions"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE"),
        )
    )
    condition: str = Field(sa_column=Column(String(100)))
    severity: str = Field(sa_column=Column(String(50)))
    description: str | None = Field(sa_column=Column(Text))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="health_conditions",
            lazy="joined",  # Set lazy loading here
        )
    )


class UserMedications(SQLModel, table=True):
    __tablename__ = "user_medications"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE"),
        )
    )
    name: str = Field(sa_column=Column(String(100)))
    dosage: str = Field(sa_column=Column(String(100)))
    frequency: str = Field(sa_column=Column(String(50)))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="medications",
            lazy="joined",  # Set lazy loading here
        )
    )


class UserAllergies(SQLModel, table=True):
    __tablename__ = "user_allergies"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE"),
        )
    )
    allergen: str = Field(sa_column=Column(String(100)))
    reaction: str | None = Field(sa_column=Column(Text))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="allergies",
            lazy="joined",  # Set lazy loading here
        )
    )


class WeatherSensitivities(SQLModel, table=True):
    __tablename__ = "weather_sensitivities"  #  type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE"),
        )
    )
    type: str = Field(
        sa_column=Column(String(50))
    )  # e.g., rain, temperature, air_quality
    description: str | None = Field(sa_column=Column(Text))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="weather_sensitivities",
            lazy="joined",  # Set lazy loading here
        )
    )


"""
This configuration model might need to change in the future.
It is meant to store settings/configurations which may change over time.
TODO: Introduce a property/method to extract/store only current valid configurations,
      possibly with versioning or deprecation handling for older configuration formats.
"""


class UserConfigurations(BaseModel):
    daily_updates: bool = False
    daily_update_prompt: str = ""


class Settings(SQLModel, table=True):
    __tablename__ = "settings"  #  type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    configurations: UserConfigurations = Field(
        sa_column=Column(JSONBFromPydantic(UserConfigurations)), default_factory=dict
    )
    user: "User" = Relationship(
        back_populates="settings",
    )
