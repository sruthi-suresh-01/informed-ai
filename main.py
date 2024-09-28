import uvicorn
from fastapi import FastAPI

from informed.api.app import create_app
from informed.config import Config, get_config
from informed.logger.logger import setup_logger


def create_default_app(config: Config | None = None) -> FastAPI:
    config = config or get_config(print_config=True)
    setup_logger(config)
    app = create_app(config)
    return app


if __name__ == "__main__":
    app = create_default_app()
    uvicorn.run(app, host="0.0.0.0", port=3001, log_config=None, log_level="info")
