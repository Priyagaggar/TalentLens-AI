import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentLens AI"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]

    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db" # Default to SQLite for easy start
    
    # Auth & Security
    SECRET_KEY: str = "your-super-secret-key-for-jwt-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day

    # SMTP Settings (configured for Mailtrap defaults)
    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = "alerts@talentlens.ai"
    MOCK_EMAIL: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
