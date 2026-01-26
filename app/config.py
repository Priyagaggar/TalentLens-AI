import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentLens AI"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]

    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db" # Default to SQLite for easy start
    
    # NLP
    # Add any specific NLP model paths or keys here

    class Config:
        env_file = ".env"

settings = Settings()
