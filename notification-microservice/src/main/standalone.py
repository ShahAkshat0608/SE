import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Try to import env_loader with either relative or absolute imports
try:
    from utils.env_loader import load_env_variables
except ImportError:
    try:
        from src.main.utils.env_loader import load_env_variables
    except ImportError:
        # Define a simple version if all imports fail
        def load_env_variables():
            logging.warning("Using fallback environment loader")
            return False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_env_variables()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

app = FastAPI(
    title="Email Notification Service",
    description="Simple microservice for sending email notifications via Gmail",
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

router = APIRouter()

def send_email(to_email, subject, body):
    """Send an email using Gmail SMTP."""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logging.error("Email credentials not set in environment variables")
        return False

    message = MIMEMultipart()
    message["From"] = f"Task Management System <{EMAIL_USERNAME}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add headers to improve deliverability
    message["X-Priority"] = "1"  # High priority
    message["X-MSMail-Priority"] = "High"
    message["Importance"] = "High"
    message["X-Mailer"] = "Task Management System"
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Create a secure connection with the server using SSL
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        # Login to email account
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Send email
        server.send_message(message)
        
        # Terminate the session
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        return False

@router.post("/email", status_code=status.HTTP_200_OK)
def send_email_notification(to_email: str, subject: str, body: str):
    """Send an email notification."""
    success = send_email(to_email, subject, body)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
    
    return {"message": f"Email sent successfully to {to_email}"}

@app.get("/", tags=["root"])
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Email Notification Service",
        "docs": "/docs",
        "endpoints": {
            "email": "/notifications/email"
        }
    }

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    is_email_ready = bool(EMAIL_USERNAME and EMAIL_PASSWORD)
    
    return {
        "status": "healthy",
        "services": {
            "email": "ready" if is_email_ready else "not_configured"
        },
        "environment": {
            "EMAIL_USERNAME": EMAIL_USERNAME is not None,
            "EMAIL_PASSWORD": EMAIL_PASSWORD is not None
        }
    }

# Include API router
app.include_router(router, prefix="/notifications", tags=["notifications"])

if __name__ == "__main__":
    # Print startup information
    print(f"Email configured for: {EMAIL_USERNAME}")
    
    # Run the service
    uvicorn.run("standalone:app", host="0.0.0.0", port=8002, reload=True) 