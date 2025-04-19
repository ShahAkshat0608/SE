#!/usr/bin/env python
import os
import smtplib
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Email configuration - use the same settings as the notification service
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Read credentials from .env file if available, otherwise use environment variables
def load_credentials_from_env_file():
    """Load credentials from .env file."""
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir
    
    # Try different possible locations for the .env file
    possible_paths = [
        current_dir / '.env',
        project_root / 'notification-microservice' / '.env',
        Path('notification-microservice') / '.env',
        Path('notification-microservice/.env'),
        Path('.env')
    ]
    
    for env_path in possible_paths:
        logger.debug(f"Checking for .env file at: {env_path}")
        if env_path.exists():
            logger.info(f"Found .env file at: {env_path}")
            try:
                with open(env_path, 'r') as f:
                    logger.info(f"Loading credentials from {env_path}")
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                            logger.debug(f"Loaded environment variable: {key}")
                return True
            except Exception as e:
                logger.error(f"Error loading .env file {env_path}: {e}")
    
    logger.error("No valid .env file found in any of the expected locations.")
    return False

# Try to load from .env file first
load_credentials_from_env_file()

# Get credentials from environment
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Print environment vars we found
logger.info(f"Found EMAIL_USERNAME: {EMAIL_USERNAME}")
logger.info(f"Found EMAIL_PASSWORD: {'*****' if EMAIL_PASSWORD else 'Not found'}")

def test_smtp_connection():
    """Test direct SMTP connection to Gmail."""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logger.error("Email credentials not set in environment variables or .env file")
        return False

    logger.info(f"Testing SMTP connection for {EMAIL_USERNAME}")
    logger.info(f"Credentials present: Username={bool(EMAIL_USERNAME)}, Password={bool(EMAIL_PASSWORD)}")

    try:
        logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        logger.info("Attempting to login...")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        logger.info("Login successful!")
        
        server.quit()
        logger.info("SMTP connection closed")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {e}")
        logger.error("This usually means incorrect username/password or Google security settings blocking the login.")
        logger.error("Check if 'Less secure app access' is enabled or use an App Password.")
        return False
    except Exception as e:
        logger.error(f"SMTP Connection Error: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        return False

def send_test_email(to_email="test@example.com"):
    """Send a test email via SMTP directly."""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logger.error("Email credentials not set in environment variables or .env file")
        return False

    logger.info(f"Sending test email from {EMAIL_USERNAME} to {to_email}")

    message = MIMEMultipart()
    message["From"] = EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = "Test Email - Direct SMTP"
    
    body = """
    This is a test email sent directly via SMTP.
    If you're receiving this, the SMTP connection is working correctly.
    """
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        logger.info("Sending email message...")
        server.send_message(message)
        logger.info("Email message sent")
        
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    logger.info("Starting direct SMTP test...")
    
    if test_smtp_connection():
        logger.info("SMTP connection test successful!")
        
        # Prompt user for email address for test email
        recipient = input("Enter your email address to receive a test email (or press Enter to skip): ").strip()
        
        if recipient:
            if send_test_email(recipient):
                logger.info(f"Test email sent successfully to {recipient}!")
            else:
                logger.error("Failed to send test email.")
        else:
            logger.info("Test email sending skipped.")
    else:
        logger.error("SMTP connection test failed.") 