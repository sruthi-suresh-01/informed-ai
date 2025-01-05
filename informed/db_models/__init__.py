from sqlmodel import Field, Relationship, SQLModel

from .shared_types import EnumAsString, JSONBFromPydantic

# If you have any utility functions or classes, import them here
from .users import (
    Language,
    User,
    UserDetails,
    UserMedicalDetails,
    UserMedications,
    UserHealthConditions,
    WeatherSensitivities,
    Settings,
    UserConfigurations,
)
from .weather_alert import WeatherAlert

from .query import Query, QueryState, QuerySource

from .chat import (
    ChatThread,
    Message,
    MessageSource,
    MessageResponseType,
    UserMessage,
    AssistantMessage,
)

from .notification import Notification, NotificationStatus

__all__ = [
    # Base and utility classes
    "SQLModel",
    "Field",
    "Relationship",
    "EnumAsString",
    "JSONBFromPydantic",
    # User-related models
    "User",
    "UserDetails",
    "Language",
    "UserMedicalDetails",
    # Weather-related models
    # Query-related models
    "Query",
    "QueryState",
    "QuerySource",
    # Weather Alert related models
    "WeatherAlert",
    # Chat-related models
    "ChatThread",
    "Message",
    "UserMessage",
    "AssistantMessage",
    "MessageSource",
    "MessageResponseType",
    # User Settings
    "Settings",
    "UserConfigurations",
    # Notification related models
    "Notification",
    "NotificationStatus",
]
