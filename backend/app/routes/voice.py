"""
Voice analysis routes for call-based interactions with language support - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import json

from app.routes.auth import get_current_user
from app.services.voice_analysis import VoiceAnalysisService
from app.services.call_bot_detection import CallBotDetectionService
from app.services.fake_detection import FakeDetectionService
from app.services.firestore_service import FirestoreService
from app.config import settings

router = APIRouter()
firestore_service = FirestoreService()

class VoiceAnalysisResponse(BaseModel):
    session_id: str  # Changed from int to str for Firestore
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
    session_id: Optional[str] = Form(default=None),  # Changed from int to str
    current_user: dict = Depends(get_current_user)
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
    
    user_id = current_user.get('id')
    
    # Save uploaded file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{user_id}_{datetime.now().timestamp()}.wav"
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
    
    # Get transcript, duration, and depression score
    transcript = analysis_result.get("transcription", "")
    call_duration = analysis_result.get("duration", 0.0)
    depression_score = analysis_result.get("depression_score", None)
    
    # Get repeat call count from last hour
    from datetime import datetime, timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    user_sessions = firestore_service.get_user_sessions(user_id)
    repeat_call_count = 0
    for session in user_sessions:
        start_time = session.get('start_time')
        if start_time:
            # Handle Firestore Timestamp objects
            if hasattr(start_time, 'timestamp'):
                try:
                    session_time = datetime.fromtimestamp(start_time.timestamp())
                except:
                    continue
            elif isinstance(start_time, datetime):
                session_time = start_time
            elif isinstance(start_time, str):
                try:
                    session_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except:
                    continue
            else:
                continue
            
            if session_time >= one_hour_ago and session.get('session_type') == 'voice':
                repeat_call_count += 1
    
    # Check for call bot detection with integrated model and algorithm
    bot_result = await call_bot_service.detect_call_bot(
        file_path,
        language=language,
        voice_features=analysis_result,
        transcript=transcript,
        call_duration_sec=call_duration,
        repeat_call_count_last_hour=repeat_call_count,
        depression_score=depression_score
    )
    
    # Also check with legacy fake detection (for compatibility)
    fake_result = await fake_service.detect_fake_voice(file_path, analysis_result)
    
    # Use integrated detection as primary, fallback to legacy
    is_fake = bot_result.get("is_call_bot", False) or fake_result.get("is_fake", False)
    fake_confidence = max(
        bot_result.get("confidence", 0.0),
        fake_result.get("confidence", 0.0)
    )
    
    # Get or create session
    if session_id:
        session = firestore_service.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = firestore_service.create_session({
            'user_id': user_id,
            'session_type': 'voice'
        })
        session = firestore_service.get_session_by_id(session_id)
    
    # Save analysis to Firestore
    firestore_service.create_voice_analysis({
        'user_id': user_id,
        'session_id': session['id'],
        'audio_file_path': file_path,
        'duration': analysis_result.get("duration", 0),
        'pitch': analysis_result.get("pitch", 0),
        'energy': analysis_result.get("energy", 0),
        'mfcc_features': json.dumps(analysis_result.get("mfcc_features", [])),
        'emotion_detected': analysis_result.get("emotion", "neutral"),
        'depression_indicator': analysis_result.get("depression_score", 0),
        'is_fake': is_fake,
        'fake_confidence': fake_confidence
    })
    
    # Update session
    firestore_service.update_session(session['id'], {
        'depression_score': analysis_result.get("depression_score", 0),
        'risk_level': analysis_result.get("risk_level", "low")
    })
    
    # Create alert if fake call bot detected
    risk_label = bot_result.get("risk_label", "low_fake_risk")
    if is_fake and fake_confidence > 0.4:
        severity = 'high' if fake_confidence >= 0.7 else 'medium'
        suspicious_words = bot_result.get("suspicious_words", [])
        words_str = ", ".join(suspicious_words[:5]) if suspicious_words else "none"
        
        firestore_service.create_alert({
            'user_id': user_id,
            'alert_type': 'fake_detected',
            'severity': severity,
            'message': f"Potential fake call detected. Risk: {risk_label}, Confidence: {fake_confidence:.2f}. Suspicious words: {words_str}. Language: {language}."
        })
    
    # Check if we should analyze a voice batch (1-5, 15-20, 30-35)
    all_voice_analyses = firestore_service.get_user_voice_analyses(user_id)
    current_count = len(all_voice_analyses)
    
    batch_result = None
    batch_info = batch_fake_service.should_check_batch(current_count, "voice")
    if batch_info:
        # Analyze this batch
        batch_result = await batch_fake_service.analyze_voice_batch(user_id, batch_info)
        
        # Create alert if batch indicates fake user
        if batch_result.get("is_fake", False) and batch_result.get("fake_score", 0) >= 0.6:
            firestore_service.create_alert({
                'user_id': user_id,
                'alert_type': 'batch_fake_detected',
                'severity': 'high' if batch_result.get("fake_score", 0) >= 0.8 else 'medium',
                'message': f"Fake user detected in {batch_result.get('batch_name')} batch (calls {batch_result.get('batch_range')}). Fake score: {batch_result.get('fake_score', 0):.2f}"
            })
    
    # Use batch result if available, otherwise use individual result
    final_is_fake = batch_result.get("is_fake", False) if batch_result else is_fake
    final_fake_confidence = max(
        batch_result.get("fake_score", 0) if batch_result else 0,
        fake_confidence
    )
    
    return VoiceAnalysisResponse(
        session_id=session['id'],
        emotion=analysis_result.get("emotion", "neutral"),
        depression_score=analysis_result.get("depression_score", 0),
        risk_level=analysis_result.get("risk_level", "low"),
        is_fake=final_is_fake,
        is_call_bot=bot_result.get("is_call_bot", False) or final_is_fake,
        fake_confidence=final_fake_confidence,
        bot_confidence=bot_result.get("confidence", 0.0),
        bot_type=bot_result.get("bot_type"),
        recommendations=analysis_result.get("recommendations", []),
        transcription=analysis_result.get("transcription", ""),
        language=language
    )

@router.get("/history")
async def get_voice_history(
    current_user: dict = Depends(get_current_user)
):
    """Get user's voice analysis history from Firestore"""
    user_id = current_user.get('id')
    analyses = firestore_service.get_user_voice_analyses(user_id)
    
    return [
        {
            "id": analysis.get('id'),
            "session_id": analysis.get('session_id'),
            "emotion": analysis.get('emotion_detected'),
            "depression_score": analysis.get('depression_indicator'),
            "is_fake": analysis.get('is_fake', False),
            "fake_confidence": analysis.get('fake_confidence'),
            "created_at": analysis.get('created_at')
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

@router.get("/batch-status")
async def get_voice_batch_status(
    current_user: dict = Depends(get_current_user)
):
    """Get batch analysis status for voice calls"""
    user_id = current_user.get('id')
    return await batch_fake_service.get_user_batch_status(user_id, "voice")
