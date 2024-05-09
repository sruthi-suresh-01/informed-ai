from pydantic import BaseModel
from typing import List, Optional
from app.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Date, Text, Float, DateTime

from sqlalchemy.orm import relationship, sessionmaker


class User(Base):
    __tablename__ = 'users'    

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean)
    account_type = Column(String)
    details = relationship("UserDetails", back_populates="user", uselist=False)


class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String(50))  # e.g., Misc, Health-related, Travel-related
    description = Column(Text)
    date = Column(DateTime)
    duration = Column(Integer)  # Duration in minutes
    location = Column(String(100))  # Optional


class UserDetails(Base):
    __tablename__ = 'user_details'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age=Column(Integer)
    address_line1 = Column(String)
    address_line2 = Column(String)
    city = Column(String(50))
    state = Column(String(30))
    zip_code = Column(String(20))
    country = Column(String(50))
    phone_number = Column(String)
    ethnicity = Column(String)
    languages = relationship("UserLanguage", back_populates="user_details")
    user = relationship("User", back_populates="details")    

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

class UserLanguage(Base):
    __tablename__ = 'user_languages'
    user_details_id = Column(Integer, ForeignKey('user_details.id'), primary_key=True)
    language_id = Column(Integer, ForeignKey('languages.id'), primary_key=True)
    language = relationship("Language")
    is_preferred = Column(Boolean, default=False, nullable=False)
    user_details = relationship("UserDetails", back_populates="languages")

class UserMedicalDetails(Base):
    __tablename__ = 'user_medical_details'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    blood_type = Column(String(3))
    height = Column(Float)  # In centimeters or meters
    weight = Column(Float)  # In kilograms

class UserHealthConditions(Base):
    __tablename__ = 'user_health_conditions'
    id = Column(Integer, primary_key=True)
    user_medical_id = Column(Integer, ForeignKey('user_medical_details.id'))
    condition = Column(String(100))
    severity = Column(String(50))
    description = Column(Text)

class UserMedications(Base):
    __tablename__ = 'user_medications'
    id = Column(Integer, primary_key=True)
    user_medical_id = Column(Integer, ForeignKey('user_medical_details.id'))
    name = Column(String(100))
    dosage = Column(String(100))
    frequency = Column(String(50))

class UserAllergies(Base):
    __tablename__ = 'user_allergies'
    id = Column(Integer, primary_key=True)
    user_medical_id = Column(Integer, ForeignKey('user_medical_details.id'))
    allergen = Column(String(100))
    reaction = Column(Text)


UserMedicalDetails.user = relationship("User", back_populates="medical_details")
User.medical_details = relationship("UserMedicalDetails", back_populates="user", uselist=False)

UserHealthConditions.user_medical_details = relationship("UserMedicalDetails", back_populates="health_conditions")
UserMedicalDetails.health_conditions = relationship("UserHealthConditions", back_populates="user_medical_details")

UserMedications.user_medical_details = relationship("UserMedicalDetails", back_populates="medications")
UserMedicalDetails.medications = relationship("UserMedications", back_populates="user_medical_details")

UserAllergies.user_medical_details = relationship("UserMedicalDetails", back_populates="allergies")
UserMedicalDetails.allergies = relationship("UserAllergies", back_populates="user_medical_details")


    
Activity.user = relationship("User", back_populates="activities")
User.activities = relationship("Activity", back_populates="user")
