from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from informed.db_models.users import (
    Language,
    UserDetails,
    UserHealthConditions,
    UserMedicalDetails,
    UserMedications,
    WeatherSensitivities,
    User,
)

from informed.db_models.query import QueryState, Query, QuerySource
from informed.db_models.chat import (
    Message,
    MessageSource,
    MessageResponseType,
    ChatThread,
)


class CreateUserRequest(BaseModel):
    email: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: str


class UserDetailsRequest(BaseModel):
    first_name: str
    last_name: str
    age: int
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    phone_number: str | None = None
    ethnicity: str | None = None
    language: Language = Language.ENGLISH


class UserDetailsResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    age: int | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    phone_number: str | None = None
    ethnicity: str | None = None
    language: Language = Language.ENGLISH

    @classmethod
    def from_user_details(cls, user_details: UserDetails) -> "UserDetailsResponse":
        details = user_details.model_dump(mode="json")
        return cls.model_validate(details)


class UserResponse(BaseModel):
    email: str
    account_type: str | None
    is_active: bool | None
    details: UserDetailsResponse | None = None

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        data = user.model_dump()
        if user.details:
            data["details"] = UserDetailsResponse.from_user_details(user.details)
        return cls.model_validate(data, from_attributes=True)


class AuthenticatedUserResponse(BaseModel):
    user: UserResponse

    @classmethod
    def from_user(cls, user: User) -> "AuthenticatedUserResponse":
        data = {"user": UserResponse.from_user(user)}
        return cls.model_validate(data, from_attributes=True)


class HealthCondition(BaseModel):
    id: UUID | None = None
    condition: str
    severity: str
    description: str


class Medication(BaseModel):
    id: int | None = None
    name: str
    dosage: str
    frequency: str


class WeatherSensitivity(BaseModel):
    id: UUID | None = None
    type: str
    description: str


class MedicalDetails(BaseModel):
    id: int | None = None
    blood_type: str | None = None
    height: float | None = None
    weight: float | None = None
    health_conditions: list[HealthCondition] = []
    medications: list[Medication] = []
    weather_sensitivities: list[WeatherSensitivity] = []


class UserMedicalDetailsRequest(BaseModel):
    blood_type: str | None = None
    height: float | None = None
    weight: float | None = None
    health_conditions: list[HealthCondition] = []
    weather_sensitivities: list[WeatherSensitivity] = []
    medications: list[Medication] = []


class WeatherDataCreate(BaseModel):
    zip_code: str
    weather_conditions: str


class WeatherDataResponse(BaseModel):
    id: int
    zip_code: str
    date: date
    timestamp: datetime
    weather_conditions: str

    class Config:
        from_attributes = True


class MedicationsResponse(BaseModel):
    id: UUID
    name: str
    dosage: str
    frequency: str

    @classmethod
    def from_db(cls, medications: UserMedications) -> "MedicationsResponse":
        return cls.model_validate(medications, from_attributes=True)


class HealthConditionsResponse(BaseModel):
    id: UUID
    condition: str
    severity: str
    description: str

    @classmethod
    def from_db(
        cls, healthConditions: UserHealthConditions
    ) -> "HealthConditionsResponse":
        return cls.model_validate(healthConditions, from_attributes=True)


class WeatherSensitivityResponse(BaseModel):
    id: UUID
    type: str
    description: str

    @classmethod
    def from_db(
        cls, weather_sensitivities: WeatherSensitivities
    ) -> "WeatherSensitivityResponse":
        return cls.model_validate(weather_sensitivities, from_attributes=True)


class UserMedicalDetailsResponse(BaseModel):
    id: UUID
    blood_type: str | None = None
    height: float | None = None
    weight: float | None = None
    health_conditions: list[HealthConditionsResponse] = []
    medications: list[MedicationsResponse] = []
    weather_sensitivities: list[WeatherSensitivityResponse] = []

    @classmethod
    def from_user_medical_details(
        cls, user_medical_details: UserMedicalDetails
    ) -> "UserMedicalDetailsResponse":
        medical_details = user_medical_details.model_dump(mode="json")
        medical_details["health_conditions"] = [
            HealthConditionsResponse.from_db(condition)
            for condition in user_medical_details.health_conditions
        ]
        medical_details["medications"] = [
            MedicationsResponse.from_db(medication)
            for medication in user_medical_details.medications
        ]
        medical_details["weather_sensitivities"] = [
            WeatherSensitivityResponse.from_db(sensitivity)
            for sensitivity in user_medical_details.weather_sensitivities
        ]
        return cls.model_validate(medical_details)


class UpdateQueryRequest(BaseModel):
    query_id: UUID
    state: QueryState


class QuerySourceResponse(BaseModel):
    source: str
    description: str | None = None

    @classmethod
    def from_db(cls, query_source: QuerySource) -> "QuerySourceResponse":
        return cls.model_validate(query_source, from_attributes=True)


class QueryResponse(BaseModel):
    query_id: UUID
    user_id: UUID
    query: str
    state: str
    sources: list[QuerySourceResponse]
    answer: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db(cls, query: Query) -> "QueryResponse":
        data = query.model_dump()
        return cls.model_validate(data)


class QueryRequest(BaseModel):
    query: str


# Chat


class ChatRequest(BaseModel):
    message: str
    source: MessageSource = MessageSource.WEBAPP
    requested_response_type: MessageResponseType | None = None

    def user_message(self, user_id: UUID | None, chat_thread_id: UUID) -> Message:
        return Message(
            content=self.message,
            user_id=user_id,
            chat_thread_id=chat_thread_id,
            source=self.source,
            requested_response_type=self.requested_response_type,
        )


class AddUserMessageRequest(ChatRequest):
    chat_thread_id: UUID


class ChatMessageResponse(BaseModel):
    message_id: UUID
    content: str
    created_at: datetime
    source: MessageSource
    response_type: MessageResponseType | None = None
    query_id: UUID | None = None

    # Hiding these from the response until we need them
    # user_id: UUID | None = None
    # acknowledged: bool = False
    # requested_response_type: MessagePresentationType | None = None

    @classmethod
    def from_chat_message(cls, message: Message) -> "ChatMessageResponse":
        data = message.model_dump()
        return cls.model_validate(data)


class ChatResponse(BaseModel):
    chat_thread_id: UUID
    messages: list[ChatMessageResponse]

    @classmethod
    def from_chat_thread(cls, chat_thread: ChatThread) -> "ChatResponse":
        data = chat_thread.model_dump()
        data["messages"] = [
            ChatMessageResponse.from_chat_message(message)
            for message in chat_thread.messages
        ]
        return cls.model_validate(data)
