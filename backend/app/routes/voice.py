"""
Voice analysis routes for call-based interactions
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db, User, Session as DBSession, VoiceAnalysis
from app.routes.auth import get_current_user
from app.services.voice_analysis import VoiceAnalysisService
from app.services.fake_detection import FakeDetectionService
from app.config import settings

router = APIRouter()

class VoiceAnalysisResponse(BaseModel):
    session_id: int
    emotion: str
    depression_score: float
    risk_level: str
    is_fake: bool
    fake_confidence: float
    recommendations: list

@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    audio_file: UploadFile = File(...),
    session_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze voice from audio file"""
    # Save uploaded file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{datetime.now().timestamp()}.wav")
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Initialize services
    voice_service = VoiceAnalysisService()
    fake_service = FakeDetectionService()
    
    # Analyze voice
    analysis_result = await voice_service.analyze_audio(file_path)
    
    # Check for fake detection
    fake_result = await fake_service.detect_fake_voice(file_path, analysis_result)
    
    # Get or create session
    if session_id:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
    else:
        session = DBSession(
            user_id=current_user.id,
            session_type="voice",
            start_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save analysis to database
    voice_analysis = VoiceAnalysis(
        user_id=current_user.id,
        session_id=session.id,
        audio_file_path=file_path,
        duration=analysis_result.get("duration", 0),
        pitch=analysis_result.get("pitch", 0),
        energy=analysis_result.get("energy", 0),
        mfcc_features=str(analysis_result.get("mfcc_features", [])),
        emotion_detected=analysis_result.get("emotion", "neutral"),
        depression_indicator=analysis_result.get("depression_score", 0),
        is_fake=fake_result.get("is_fake", False),
        fake_confidence=fake_result.get("confidence", 0)
    )
    db.add(voice_analysis)
    
    # Update session
    session.depression_score = analysis_result.get("depression_score", 0)
    session.risk_level = analysis_result.get("risk_level", "low")
    db.commit()
    
    return VoiceAnalysisResponse(
        session_id=session.id,
        emotion=analysis_result.get("emotion", "neutral"),
        depression_score=analysis_result.get("depression_score", 0),
        risk_level=analysis_result.get("risk_level", "low"),
        is_fake=fake_result.get("is_fake", False),
        fake_confidence=fake_result.get("confidence", 0),
        recommendations=analysis_result.get("recommendations", [])
    )

@router.get("/history")
async def get_voice_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's voice analysis history"""
    analyses = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.user_id == current_user.id
    ).order_by(VoiceAnalysis.created_at.desc()).all()
    
    return [
        {
            "id": analysis.id,
            "session_id": analysis.session_id,
            "emotion": analysis.emotion_detected,
            "depression_score": analysis.depression_indicator,
            "is_fake": analysis.is_fake,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]

