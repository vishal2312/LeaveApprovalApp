
from fastapi import APIRouter
from api.controller import router

api_router = APIRouter()
api_router.include_router(router,tags=["auth"])
