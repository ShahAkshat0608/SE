"""
Load environment variables from .env file.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_env_variables():
    """
    Load environment variables from .env file located in the notification-microservice root.
    Maps EMAIL_ADDRESS to EMAIL_USERNAME for compatibility.
    """
    # Construct the path relative to this script file
    # __file__ -> utils -> main -> src -> notification-microservice/.env
    script_dir = Path(__file__).parent
    env_path = script_dir.parents[2] / '.env'

    # Load the .env file if found
    if env_path.exists():
        logging.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path) # Use dotenv_path argument

        # Map EMAIL_ADDRESS to EMAIL_USERNAME for compatibility
        if "EMAIL_ADDRESS" in os.environ and "EMAIL_USERNAME" not in os.environ:
            os.environ["EMAIL_USERNAME"] = os.environ["EMAIL_ADDRESS"]
            logging.info("Mapped EMAIL_ADDRESS to EMAIL_USERNAME for compatibility")

        # Check if email credentials are properly set
        if os.environ.get("EMAIL_USERNAME") and os.environ.get("EMAIL_PASSWORD"):
            logging.info(f"Email configured for: {os.environ.get('EMAIL_USERNAME')}")
            return True
        else:
            logging.warning("Email credentials not properly set in environment variables")
            return False
    else:
        logging.error(f".env file not found at expected path: {env_path}")
        return False 