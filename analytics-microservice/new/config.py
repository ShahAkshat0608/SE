"""Root configuration file for the analytics microservice."""

import os
import json
from typing import Dict, Any


def get_config() -> Dict[str, Any]:
    """Get configuration dictionary.
    
    Returns:
        Dictionary with configuration values
    """
    # Default configuration
    config = {
        # API settings
        "API_HOST": "0.0.0.0",
        "API_PORT": 5000,
        "API_DEBUG": False,
        
        # Data settings
        "DATA_DIR": "data",
        "TASKS_FILE": os.path.join("data", "tasks.json"),
        "PROJECTS_FILE": os.path.join("data", "projects.json"),
        "USERS_FILE": os.path.join("data", "users.json"),
        
        # Logging settings
        "LOG_LEVEL": "INFO",
        "LOG_FILE": os.path.join("logs", "analytics.log")
    }
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    return config


if __name__ == "__main__":
    # If run directly, output the current configuration
    config = get_config()
    print(json.dumps(config, indent=2))