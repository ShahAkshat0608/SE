"""
Root level runner for the Notification Microservice.
This script allows you to run the service from the project root directory.
"""
import uvicorn
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to the Python path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the environment loader
from src.main.utils.env_loader import load_env_variables

if __name__ == "__main__":
    # Load environment variables
    env_loaded = load_env_variables()
    
    if not env_loaded:
        print("WARNING: Email credentials not properly loaded. Email notifications may not work.")
    
    # Run the service using the full module path
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run("src.main.main:app", host="0.0.0.0", port=port, reload=True) 