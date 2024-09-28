import os
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger as log

from informed.api.user_query_routes import user_query_router
from informed.api.user_routes import user_router
from informed.api.weather_data_routes import weather_router
from informed.config import Config
from informed.db import init_db
from informed.helper.utils import get_concise_exception_traceback


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    try:
        # Startup logic
        log.info("Initializing resources...")
        # Add any initialization code here

        executor = ThreadPoolExecutor(max_workers=4)
        app.state.executor = executor

        yield
    finally:
        # Shutdown logic
        log.info("Shutting down resources...")
        # Close the executor if it exists
        if hasattr(app.state, "executor"):
            app.state.executor.shutdown(wait=True)
            log.info("Executor has been shut down")
        # Add any other cleanup code here


def create_app(config: Config) -> FastAPI:
    # Initialize the database
    init_db(config.database_config)
    # Initialize the job scheduler
    # app = FastAPI(lifespan=lifespan)
    app = FastAPI()
    # app.mount("/files", StaticFiles(directory="static"), name="static")
    app.state.config = config
    app.state.version = os.getenv("APP_VERSION")

    # Initialize the job scheduler

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_v1_router = APIRouter()
    api_v1_router.include_router(user_router, prefix="/user", tags=["users"])
    api_v1_router.include_router(user_query_router, prefix="/query", tags=["query"])
    api_v1_router.include_router(weather_router, prefix="/weather", tags=["weather"])

    # TODO: Frontend needs to update api version in its path
    app.include_router(api_v1_router, prefix="/api/v1")

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app


def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
        headers = exc.headers
    else:
        status_code = 500
        detail = "Internal Server Error"
        headers = None

    error_response = {
        "detail": detail,
        "status_code": status_code,
        "type": (
            "HTTPException" if isinstance(exc, HTTPException) else type(exc).__name__
        ),
        "headers": dict(headers) if headers else None,
        "path": request.url.path,
        "method": request.method,
    }

    log.error(
        "HTTP exception occurred: {}, exception: {}",
        error_response,
        get_concise_exception_traceback(exc),
    )

    return JSONResponse(status_code=status_code, content=error_response)


def general_exception_handler(request: Request, exception: Exception) -> Response:
    error_response = {
        "detail": "An unexpected error occurred. Please try again later.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "type": type(exception).__name__,
        "path": request.url.path,
        "method": request.method,
    }

    log.error(
        "unhandled exception occurred: {}, exception: {}",
        error_response,
        get_concise_exception_traceback(exception),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response
    )
