from sqlmodel import Field, Relationship, SQLModel

from .chat import (
    AssistantMessage,
    ChatThread,
    Message,
    MessageResponseType,
    MessageSource,
    UserMessage,
)
from .notification import Notification, NotificationStatus
from .query import Query, QuerySource, QueryState
from .shared_types import EnumAsString, JSONBFromPydantic

# If you have any utility functions or classes, import them here
from .users import (
    Language,
    Settings,
    User,
    UserConfigurations,
    UserDetails,
    UserHealthConditions,
    UserMedicalDetails,
    UserMedications,
    WeatherSensitivities,
)
from .weather_alert import WeatherAlert

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
