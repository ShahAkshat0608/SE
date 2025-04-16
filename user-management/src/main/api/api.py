from fastapi import APIRouter

from .endpoints import user_auth

api_router = APIRouter()

# Include routers from endpoint modules
api_router.include_router(user_auth.router, prefix="/auth", tags=["Authentication"])

# Add other routers here if needed (e.g., for user profile management) 