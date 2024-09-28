import argparse
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

from informed.db_models import (  # noqa: F401
    Activity,
    Language,
    User,
    UserDetails,
    UserLanguage,
    UserMedicalDetails,
)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--message", help="Migration message", type=str)
    args = parser.parse_args()

    with PostgresContainer("postgres:latest", driver="psycopg").with_bind_ports(
        5432, 5432
    ).with_env("POSTGRES_POSTGRES_PASSWORD", "password").with_env(
        "POSTGRES_INITSCRIPTS_PASSWORD", "password"
    ).with_env(
        "POSTGRES_INITSCRIPTS_USERNAME", "postgres"
    ) as postgres:
        connection_string = postgres.get_connection_url()
        os.environ["DB_URL"] = connection_string
        engine = create_engine(connection_string)
        with engine.begin() as conn:
            conf = Config("alembic.ini")
            conf.attributes["connection"] = conn
            command.upgrade(conf, "head")
            command.revision(conf, message=args.message, autogenerate=True)
