import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Adjust import paths
from .core.config import settings
from .api.api import api_router
# Import model to ensure DB initialization runs on startup
from .models import user_model

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for managing users and authentication.",
    # Add other FastAPI configurations as needed
)

# Configure CORS (allow all for simplicity, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME}

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    # Note: Running directly like this is for development.
    # Production deployments often use Gunicorn + Uvicorn workers.
    # The host '0.0.0.0' makes it accessible on the network.
    # Default port 8001 to avoid conflict with analytics service (assumed 8000).
    # Use "main:app" when running the script directly.
    # The command line 'uvicorn user-management.src.main.main:app ...' works because
    # uvicorn handles the path resolution from the project root.
    uvicorn.run(
        "main:app", # Correct reference when running this script directly
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG # Enable reload if DEBUG is True
    ) 