from fastapi import APIRouter
from .user_routes import user_router
from .user_query_routes import user_query_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/user", tags=["users"])
api_router.include_router(user_query_router, prefix="/query", tags=["query"])
