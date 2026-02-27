"""
Configuration settings for the application
"""

import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database settings
    # Using Firestore (Firebase) as primary database
    # No MySQL/SQLite configuration needed
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: Union[str, List[str]] = "*"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Handle "*" for allow all
            if v.strip() == "*":
                return ["*"]
            # Try to parse as JSON list
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as comma-separated string
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # AI/ML settings
    MODEL_PATH: str = "./models"
    VOICE_MODEL_PATH: str = "./models/voice_analysis"
    TYPING_MODEL_PATH: str = "./models/typing_analysis"
    DEPRESSION_MODEL_PATH: str = "./models/depression_detection"
    TWITTER_MODEL_PATH: str = "./models/twitter_model"
    
    # Firebase settings
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    
    # Google APIs
    GOOGLE_SPEECH_API_KEY: str = os.getenv("GOOGLE_SPEECH_API_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    X_BEARER_TOKEN: str = os.getenv("X_BEARER_TOKEN", "")

    
    # Rasa chatbot
    RASA_SERVER_URL: str = os.getenv("RASA_SERVER_URL", "http://localhost:5005")
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env (like old MySQL settings)

settings = Settings()

