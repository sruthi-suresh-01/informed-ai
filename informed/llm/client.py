import json
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import Function
from informed.config import LLMConfig
from informed.llm.llm import ChatState


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config: LLMConfig = config
        if not config.openai_config:
            raise ValueError("OpenAI config not found")
        self.client = AsyncOpenAI(
            api_key=config.openai_config.api_key,
        )

    async def chat_completion(
        self, chat_state: ChatState, tools: list[Any], max_tokens: int | None = None
    ) -> Function:
        response = await self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=chat_state.messages,
            temperature=self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
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
