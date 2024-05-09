from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import ENV_VARS

DB_USERNAME = ENV_VARS["DB_USERNAME"]
DB_PASSWORD = ENV_VARS["DB_PASSWORD"]
DB_SERVER_NAME = ENV_VARS["DB_SERVER_NAME"]
DB_PORT = ENV_VARS["DB_PORT"]
DB_DATABASE_NAME = ENV_VARS["DB_DATABASE_NAME"]
DB_URL = ENV_VARS["DB_URL"]


# Syntax is postgresql://<username>:<password>@<db_server>:<postgres_port>/<db_name>
URL_DATABASE=DB_URL
# URL_DATABASE = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DATABASE_NAME}"

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()