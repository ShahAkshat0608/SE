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
    Load environment variables from .env file.
    Maps EMAIL_ADDRESS to EMAIL_USERNAME for compatibility.
    """
    # Find .env file - look in current directory, parent directories, and project root
    env_path = None
    
    # Start with the current directory
    current_dir = Path.cwd()
    
    # Check current directory
    if (current_dir / '.env').exists():
        env_path = current_dir / '.env'
    
    # Check parent directories (up to 3 levels)
    if not env_path:
        for i in range(1, 4):
            parent_dir = current_dir.parents[i-1] if i <= len(current_dir.parents) else None
            if parent_dir and (parent_dir / '.env').exists():
                env_path = parent_dir / '.env'
                break
    
    # Load the .env file if found
    if env_path:
        logging.info(f"Loading environment variables from {env_path}")
        load_dotenv(env_path)
        
        # Map EMAIL_ADDRESS to EMAIL_USERNAME for compatibility
        if "EMAIL_ADDRESS" in os.environ and not "EMAIL_USERNAME" in os.environ:
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
        logging.error(".env file not found")
        return False 