import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Recruitment System - Agent 1"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./ai_recruitment.db"
    
    AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o-mini"
    
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    UPLOAD_DIR: str = "./uploads"
    
    SECRET_KEY: str = "development-secret-key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
