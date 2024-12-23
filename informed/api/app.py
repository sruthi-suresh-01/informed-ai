import os
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger as log
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# from informed.api.chat_query import chat_query_router
from informed.api.chat import router as chat_router
from informed.api.user import user_router
from informed.api.weather import weather_router
from informed.api.health import router as health_router
from informed.api.admin import admin_router
from informed.config import Config
from informed.db import init_db
from informed.redis import init_redis_client
from informed.helper.utils import get_concise_exception_traceback
from informed.informed import InformedManager
from informed.llm.client import LLMClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    try:
        # Startup logic
        log.info("Initializing resources...")
        # Add any initialization code here

        yield

        await app.state.app_manager.cancel_all_tasks()
        if hasattr(app.state, "executor"):
            app.state.executor.shutdown(wait=True)
        log.info("Executor has been shut down")
    except Exception as e:
        log.exception(e)
        raise e


def create_app(config: Config) -> FastAPI:
    log.info("Creating app...")
    # Initialize the database
    init_db(config.database_config)
    redis_client = init_redis_client(config.redis_config)
    # Initialize the job scheduler
    app = FastAPI(lifespan=lifespan)
    # app.mount("/files", StaticFiles(directory="static"), name="static")
    app.state.config = config
    app.state.version = os.getenv("APP_VERSION")

    app.state.redis_client = redis_client

    executor = ThreadPoolExecutor(max_workers=4)
    app.state.executor = executor

    llm_client = LLMClient(config.llm_config)
    app.state.llm_client = llm_client

    app_manager = InformedManager(config, llm_client, redis_client)
    app.state.app_manager = app_manager

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
    api_v1_router.include_router(chat_router, prefix="/chat", tags=["chat"])
    # api_v1_router.include_router(chat_query_router, prefix="/query", tags=["query"])
    api_v1_router.include_router(weather_router, prefix="/weather", tags=["weather"])
    api_v1_router.include_router(health_router, prefix="/health", tags=["health"])
    api_v1_router.include_router(admin_router, prefix="/admin", tags=["admin"])

    app.include_router(api_v1_router, prefix="/api/v1")

    # Create a Limiter instance with a global rate limit
    limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

    # Add the rate limit middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


def _rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    """
    Build a simple JSON response that includes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    if isinstance(exc, RateLimitExceeded):
        response = JSONResponse(
            {"error": f"Rate limit exceeded: {exc.detail}"}, status_code=429
        )
        response = request.app.state.limiter._inject_headers(
            response, request.state.view_rate_limit
        )
        return response
    # Handle other exceptions if necessary
    return JSONResponse({"error": "An unexpected error occurred."}, status_code=500)
