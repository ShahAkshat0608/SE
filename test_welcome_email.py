#!/usr/bin/env python
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path so we can import the modules
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import the necessary functions
try:
    from user_management.src.main.services.notification_client import send_welcome_email
    logger.info("Successfully imported send_welcome_email function")
except ImportError as e:
    logger.error(f"Failed to import send_welcome_email: {e}")
    # Try an alternative import path
    try:
        import sys
        sys.path.append("user-management")
        from src.main.services.notification_client import send_welcome_email
        logger.info("Successfully imported send_welcome_email via alternative path")
    except ImportError as e:
        logger.error(f"Alternative import also failed: {e}")
        sys.exit(1)

def test_welcome_email():
    """Test sending a welcome email directly."""
    user_id = 9999  # Test user ID
    email = input("Enter your email address to receive a test welcome email: ").strip()
    name = "Test User"
    
    logger.info(f"Attempting to send welcome email to {email}")
    
    try:
        result = send_welcome_email(user_id, email, name)
        
        if result:
            logger.info(f"Welcome email sent successfully: {result}")
            return True
        else:
            logger.error("Failed to send welcome email - function returned None")
            return False
    except Exception as e:
        logger.error(f"Exception while sending welcome email: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    logger.info("Starting welcome email test...")
    if test_welcome_email():
        logger.info("Welcome email test completed successfully!")
    else:
        logger.error("Welcome email test failed!") 