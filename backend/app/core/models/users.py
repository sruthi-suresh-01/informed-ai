from pydantic import BaseModel
from typing import List, Optional
from app.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker



class User(Base):
    __tablename__ = 'users'    

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean)
    account_type = Column(String)

class UserDetails(Base):
    __tablename__ = 'user_details'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    address = Column(String)
    phone_number = Column(String)
    user = relationship("User", back_populates="details")

User.details = relationship("UserDetails", back_populates="user", uselist=False)
