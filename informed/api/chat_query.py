from typing import cast, Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, Response
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core import client_options
import os
from fastapi.responses import StreamingResponse
import io

from informed.helper.utils import get_current_user
from informed.api.schema import QueryRequest, QueryResponse
from informed.db_models.users import (
    User,
    Language,
)
from informed.informed import InformedManager
from uuid import UUID

# from dependencies import db_dependency
chat_query_router = APIRouter()


# # Create a Limiter instance
# limiter = Limiter(key_func=get_remote_address)


# @chat_query_router.post("/", response_model=QueryResponse)
# @limiter.limit("20/minute")
# async def submit_question(
#     request: Request,
#     query_request: QueryRequest,
#     current_user: User = Depends(get_current_user),
# ) -> QueryResponse:

#     # Check if the user exists
#     user = current_user

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     app_manager = cast(InformedManager, request.app.state.app_manager)
#     query = await app_manager.create_query(
#         user_id=user.user_id,
#         query=query_request.query,
#         response_mode=query_request.response_mode,
#     )
#     query = await app_manager.start_query(
#         query.query_id
#     )  # TODO: this is temporary until i integrate the query_start
#     return query


# @chat_query_router.post("/{query_id}/start", response_model=QueryResponse)
# async def start_query(
#     request: Request, query_id: UUID, current_user: User = Depends(get_current_user)
# ) -> QueryResponse:
#     app_manager = cast(InformedManager, request.app.state.app_manager)

#     try:
#         query = await app_manager.start_query(query_id)
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=f"Query {query_id} not found")

#     return query


# @chat_query_router.get("/latest", response_model=QueryResponse)
# async def get_question_and_facts(
#     request: Request,
#     current_user: User = Depends(get_current_user),
# ) -> QueryResponse:
#     logger.info("Inside GET function")

#     app_manager = cast(InformedManager, request.app.state.app_manager)
#     query = await app_manager.get_recent_query_for_user(current_user.user_id)
#     if not query:
#         raise HTTPException(
#             status_code=404, detail="No active or recent task data found"
#         )
#     return query


# # @chat_query_router.get("/tts/{query_id}")
# # async def get_query_tts(
# #     query_id: UUID,
# #     request: Request,
# #     current_user: User = Depends(get_current_user)
# # ):
# #     # Create client with API key
# #     options = client_options.ClientOptions(
# #         api_key=os.getenv('GOOGLE_API_KEY')
# #     )
# #     client = texttospeech.TextToSpeechClient(client_options=options)

# #     app_manager = request.app.state.app_manager
# #     try:
# #         # Get query findings
# #         query = await app_manager.get_query(query_id)
# #         if not query:
# #             raise HTTPException(status_code=404, detail="Query not found")

# #         # Get user's preferred language
# #         user_language = current_user.details.language if current_user.details else Language.ENGLISH

# #         # Map our language enum to Google's language codes
# #         language_code_map = {
# #             Language.ENGLISH: "en-US",
# #             Language.SPANISH: "es-ES",
# #             Language.TAGALOG: "fil-PH"
# #         }

# #         # Join findings into a single text
# #         text = " ".join(query.findings)

# #         # Configure TTS request
# #         input_text = texttospeech.SynthesisInput(text=text)
# #         voice = texttospeech.VoiceSelectionParams(
# #             language_code=language_code_map[user_language],
# #             ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
# #         )
# #         audio_config = texttospeech.AudioConfig(
# #             audio_encoding=texttospeech.AudioEncoding.MP3
# #         )

# #         # Generate audio
# #         response = client.synthesize_speech(
# #             input=input_text,
# #             voice=voice,
# #             audio_config=audio_config
# #         )

# #         # Create a BytesIO object from the audio content
# #         audio_bytes = io.BytesIO(response.audio_content)

# #         # Function to stream the file
# #         def iterfile():
# #             yield from audio_bytes

# #         # Return streaming response
# #         return StreamingResponse(
# #             iterfile(),
# #             media_type="audio/mpeg",
# #             headers={
# #                 "Accept-Ranges": "bytes",
# #                 "Content-Disposition": f"inline; filename=tts_{query_id}.mp3"
# #             }
# #         )

# #     except Exception as e:
# #         logger.error(f"TTS Error: {e}")
# #         raise HTTPException(status_code=500, detail="Error generating audio")
