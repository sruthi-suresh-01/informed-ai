import os
import logging
from concurrent.futures import ThreadPoolExecutor

APP_ENV = os.getenv("APP_ENV", "DEV")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER_NAME = os.getenv("DB_SERVER_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE_NAME = os.getenv("DB_DATABASE_NAME")
DB_URL = os.getenv("DB_URL")

GPT_APIKEY = os.getenv("GPT_APIKEY")
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME", "gpt-3.5-turbo")

ENV_VARS = {
    "DB_USERNAME" : DB_USERNAME,
    "DB_PASSWORD" : DB_PASSWORD,
    "DB_SERVER_NAME" : DB_SERVER_NAME,
    "DB_PORT" : DB_PORT,
    "DB_DATABASE_NAME" : DB_DATABASE_NAME,
    "DB_URL" : DB_URL,
    "APP_ENV" : APP_ENV,
    "GPT_APIKEY" : GPT_APIKEY,
    "GPT_MODEL_NAME" : GPT_MODEL_NAME,

}

def setup_logger():
    logging.basicConfig(level=logging.INFO if APP_ENV == "DEV" else logging.WARNING)
    logger = logging.getLogger(__name__)
    return logger

# Initialize the logger
logger = setup_logger()


executor = ThreadPoolExecutor(max_workers=4)


