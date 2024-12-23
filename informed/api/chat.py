from typing import cast, Any

from fastapi import APIRouter, HTTPException, Request, Response
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address


from informed.helper.utils import UserDep
from informed.api.schema import ChatRequest, AddUserMessageRequest, ChatResponse
from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core import client_options
import os
from fastapi.responses import StreamingResponse
import io
from informed.informed import InformedManager
from uuid import UUID
from informed.db_models.users import Language

router = APIRouter()


# Create a Limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=ChatResponse)
async def create_chat(
    chat_request: ChatRequest, request: Request, user: UserDep
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        chat_thread = await app_manager.start_new_chat_thread(
            chat_request, user.user_id
        )
        chat_thread = await app_manager.get_chat(chat_thread.chat_thread_id)
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}") from e


@router.post("/{chat_thread_id}", response_model=ChatResponse)
async def add_user_message(
    add_user_message_request: AddUserMessageRequest,
    user: UserDep,
    request: Request,
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        await app_manager.add_user_message(add_user_message_request, user.user_id)
        chat_thread_id = add_user_message_request.chat_thread_id
        chat_thread = await app_manager.get_chat(chat_thread_id)
        if chat_thread is None:
            raise HTTPException(
                status_code=404, detail=f"chat thread {chat_thread_id} not found"
            )
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected error: {e}") from e


@router.get("/{chat_thread_id}", response_model=ChatResponse)
async def get_chat(
    chat_thread_id: UUID,
    _: UserDep,
    request: Request,
) -> ChatResponse:
    app_manager = cast(InformedManager, request.app.state.app_manager)
    try:
        chat_thread = await app_manager.get_chat(chat_thread_id)
        chat_response = ChatResponse.from_chat_thread(chat_thread)
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected error: {e!s}") from e


@router.get("/tts/{message_id}")
async def get_query_tts(
    message_id: UUID, request: Request, current_user: UserDep
) -> Any:
    # Validate API key exists
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Google API key not configured")

    # Create async client
    options = client_options.ClientOptions(api_key=api_key)
    client = texttospeech.TextToSpeechAsyncClient(client_options=options)

    app_manager = request.app.state.app_manager
    try:
        # Get message
        message = await app_manager.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Get user's preferred language
        user_language = (
            current_user.details.language if current_user.details else Language.ENGLISH
        )

        language_code_map = {
            Language.ENGLISH: "en-US",
            Language.SPANISH: "es-ES",
            Language.TAGALOG: "fil-PH",
        }

        # Configure TTS request
        input_text = texttospeech.SynthesisInput(text=message.content)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code_map[user_language],
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Generate audio asynchronously
        response = await client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        # Return the audio content directly
        return Response(
            content=response.audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"inline; filename=tts_{message_id}.mp3"},
        )

    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating audio")
