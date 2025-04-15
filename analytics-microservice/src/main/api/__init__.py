# In api/__init__.py
from fastapi import APIRouter

from .project_routes import router as project_router
from .team_routes import router as team_router
from .user_routes import router as user_router

# Create a unified router
api_router = APIRouter()

# Include all analytics routes with appropriate prefixes
api_router.include_router(
    project_router,
    prefix="/project",
    tags=["Project Analytics"]
)

api_router.include_router(
    team_router,
    prefix="/team",
    tags=["Team Analytics"]
)

api_router.include_router(
    user_router,
    prefix="/user",
    tags=["User Analytics"]
)