from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.user_routes import router as user_router
from api.team_routes import router as team_router
from api.project_routes import router as project_router
from config.settings import settings

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

# Include routers with prefixes
app.include_router(
    user_router,
    prefix=f"{settings.API_PREFIX}/user",
    tags=["User Analytics"]
)

app.include_router(
    team_router,
    prefix=f"{settings.API_PREFIX}/team",
    tags=["Team Analytics"]
)

app.include_router(
    project_router,
    prefix=f"{settings.API_PREFIX}/project",
    tags=["Project Analytics"]
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)