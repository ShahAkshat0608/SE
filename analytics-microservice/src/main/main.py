from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .config.settings import settings

# Import the unified API router
from .api import api_router

# Create FastAPI app
app = FastAPI(
    title="Analytics Microservice",
    description="Analytics API for task management system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, limit this to specific frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unified router with the API prefix
app.include_router(
    api_router,
    prefix=settings.API_PREFIX
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-microservice"}

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Analytics Microservice",
        "version": "0.1.0",
        "endpoints": {
            "user_analytics": f"{settings.API_PREFIX}/user",
            "team_analytics": f"{settings.API_PREFIX}/team",
            "project_analytics": f"{settings.API_PREFIX}/project",
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=settings.DEBUG)