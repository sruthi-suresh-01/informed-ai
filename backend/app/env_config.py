import logging
import os

APP_ENV = os.getenv("APP_ENV", "DEV")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER_NAME = os.getenv("DB_SERVER_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE_NAME = os.getenv("DB_DATABASE_NAME")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:toor@localhost:5432/Informed")

GPT_APIKEY = os.getenv("GPT_APIKEY", "")
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME", "gpt-3.5-turbo")

ENV_VARS = {
    "DB_USERNAME": DB_USERNAME,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_SERVER_NAME": DB_SERVER_NAME,
    "DB_PORT": DB_PORT,
    "DB_DATABASE_NAME": DB_DATABASE_NAME,
    "DB_URL": DB_URL,
    "APP_ENV": APP_ENV,
    "GPT_APIKEY": GPT_APIKEY,
    "GPT_MODEL_NAME": GPT_MODEL_NAME,
}
