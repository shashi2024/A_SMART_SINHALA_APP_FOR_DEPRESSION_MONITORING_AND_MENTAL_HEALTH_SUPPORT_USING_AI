"""
Configuration settings for the application
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./depression_monitoring.db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["*"]
    
    # AI/ML settings
    MODEL_PATH: str = "./models"
    VOICE_MODEL_PATH: str = "./models/voice_analysis"
    TYPING_MODEL_PATH: str = "./models/typing_analysis"
    DEPRESSION_MODEL_PATH: str = "./models/depression_detection"
    
    # Firebase settings
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    
    # Google APIs
    GOOGLE_SPEECH_API_KEY: str = os.getenv("GOOGLE_SPEECH_API_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Rasa chatbot
    RASA_SERVER_URL: str = os.getenv("RASA_SERVER_URL", "http://localhost:5005")
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()

