from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from informed.db_models.users import (
    Language,
    UserDetails,
    UserHealthConditions,
    UserLanguage,
    UserMedicalDetails,
    UserMedications,
    WeatherSensitivities,
)


class QuestionsRequest(BaseModel):
    question: str


class GetQuestionAndFactsResponse(BaseModel):
    question: str
    facts: list[str] | None = None
    status: str
    source: str | None = None


class CreateUserRequest(BaseModel):
    username: str
    email: str


class LoginRequest(BaseModel):
    username: str


class LanguageRequest(BaseModel):
    name: str
    is_preferred: bool = Field(
        default=False, description="Indicates if the language is preferred"
    )


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
    languages: list[LanguageRequest]

    @field_validator("languages")
    def must_contain_language(cls, v: list[LanguageRequest]) -> list[LanguageRequest]:
        if not v:
            raise ValueError("At least one language is required")
        return v


class UserLanguageResponse(BaseModel):
    id: UUID
    name: Language
    is_preferred: bool

    @classmethod
    def from_db(cls, user_language: UserLanguage) -> "UserLanguageResponse":
        return cls.model_validate(user_language, from_attributes=True)


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
    languages: list[UserLanguageResponse] = []

    @classmethod
    def from_user_details(cls, user_details: UserDetails) -> "UserDetailsResponse":
        details = user_details.model_dump(mode="json")
        details["languages"] = [
            UserLanguageResponse.from_db(language)
            for language in user_details.languages
        ]
        return cls.model_validate(details)


class HealthCondition(BaseModel):
    id: int | None = None
    condition: str
    severity: str
    description: str


class Medication(BaseModel):
    id: int | None = None
    name: str
    dosage: str
    frequency: str


class WeatherSensitivity(BaseModel):
    id: int | None = None
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
