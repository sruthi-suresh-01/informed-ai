from pydantic import BaseModel, field_validator, Field
from typing import List, Optional

class CreateUserRequest(BaseModel):
    username: str
    email: str


class LoginRequest(BaseModel):
    username: str



class LanguageRequest(BaseModel):
    name: str
    is_preferred: bool = Field(default=False, description="Indicates if the language is preferred")


class UserDetailsRequest(BaseModel):
    first_name: str
    last_name: str
    age: int
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    ethnicity: Optional[str] = None
    languages: List[LanguageRequest]

    @field_validator('languages')
    def must_contain_language(cls, v):
        if not v:
            raise ValueError('At least one language is required')
        return v
    
class LanguageResponse(BaseModel):
    name: str
    is_preferred: bool

class UserDetailsResponse(BaseModel):
    first_name: str
    last_name: str
    age: int
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    ethnicity: Optional[str] = None
    languages: List[LanguageResponse]





class HealthCondition(BaseModel):
    id: Optional[int] = None
    condition: str
    severity: str
    description: str

class Medication(BaseModel):
    id: Optional[int] = None
    name: str
    dosage: str
    frequency: str

class MedicalDetails(BaseModel):
    id: Optional[int] = None
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    health_conditions: List[HealthCondition] = []
    medications: List[Medication] = []

class UserMedicalDetailsRequest(BaseModel):
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    health_conditions: List[HealthCondition] = []
    medications: List[Medication] = []
