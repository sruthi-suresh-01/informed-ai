from app.database import engine, SessionLocal
from typing import Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import redis
import secrets

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)