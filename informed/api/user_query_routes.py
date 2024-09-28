import asyncio
import json
from typing import cast, Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import ColumnElement, select

from backend.app.gptclient import generate_response
from backend.app.services.user_services import get_current_user
from backend.app.util import extract_user_info
from informed.api.api_types import GetQuestionAndFactsResponse, QuestionsRequest
from informed.db import session_maker
from informed.db_models.users import (
    User,
)
from informed.db_models.weather import WeatherData

# from dependencies import db_dependency
user_query_router = APIRouter()

# TODO: Move to Session Store
current_task: asyncio.Task | None = None  # Reference to the current processing task
processing_data: dict[str, Any] = {}

# Lock to synchronize access to processing_data
lock = asyncio.Lock()


@user_query_router.post("/submit_question")
async def submit_question(
    request: QuestionsRequest, current_user: User = Depends(get_current_user)
) -> dict:

    # Check if the user exists
    user = current_user

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    global current_task

    # Killing previous generate process if new we get a new question
    if current_task and not current_task.done():
        logger.info("Current task running, attempting to cancel...")
        current_task.cancel()
        try:
            await current_task  # Wait for the task to actually cancel
            logger.info("Current task was successfully cancelled.")
        except asyncio.CancelledError:
            logger.info("Successfully caught cancellation of the task.")
        except Exception as e:
            logger.error(f"Error during task cancellation: {e}")

    processing_data["question"] = request.question
    processing_data["facts"] = []
    processing_data["status"] = "processing"

    # Temp hardcoded user profile
    if user and user.details and user.details.zip_code:
        print(user.details.zip_code)
        async with session_maker() as session:
            latest_weather_query = await session.execute(
                select(WeatherData)
                .filter(
                    cast(
                        ColumnElement[bool],
                        WeatherData.zip_code == user.details.zip_code,
                    )
                )
                .order_by(WeatherData.timestamp.desc())  # type: ignore
            )
            latest_weather = latest_weather_query.first()

        if latest_weather and latest_weather[0].weather_conditions:
            weather_conditions = json.loads(latest_weather[0].weather_conditions)
            current_task = asyncio.create_task(
                process_query(request, user, weather_conditions)
            )
        else:
            logger.warning(
                f"No weather data available for zip code: {user.details.zip_code}"
            )
            current_task = asyncio.create_task(process_query(request, user, []))

    logger.info("Started new task for processing documents")

    return {"status": "processing"}


@user_query_router.get(
    "/get_question_and_facts", response_model=GetQuestionAndFactsResponse
)
async def get_question_and_facts(
    current_user: User = Depends(get_current_user),
) -> dict:
    logger.info("Inside GET function")

    # Check if the user exists
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not processing_data or (processing_data and not processing_data["question"]):
        raise HTTPException(
            status_code=404, detail="No active or recent task data found"
        )
    if processing_data and processing_data["facts"] is None:
        processing_data["status"] = "processing"

    print(processing_data)
    return processing_data


# Async function
async def process_query(
    request: QuestionsRequest, user: User, weather_alerts: list[dict[str, Any]]
) -> None:
    facts = []
    async with lock:
        try:
            if user and user.details and user.details.zip_code:

                user_info = extract_user_info(user)
                print("userifdo: ", user_info)
                gpt_response = await generate_response(
                    query=request.question, alerts=weather_alerts, user_info=user_info
                )
                logger.info(
                    f"GPT response processed.\n {gpt_response.model_dump_json()}"
                )

                #  Adding extra checks due to unpredictability of LLM
                if (
                    gpt_response.facts
                    and isinstance(gpt_response.facts, list)
                    and len(gpt_response.facts) > 0
                    and not (
                        len(gpt_response.facts) == 1
                        and gpt_response.facts[0].strip() == ""
                    )
                ):
                    facts = gpt_response.facts
                else:
                    facts = [
                        "I'm sorry, I'm unable to answer your question. Can you please try again?"
                    ]

                processing_data["facts"] = facts
                processing_data["status"] = "done"
                if gpt_response and gpt_response.source:
                    processing_data["source"] = gpt_response.source

                logger.info(processing_data["facts"])

        except asyncio.CancelledError:
            logger.info("Document processing was cancelled.")
            processing_data["status"] = "cancelled"
            raise
        except Exception as e:
            processing_data["status"] = "done"
            logger.error(f"Error processing documents: {e}")
