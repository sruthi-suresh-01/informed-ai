import asyncio
import os
import signal
import subprocess
import sys
import threading
import shutil

# Looks ugly but apparently there is some issue with asyncio event loop on Windows
# and the solution is to set a different event loop policy at the beginning of code execution
# Best to look for an alternate solution, but since this is a file that is only
# meant for running the app locally, we can keep this for now
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI
from loguru import logger as log
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from informed.config import get_config
from informed.db import upgrade_db
from main import create_default_app


# def strtobool(val):
#     return val.lower() in ("y", "yes", "t", "true", "on", "1")


def safe_strtobool(value: str) -> bool:
    """Safely convert a string to a boolean."""
    value = value.lower().strip()
    if value in ("y", "yes", "true", "t", "1"):
        return True
    elif value in ("n", "no", "false", "f", "0"):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


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
        npm_path = shutil.which("npm")
        if not npm_path:
            log.error("npm not found in PATH. Make sure Node.js and npm are installed.")
            return
        subprocess.run([npm_path, "run", "start"], cwd=ui_dir, check=True)
    except subprocess.CalledProcessError as e:
        log.error("Failed to start UI: {}", str(e))
    except FileNotFoundError:
        log.error("npm command not found. Make sure Node.js and npm are installed.")


def start_server(db_connection_string: str) -> None:
    # Replace strtobool with ast.literal_eval
    start_ui_flag = bool(strtobool(os.environ.get("USER_START_UI", "true")))

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

    try:
        with RedisContainer(image="redis:latest") as redis_container:
            redis_container.start()
            redis_host = redis_container.get_container_host_ip()
            redis_port = redis_container.get_exposed_port(6379)
            os.environ["REDIS_CONFIG__HOST"] = redis_host
            os.environ["REDIS_CONFIG__PORT"] = redis_port
            log.info("Redis container started on port {}", redis_port)

            if db_connection_string is None:
                with PostgresContainer(
                    "postgres:latest", driver="psycopg"
                ).with_bind_ports(5432, 5433) as postgres:
                    db_connection_string = postgres.get_connection_url()
                    os.environ["DATABASE_CONFIG__DB_URL"] = db_connection_string
                    start_server(db_connection_string)
            else:
                start_server(db_connection_string)
    except Exception as e:
        log.error("Failed to start server: {}", str(e))
