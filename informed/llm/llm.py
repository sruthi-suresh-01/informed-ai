from typing import Any
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import tiktoken
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel
from informed.config import ENV_VARS
from informed.db_models.query import QuerySource
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import Function

GPT_APIKEY = ENV_VARS["GPT_APIKEY"]
GPT_MODEL_NAME = ENV_VARS["GPT_MODEL_NAME"]


# Context and Response Token size can be adjusted according to business requirements
MAX_CONTEXT_SIZE = 7000
MAX_RESPONSE_TOKENS = 150


openAIClient = AsyncOpenAI(
    api_key=GPT_APIKEY,
)


class GPTConfig(BaseModel):
    model: str
    temperature: float = 0.0
    response_format: str = "json"
    max_tokens: int = MAX_RESPONSE_TOKENS


class ChatState:
    def __init__(self, system_prompt: str, user_prompt: str):
        self.messages: list = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
        self.retry_count: int = 0  # Initialize retry count

    def append_message(self, message: Any) -> None:
        # log.info("appending {}", message)
        self.messages.append(message)


async def getLLMResponse(messages: Any, tools: list[Any]) -> Function:
    config = GPTConfig(
        model=GPT_MODEL_NAME,
        temperature=0,
        max_tokens=MAX_RESPONSE_TOKENS,
    )
    response = await openAIClient.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        tools=tools,
    )
    if (
        response
        and response.choices
        and isinstance(response.choices[0], Choice)
        and response.choices[0].message
        and response.choices[0].message.tool_calls
    ):
        function: Function = response.choices[0].message.tool_calls[0].function

        return function
    else:
        raise Exception("No function call found in the response")
