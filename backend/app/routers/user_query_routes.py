from fastapi import APIRouter, HTTPException, Depends
import asyncio
from typing import Optional

from app.core.schemas.user_query_request import QuestionsRequest, GetQuestionAndFactsResponse
from app.util import extract_alert_info, fetchAlerts, extract_user_info
from app.config import logger
from app.gptclient import generate_response
from app.core.models.users import User, UserDetails, UserLanguage, Language, UserAllergies, UserHealthConditions, UserMedicalDetails, UserMedications
from app.services.user_services import get_current_user
from app.dependencies import db_dependency


# from dependencies import db_dependency
user_query_router = APIRouter()

# TODO: Move to Session Store
current_task: Optional[asyncio.Task] = None # Reference to the current processing task
processing_data = {}

# Lock to synchronize access to processing_data
lock = asyncio.Lock()


@user_query_router.post("/submit_question")
async def submit_question(request: QuestionsRequest, db: db_dependency, current_user: User = Depends(get_current_user)):

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
    processing_data["facts"] = None
    processing_data["status"] = "processing"
    
    # Temp hardcoded user profile

    current_task = asyncio.create_task(process_query(request, user))
    logger.info("Started new task for processing documents")

    return {"status": "processing"}


@user_query_router.get("/get_question_and_facts", response_model=GetQuestionAndFactsResponse)
async def get_question_and_facts(current_user: User = Depends(get_current_user)):
    logger.info("Inside GET function")

     # Check if the user exists
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not processing_data or (processing_data and not processing_data["question"]) :
        raise HTTPException(status_code=404, detail="No active or recent task data found")
    if processing_data and processing_data["facts"] is None:
        processing_data["status"] = "processing"  

    print(processing_data)      
    return processing_data


# Async function
async def process_query(request: QuestionsRequest, user):
    facts = []
    zip_alerts = []
    async with lock:
        try:
            # user = user_profiles[request.user_id]
            if user and user.details and user.details.zip_code:
                extracted_info = []
                try:
                    
                    
                    
                    # Extracting all text from the documents
                    zip_alerts = await fetchAlerts(user.details.zip_code)
                    extracted_info = extract_alert_info(zip_alerts['data'])

                except Exception as e:
                    logger.error(e)
                    processing_data["status"] = "error"

                user_info = extract_user_info(user)
                print("userifdo: ", user_info)
                gpt_response = await generate_response(query=request.question, alerts=extracted_info, user_info=user_info)
                logger.info(f"GPT response processed.\n {gpt_response}")

                #  Adding extra checks due to unpredictability of LLM
                if "facts" in gpt_response and isinstance(gpt_response['facts'], list) and len(gpt_response["facts"]) >0 and not(len(gpt_response["facts"]) == 1 and gpt_response["facts"][0].strip() == ""):
                    facts = gpt_response["facts"]
                else:
                    facts = ["I'm sorry, I'm unable to answer your question. Can you please try again?"]

                processing_data["facts"] = facts
                processing_data["status"] = "done"

                logger.info(processing_data["facts"])

        except asyncio.CancelledError:
            logger.info("Document processing was cancelled.")
            processing_data["status"] = "cancelled"
            raise
        except Exception as e:
            processing_data["status"] = "error"
            logger.error(f"Error processing documents: {e}")
