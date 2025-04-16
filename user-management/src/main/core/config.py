from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    APP_NAME: str = "User Management Microservice"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False # Set to True for development reload

    class Config:
        # If you were using a .env file:
        # env_file = ".env"
        pass

settings = Settings() 