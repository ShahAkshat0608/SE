"""Configuration settings for the analytics microservice."""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Configuration settings for the application."""
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    API_DEBUG: bool = False
    
    # Data settings
    DATA_DIR: str = "data"
    TASKS_FILE: str = "data/tasks.json"
    PROJECTS_FILE: str = "data/projects.json"
    USERS_FILE: str = "data/users.json"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Analytics settings
    DEFAULT_TIME_PERIOD_DAYS: int = 30
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables.
        
        Returns:
            Settings instance with values from environment variables
        """
        settings = cls()
        
        # API settings
        settings.API_HOST = os.environ.get("API_HOST", settings.API_HOST)
        settings.API_PORT = int(os.environ.get("API_PORT", settings.API_PORT))
        settings.API_DEBUG = os.environ.get("API_DEBUG", "").lower() in ("true", "1", "yes")
        
        # Data settings
        settings.DATA_DIR = os.environ.get("DATA_DIR", settings.DATA_DIR)
        settings.TASKS_FILE = os.environ.get("TASKS_FILE", settings.TASKS_FILE)
        settings.PROJECTS_FILE = os.environ.get("PROJECTS_FILE", settings.PROJECTS_FILE)
        settings.USERS_FILE = os.environ.get("USERS_FILE", settings.USERS_FILE)
        
        # Ensure data settings have consistent base directory
        if not os.path.isabs(settings.TASKS_FILE):
            settings.TASKS_FILE = os.path.join(os.getcwd(), settings.TASKS_FILE)
            
        if not os.path.isabs(settings.PROJECTS_FILE):
            settings.PROJECTS_FILE = os.path.join(os.getcwd(), settings.PROJECTS_FILE)
            
        if not os.path.isabs(settings.USERS_FILE):
            settings.USERS_FILE = os.path.join(os.getcwd(), settings.USERS_FILE)
        
        # Logging settings
        settings.LOG_LEVEL = os.environ.get("LOG_LEVEL", settings.LOG_LEVEL)
        settings.LOG_FILE = os.environ.get("LOG_FILE", settings.LOG_FILE)
        
        # Analytics settings
        settings.DEFAULT_TIME_PERIOD_DAYS = int(os.environ.get("DEFAULT_TIME_PERIOD_DAYS", 
                                                              settings.DEFAULT_TIME_PERIOD_DAYS))
        
        return settings
    
    @classmethod
    def from_file(cls, config_file: str) -> 'Settings':
        """Create settings from a configuration file.
        
        Args:
            config_file: Path to JSON configuration file
            
        Returns:
            Settings instance with values from the configuration file
        """
        settings = cls()
        
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Configuration file {config_file} not found, using defaults")
                return settings
                
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update settings with values from config file
            for key, value in config.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            return settings
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {str(e)}")
            return settings


_settings_instance = None


def get_settings() -> Settings:
    """Get the application settings.
    
    Returns:
        Settings instance
    """
    global _settings_instance
    
    if _settings_instance is None:
        # First try to load from config file
        config_file = os.environ.get("CONFIG_FILE", "config.json")
        if os.path.exists(config_file):
            _settings_instance = Settings.from_file(config_file)
        else:
            # Fall back to environment variables
            _settings_instance = Settings.from_env()
    
    return _settings_instance


def update_settings(settings: Settings) -> None:
    """Update the application settings.
    
    Args:
        settings: New settings instance
    """
    global _settings_instance
    _settings_instance = settings