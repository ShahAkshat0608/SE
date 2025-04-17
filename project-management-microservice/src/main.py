import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer
from fastapi.openapi.models import APIKey
from fastapi.openapi.models import SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi import Security

from datetime import datetime, timedelta
from typing import Dict
import os

from .utils.auth_token_gen import create_access_token 
from .services.clients.user_management_client import APIClient
from .api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("project-management")

# Create FastAPI app
app = FastAPI(
    title="Project Management API",
    description="API for role-based project management system",
    version="1.0.0"
)

# Create API client for user management service
user_client = APIClient(base_url="http://localhost:8000")

# Configure CORS for frontend access
origins = [
    "http://localhost:3000",  # React frontend
    "http://localhost:8000",  # Development server
    "http://localhost:8080",  # Alternative development port
    "*",  # For development - remove in production!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Authentication routes directly in main.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Project Management API",
        version="1.0.0",
        description="API for role-based project management system",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if "security" not in openapi_schema["paths"][path][method]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# @app.post("/api/auth/login", response_model=Dict)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     """
#     OAuth2 compatible token endpoint for user login that delegates to user management service
#     """
#     # Call the user management service to authenticate the user
#     print("Form data:", form_data)
#     auth_response = user_client.login_user(form_data.username, form_data.password)
    
#     # Check if there was an error in the response
#     if "error" in auth_response:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=auth_response.get("detail", "Authentication failed"),
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # User management service validated the user
#     user = auth_response.get("user", {})
    
#     # Use token from user management service if provided, otherwise create our own
#     if "access_token" in auth_response:
#         access_token = auth_response["access_token"]
#     else:
#         # Create access token with 30-day expiry (adjust as needed)
#         access_token_expires = timedelta(days=30)
#         access_token = create_access_token(
#             data={"sub": user["id"], "username": user.get("email")},
#             # expires_delta=access_token_expires
#         )
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": {
#             "id": user.get("id"),
#             "name": user.get("name"),
#             "email": user.get("email"),
#             "role": user.get("role", "user")  # Include role if provided
#         }
#     }

@app.post("/api/auth/register", response_model=Dict)
async def register_user(name: str, email: str, password: str, contact: str = None):
    """
    Register a new user using the user management service
    """
    register_response = user_client.register_user(name, email, password, contact)
    
    if "error" in register_response:
        status_code = 400
        if register_response["error"] == "Conflict":
            status_code = 409
        
        raise HTTPException(
            status_code=status_code,
            detail=register_response.get("detail", "Registration failed")
        )
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": register_response
    }

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running
    """
    return {
        "message": "Project Management API",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """
    Execute tasks when the application starts
    """
    logger.info("Starting Project Management microservice")
    # Add any database connection or initialization here
    # Example: await database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute tasks when the application shuts down
    """
    logger.info("Shutting down Project Management microservice")
    # Close database connections or perform cleanup here
    # Example: await database.disconnect()

if __name__ == "__main__":
    # Run the application with uvicorn
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",  # Change this if your import path differs
            host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )