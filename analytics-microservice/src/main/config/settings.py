import os
from pydantic_settings import BaseSettings  # Updated import

class Settings(BaseSettings):
    """Application settings"""
    # API settings
    API_PREFIX: str = "/api/analytics"
    DEBUG: bool = True
    
    # Authentication - ensure this matches project-management-microservice
    JWT_SECRET_KEY: str = "your-secret-key-for-development-only"
    JWT_ALGORITHM: str = "HS256"
    
    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()