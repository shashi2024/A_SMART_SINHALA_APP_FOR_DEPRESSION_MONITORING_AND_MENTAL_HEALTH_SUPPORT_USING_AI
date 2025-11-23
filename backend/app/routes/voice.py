"""
Voice analysis routes for call-based interactions with language support
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db, User, Session as DBSession, VoiceAnalysis
from app.routes.auth import get_current_user
from app.services.voice_analysis import VoiceAnalysisService
from app.services.call_bot_detection import CallBotDetectionService
from app.services.fake_detection import FakeDetectionService
from app.config import settings

router = APIRouter()

class VoiceAnalysisResponse(BaseModel):
    session_id: int
    emotion: str
    depression_score: float
    risk_level: str
    is_fake: bool
    is_call_bot: bool
    fake_confidence: float
    bot_confidence: float
    bot_type: Optional[str]
    recommendations: list
    transcription: str
    language: str

@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    audio_file: UploadFile = File(...),
    language: str = Form(default="sinhala"),  # Language selection: sinhala, tamil, english
    session_id: Optional[int] = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze voice from audio file with language support and call bot detection
    
    Args:
        audio_file: Audio file to analyze
        language: Language of the call ('sinhala', 'tamil', 'english')
        session_id: Optional session ID to continue existing session
        current_user: Authenticated user
        db: Database session
    """
    # Validate language
    valid_languages = ["sinhala", "tamil", "english"]
    if language.lower() not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Must be one of: {', '.join(valid_languages)}"
        )
    
    language = language.lower()
    
    # Save uploaded file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{current_user.id}_{datetime.now().timestamp()}.wav"
    )
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Initialize services
    voice_service = VoiceAnalysisService()
    call_bot_service = CallBotDetectionService()
    fake_service = FakeDetectionService()
    
    # Analyze voice with language support
    analysis_result = await voice_service.analyze_audio(file_path, language)
    
    # Check for call bot detection
    bot_result = await call_bot_service.detect_call_bot(
        file_path,
        language=language,
        voice_features=analysis_result
    )
    
    # Also check with legacy fake detection (for compatibility)
    fake_result = await fake_service.detect_fake_voice(file_path, analysis_result)
    
    # Use call bot detection as primary, fallback to fake detection
    is_fake = bot_result.get("is_call_bot", False) or fake_result.get("is_fake", False)
    fake_confidence = max(
        bot_result.get("confidence", 0.0),
        fake_result.get("confidence", 0.0)
    )
    
    # Get or create session
    if session_id:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
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
        is_fake=is_fake,
        fake_confidence=fake_confidence
    )
    db.add(voice_analysis)
    
    # Update session
    session.depression_score = analysis_result.get("depression_score", 0)
    session.risk_level = analysis_result.get("risk_level", "low")
    db.commit()
    
    # Create alert if fake call bot detected
    if is_fake and fake_confidence > 0.7:
        from app.database import AdminAlert
        alert = AdminAlert(
            user_id=current_user.id,
            alert_type="fake_detected",
            severity="high",
            message=f"Potential call bot detected in voice analysis. Confidence: {fake_confidence:.2f}. Language: {language}."
        )
        db.add(alert)
        db.commit()
    
    return VoiceAnalysisResponse(
        session_id=session.id,
        emotion=analysis_result.get("emotion", "neutral"),
        depression_score=analysis_result.get("depression_score", 0),
        risk_level=analysis_result.get("risk_level", "low"),
        is_fake=is_fake,
        is_call_bot=bot_result.get("is_call_bot", False),
        fake_confidence=fake_confidence,
        bot_confidence=bot_result.get("confidence", 0.0),
        bot_type=bot_result.get("bot_type"),
        recommendations=analysis_result.get("recommendations", []),
        transcription=analysis_result.get("transcription", ""),
        language=language
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
            "fake_confidence": analysis.fake_confidence,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {
                "code": "sinhala",
                "name": "Sinhala",
                "native_name": "සිංහල"
            },
            {
                "code": "tamil",
                "name": "Tamil",
                "native_name": "தமிழ்"
            },
            {
                "code": "english",
                "name": "English",
                "native_name": "English"
            }
        ]
    }
