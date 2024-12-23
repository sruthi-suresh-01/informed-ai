import traceback

import json

from fastapi import Request, Cookie, HTTPException, status, Depends
from sqlalchemy.future import select

from informed.db import session_maker
from informed.db_models.users import User
from typing import Annotated


async def get_current_user(request: Request, session_token: str = Cookie(None)) -> User:
    redis_client = request.app.state.redis_client

    serialized_session = await redis_client.get(session_token)
    if not serialized_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session or expired session",
        )

    try:
        # Convert the Redis response to a string before parsing
        session_object = json.loads(str(serialized_session))
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session data format",
        )

    if not session_object or not session_object.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session data"
        )

    try:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(User.email == session_object["email"])
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e!s}")


UserDep = Annotated[User, Depends(get_current_user)]


def get_concise_exception_traceback(exc: Exception, num_lines: int = 2) -> str:
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    return "".join(tb_lines[-num_lines:])
