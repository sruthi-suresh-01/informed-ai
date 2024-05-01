from fastapi import APIRouter, Depends

from app.core.models.users import User
from app.core.schemas.user_request import CreateUserRequest
from app.dependencies import db_dependency
user_router = APIRouter()


@user_router.post("/create/")
async def create_user(user: CreateUserRequest, db: db_dependency):
    db_user = User(username=user.username, email=user.email, is_active=True, account_type='user')
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
