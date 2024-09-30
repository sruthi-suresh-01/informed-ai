import asyncio
import json
from typing import cast, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger

from informed.helper.utils import get_current_user
from informed.api.api_types import QueryRequest, QueryResponse
from informed.db_models.users import (
    User,
)
from informed.db_models.weather import WeatherData
from informed.informed import InformedManager
from uuid import UUID

# from dependencies import db_dependency
chat_query_router = APIRouter()

# TODO: Move to Session Store
current_task: asyncio.Task | None = None  # Reference to the current processing task
processing_data: dict[str, Any] = {}

# Lock to synchronize access to processing_data
lock = asyncio.Lock()


@chat_query_router.post("/submit_question", response_model=QueryResponse)
async def submit_question(
    request: Request,
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
) -> QueryResponse:

    # Check if the user exists
    user = current_user

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    app_manager = cast(InformedManager, request.app.state.app_manager)
    query = await app_manager.create_query(user_id=user.id, query=query_request.query)
    query = await app_manager.start_query(
        query.query_id
    )  # TODO: this is temporary until i integrate the query_start
    return query


@chat_query_router.post("/{query_id}/start", response_model=QueryResponse)
async def start_query(
    request: Request, query_id: UUID, current_user: User = Depends(get_current_user)
) -> QueryResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)

    try:
        query = await app_manager.start_query(query_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Query {query_id} not found")

    return query


@chat_query_router.get("/get_question_and_facts", response_model=QueryResponse)
async def get_question_and_facts(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    logger.info("Inside GET function")

    app_manager = cast(InformedManager, request.app.state.app_manager)
    query = await app_manager.get_recent_query_for_user(current_user.id)
    if not query:
        raise HTTPException(
            status_code=404, detail="No active or recent task data found"
        )
    return query
