from fastapi import APIRouter
from apps.core import router

apps_router = APIRouter()
apps_router.include_router(router,tags=["auth"])