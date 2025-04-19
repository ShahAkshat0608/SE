import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Fix import to be relative when run from this directory or absolute when run from project root
try:
    from api.api import api_router
    from utils.env_loader import load_env_variables
except ImportError:
    from src.main.api.api import api_router
    from src.main.utils.env_loader import load_env_variables

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_env_variables()

app = FastAPI(
    title="Notification Microservice",
    description="Microservice for sending email notifications and managing Google Calendar events",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/", tags=["root"])
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Notification Microservice API",
        "docs": "/docs",
        "endpoints": {
            "email": "/notifications/email",
            "calendar": "/notifications/calendar"
        }
    }

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    # Check required environment variables
    env_vars = {
        "EMAIL_USERNAME": os.environ.get("EMAIL_USERNAME"),
        "EMAIL_PASSWORD": os.environ.get("EMAIL_PASSWORD"),
        "GOOGLE_CREDENTIALS_FILE": os.path.exists(
            os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        )
    }
    
    # Check if email credentials are set
    is_email_ready = bool(env_vars["EMAIL_USERNAME"] and env_vars["EMAIL_PASSWORD"])
    
    # Check if Google Calendar API credentials are available
    is_calendar_ready = env_vars["GOOGLE_CREDENTIALS_FILE"]
    
    return {
        "status": "healthy",
        "services": {
            "email": "ready" if is_email_ready else "not_configured",
            "calendar": "ready" if is_calendar_ready else "not_configured" 
        },
        "environment": env_vars
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))  # Use port 8002 as default for notification service
    # Use the full module path for reliability
    module_path = "src.main.main:app"
    # When running directly from src/main directory, use local path
    if os.path.basename(os.getcwd()) == "main":
        module_path = "main:app"
    uvicorn.run(module_path, host="0.0.0.0", port=port, reload=True) 