import os
import tiktoken
import json
from openai import AsyncOpenAI
from app.config import logger, ENV_VARS

GPT_APIKEY = ENV_VARS["GPT_APIKEY"]
GPT_MODEL_NAME = ENV_VARS["GPT_MODEL_NAME"]


# Context and Response Token size can be adjusted according to business requirements 
MAX_CONTEXT_SIZE = 7000 
MAX_RESPONSE_TOKENS = 2000

openAIClient = AsyncOpenAI(
  api_key= GPT_APIKEY,
)

# Code snippet borrowed from : https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        logger.warning("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        logger.warning("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


async def generate_response(query='', alerts = [], user_info = ''):
    config = {
        "model": GPT_MODEL_NAME,
        "temperature": 0,
        "response_format": { "type": "json_object" },
        "max_tokens": MAX_RESPONSE_TOKENS
    }

    context = ''
    for alert in alerts:
        context += f"Event: {alert['event']}; Headline: {alert['headline']}; Description: {alert['description']}; Instruction: {alert['instruction']}\n"

    messages = [
            {
                "role": "system",
                "content": "You are a highly skilled AI tasked with analyzing Weather alerts and giving users advice based on their Age and health in json format. Given a user's question, their details, and weather info, your role involves identifying the most reasonable advice to give them about their query. If no answers are possible for the question-query, simply return empty array of facts'. Example= {'facts':['The weather is good','It is safe to go out']}. Try to answer in their preferred language of choice. If not available, English works"                
            }, 
            {
                "role": "user",
                "content": "\nQuestion: " + query + "\nContext: \n" + context + "\nUser Details: \n" + user_info
            }
    ]
    
    try :
        num_tokens = num_tokens_from_messages(messages, model=GPT_MODEL_NAME)
        logger.info(f"Number of tokens in LLM prompt: {num_tokens}")
        if num_tokens > MAX_CONTEXT_SIZE - config['max_tokens']: # To control the input text size
            return {
                "status" : "error",
                "facts" : ["Sorry, that's too much text for me to process. Can you reduce the number of attached files and try again?"]
            }
        response = await getLLMResponse(messages, config)
        logger.info(f"GPT Response: {response}")
        
    except Exception as e:
        logger.error(e)
        return {
            "status" : "error",
            "facts" : ["Sorry, I'm having some trouble answering your question. Please contact support"]
        }

    if(response):
        try:
            response = json.loads(response)
            response['status'] = 'success'
            return response
        except:
            return {
            "status" : "error",
            "facts" : ["Sorry, I'm having some trouble answering your question. Please contact support"]
        }

    return {
            "status" : "error",
            "facts" : ["Sorry, I'm having some trouble answering your question. Please contact support"]
        }

async def getLLMResponse(messages, config):
    response = await openAIClient.chat.completions.create(
        model=config['model'],
        temperature=config['temperature'],
        messages=messages,
        response_format={ "type": "json_object" },
        max_tokens=config['max_tokens']
    )
    return response.choices[0].message.content

