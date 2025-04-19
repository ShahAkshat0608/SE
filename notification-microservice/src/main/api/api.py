from fastapi import APIRouter
from src.main.api.endpoints import notification

api_router = APIRouter()

api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"]) 