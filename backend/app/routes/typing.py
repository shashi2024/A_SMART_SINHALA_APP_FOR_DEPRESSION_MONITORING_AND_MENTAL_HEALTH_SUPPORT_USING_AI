"""
Typing pattern analysis routes - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from app.routes.auth import get_current_user
from app.services.typing_analysis import TypingAnalysisService
from app.services.fake_detection import FakeDetectionService
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class TypingData(BaseModel):
    keystroke_timings: List[float]  # Time between keystrokes
    typing_speed: float  # Characters per minute
    pause_duration: float  # Average pause duration
    error_rate: float  # Percentage of errors
    pressure_patterns: Optional[List[float]] = None  # Pressure data if available
    session_id: Optional[str] = None  # Changed from int to str for Firestore

class TypingAnalysisResponse(BaseModel):
    session_id: str  # Changed from int to str for Firestore
    depression_score: float
    risk_level: str
    is_fake: bool
    fake_confidence: float
    insights: dict

@router.post("/analyze", response_model=TypingAnalysisResponse)
async def analyze_typing(
    typing_data: TypingData,
    current_user: dict = Depends(get_current_user)
):
    """Analyze typing patterns"""
    typing_service = TypingAnalysisService()
    fake_service = FakeDetectionService()
    
    user_id = current_user.get('id')
    
    # Analyze typing patterns
    analysis_result = await typing_service.analyze_patterns(
        keystroke_timings=typing_data.keystroke_timings,
        typing_speed=typing_data.typing_speed,
        pause_duration=typing_data.pause_duration,
        error_rate=typing_data.error_rate,
        pressure_patterns=typing_data.pressure_patterns
    )
    
    # Check for fake detection
    fake_result = await fake_service.detect_fake_typing(
        typing_data.keystroke_timings,
        typing_data.typing_speed,
        typing_data.pause_duration
    )
    
    # Get or create session
    if typing_data.session_id:
        session = firestore_service.get_session_by_id(typing_data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = firestore_service.create_session({
            'user_id': user_id,
            'session_type': 'typing'
        })
        session = firestore_service.get_session_by_id(session_id)
    
    # Save analysis to Firestore
    firestore_service.create_typing_analysis({
        'user_id': user_id,
        'session_id': session['id'],
        'keystroke_timings': json.dumps(typing_data.keystroke_timings),
        'typing_speed': typing_data.typing_speed,
        'pause_duration': typing_data.pause_duration,
        'error_rate': typing_data.error_rate,
        'pressure_patterns': json.dumps(typing_data.pressure_patterns or []),
        'depression_indicator': analysis_result.get("depression_score", 0),
        'is_fake': fake_result.get("is_fake", False),
        'fake_confidence': fake_result.get("confidence", 0)
    })
    
    # Update session
    firestore_service.update_session(session['id'], {
        'depression_score': analysis_result.get("depression_score", 0),
        'risk_level': analysis_result.get("risk_level", "low")
    })
    
    return TypingAnalysisResponse(
        session_id=session['id'],
        depression_score=analysis_result.get("depression_score", 0),
        risk_level=analysis_result.get("risk_level", "low"),
        is_fake=fake_result.get("is_fake", False),
        fake_confidence=fake_result.get("confidence", 0),
        insights=analysis_result.get("insights", {})
    )

@router.get("/history")
async def get_typing_history(
    current_user: dict = Depends(get_current_user)
):
    """Get user's typing analysis history from Firestore"""
    user_id = current_user.get('id')
    analyses = firestore_service.get_user_typing_analyses(user_id)
    
    return [
        {
            "id": analysis.get('id'),
            "session_id": analysis.get('session_id'),
            "typing_speed": analysis.get('typing_speed'),
            "depression_score": analysis.get('depression_indicator'),
            "is_fake": analysis.get('is_fake', False),
            "created_at": analysis.get('created_at')
        }
        for analysis in analyses
    ]

