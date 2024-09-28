from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.app.env_config import ENV_VARS

DB_USERNAME = ENV_VARS["DB_USERNAME"]
DB_PASSWORD = ENV_VARS["DB_PASSWORD"]
DB_SERVER_NAME = ENV_VARS["DB_SERVER_NAME"]
DB_PORT = ENV_VARS["DB_PORT"]
DB_DATABASE_NAME = ENV_VARS["DB_DATABASE_NAME"]
DB_URL = ENV_VARS["DB_URL"]
