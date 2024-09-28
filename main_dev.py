import ast
import os
import signal
import subprocess
import sys
import threading

import uvicorn
from fastapi import FastAPI
from loguru import logger as log
from sqlalchemy import create_engine
from testcontainers.core.image import DockerImage
from testcontainers.postgres import PostgresContainer

# import misc.scripts.app.create_default_scenario_toolkits as toolkit_script
from informed.config import get_config
from informed.db import upgrade_db
from main import create_default_app


def strtobool(val):
    return val.lower() in ("y", "yes", "t", "true", "on", "1")


def _run_upgrade(db_connection_string: str):
    engine = create_engine(db_connection_string)
    with engine.begin() as conn:
        upgrade_db(conn)


def signal_handler(signum, frame):
    log.info("Received termination signal. Cleaning up...")
    sys.exit(0)


def run_informed_server(app: FastAPI, host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_config=None, log_level="debug")


def run_ui():
    ui_dir = os.path.join(os.getcwd(), "frontend")
    log.info("Starting UI in directory: {}", ui_dir)
    try:
        subprocess.run(["npm", "run", "dev"], cwd=ui_dir, check=True)  # noqa: S603
    except subprocess.CalledProcessError as e:
        log.error("Failed to start UI: {}", str(e))
    except FileNotFoundError:
        log.error("npm command not found. Make sure Node.js and npm are installed.")


def start_server(db_connection_string: str) -> None:
    # Replace strtobool with ast.literal_eval
    start_ui_flag = bool(strtobool(os.environ.get("USER_START_UI", "true")))
    enable_auth = bool(strtobool(os.environ.get("ENABLE_AUTH", "false")))

    if enable_auth:
        os.environ["AUTH_CONFIG__WORKOS_CONFIG__REDIRECT_URI"] = (
            "http://localhost:3001/api/v1/auth/callback"
        )
        os.environ["AUTH_CONFIG__WORKOS_CONFIG__ORGANIZATION_ID"] = (
            "org_01J2STQ7C69GYJZJMNB8D6MGGQ"
        )
    else:
        os.environ["AUTH_CONFIG__AUTH_MODE"] = "SUPERUSER"
        os.environ["AUTH_CONFIG__WORKOS_CONFIG__REDIRECT_URI"] = "dummy"
        os.environ["AUTH_CONFIG__WORKOS_CONFIG__ORGANIZATION_ID"] = "dummy"

    _run_upgrade(db_connection_string)
    print(f"db_connection_string: {db_connection_string}")

    config = get_config(print_config=True)

    config.logging_config.level = "DEBUG"
    config.logging_config.enable_console = True
    app = create_default_app(config)

    host = "127.0.0.1"
    port = 3001

    ui_thread = None

    try:
        # Start the server in a separate thread
        log.info("Starting server on {}:{}", host, port)
        server_thread = threading.Thread(
            target=run_informed_server, args=(app, host, port)
        )
        server_thread.start()

        # log.info("Server thread started. API URL: {}", api_url)

        # Start UI in a separate thread
        if start_ui_flag:
            log.info("Starting UI...")
            ui_thread = threading.Thread(target=run_ui)
            ui_thread.start()

        # Keep the main thread alive
        server_thread.join()

    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        if ui_thread is not None:
            log.info("Waiting for UI thread to finish...")
            ui_thread.join(timeout=5)

        log.info("Exiting...")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    db_connection_string = os.getenv("DATABASE_CONFIG__DB_URL")

    # If DATABASE_CONFIG__DB_URL is not provided, create a new DB
    if db_connection_string is None:
        try:
            with DockerImage(path="misc/images/pgvector") as image, PostgresContainer(
                "postgres:latest", driver="psycopg"
            ).with_bind_ports(5432, 5432).with_env(
                "POSTGRES_POSTGRES_PASSWORD", "password"
            ).with_env(
                "POSTGRES_INITSCRIPTS_PASSWORD", "password"
            ).with_env(
                "POSTGRES_INITSCRIPTS_USERNAME", "postgres"
            ) as postgres:

                db_connection_string = postgres.get_connection_url()
                os.environ["DATABASE_CONFIG__DB_URL"] = db_connection_string
                start_server(db_connection_string)
        except Exception as e:
            log.error("Failed to start server: {}", str(e))
            sys.exit(1)
    else:
        start_server(db_connection_string)
