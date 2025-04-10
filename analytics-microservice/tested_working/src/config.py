"""Configuration settings for the analytics microservice."""

import os

# Data source configuration
TASKS_FILE = os.environ.get("TASKS_FILE", "tasks.json")

# API configuration
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "5000"))
API_DEBUG = os.environ.get("API_DEBUG", "True").lower() == "true"

# Analytics configuration
DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
PRIORITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}