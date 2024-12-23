from informed.config import Config
from informed.db_models.users import User
from informed.db import session_maker
from sqlalchemy.sql import select, ColumnElement
from fastapi import HTTPException, status
from uuid import UUID
from typing import cast


class UserManager:
    def __init__(self, config: Config):
        self.config = config

    async def get_user(self, user_id: UUID) -> User:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(cast(ColumnElement[bool], User.user_id == user_id))
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
