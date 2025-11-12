"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

Base = declarative_base()

# Database engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user")
    voice_analyses = relationship("VoiceAnalysis", back_populates="user")
    typing_analyses = relationship("TypingAnalysis", back_populates="user")
    digital_twin = relationship("DigitalTwin", back_populates="user", uselist=False)

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String)  # 'chat', 'voice', 'typing'
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    depression_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # 'low', 'moderate', 'high', 'severe'
    
    user = relationship("User", back_populates="sessions")

class VoiceAnalysis(Base):
    __tablename__ = "voice_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    audio_file_path = Column(String)
    duration = Column(Float)
    pitch = Column(Float)
    energy = Column(Float)
    mfcc_features = Column(Text)  # JSON string
    emotion_detected = Column(String)
    depression_indicator = Column(Float)
    is_fake = Column(Boolean, default=False)
    fake_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="voice_analyses")

class TypingAnalysis(Base):
    __tablename__ = "typing_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    keystroke_timings = Column(Text)  # JSON string
    typing_speed = Column(Float)
    pause_duration = Column(Float)
    error_rate = Column(Float)
    pressure_patterns = Column(Text)  # JSON string (if available)
    depression_indicator = Column(Float)
    is_fake = Column(Boolean, default=False)
    fake_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="typing_analyses")

class DigitalTwin(Base):
    __tablename__ = "digital_twins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    mental_health_profile = Column(Text)  # JSON string
    historical_data = Column(Text)  # JSON string
    risk_factors = Column(Text)  # JSON string
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="digital_twin")

class AdminAlert(Base):
    __tablename__ = "admin_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String)  # 'high_risk', 'fake_detected', 'crisis'
    severity = Column(String)  # 'low', 'medium', 'high', 'critical'
    message = Column(Text)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

