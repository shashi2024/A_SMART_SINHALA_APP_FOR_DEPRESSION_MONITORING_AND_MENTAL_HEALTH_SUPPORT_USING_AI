"""
Typing pattern analysis routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db, User, Session as DBSession, TypingAnalysis
from app.routes.auth import get_current_user
from app.services.typing_analysis import TypingAnalysisService
from app.services.fake_detection import FakeDetectionService

router = APIRouter()

class TypingData(BaseModel):
    keystroke_timings: List[float]  # Time between keystrokes
    typing_speed: float  # Characters per minute
    pause_duration: float  # Average pause duration
    error_rate: float  # Percentage of errors
    pressure_patterns: Optional[List[float]] = None  # Pressure data if available
    session_id: Optional[int] = None

class TypingAnalysisResponse(BaseModel):
    session_id: int
    depression_score: float
    risk_level: str
    is_fake: bool
    fake_confidence: float
    insights: dict

@router.post("/analyze", response_model=TypingAnalysisResponse)
async def analyze_typing(
    typing_data: TypingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze typing patterns"""
    typing_service = TypingAnalysisService()
    fake_service = FakeDetectionService()
    
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
        session = db.query(DBSession).filter(DBSession.id == typing_data.session_id).first()
    else:
        session = DBSession(
            user_id=current_user.id,
            session_type="typing",
            start_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save analysis to database
    typing_analysis = TypingAnalysis(
        user_id=current_user.id,
        session_id=session.id,
        keystroke_timings=json.dumps(typing_data.keystroke_timings),
        typing_speed=typing_data.typing_speed,
        pause_duration=typing_data.pause_duration,
        error_rate=typing_data.error_rate,
        pressure_patterns=json.dumps(typing_data.pressure_patterns or []),
        depression_indicator=analysis_result.get("depression_score", 0),
        is_fake=fake_result.get("is_fake", False),
        fake_confidence=fake_result.get("confidence", 0)
    )
    db.add(typing_analysis)
    
    # Update session
    session.depression_score = analysis_result.get("depression_score", 0)
    session.risk_level = analysis_result.get("risk_level", "low")
    db.commit()
    
    return TypingAnalysisResponse(
        session_id=session.id,
        depression_score=analysis_result.get("depression_score", 0),
        risk_level=analysis_result.get("risk_level", "low"),
        is_fake=fake_result.get("is_fake", False),
        fake_confidence=fake_result.get("confidence", 0),
        insights=analysis_result.get("insights", {})
    )

@router.get("/history")
async def get_typing_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's typing analysis history"""
    analyses = db.query(TypingAnalysis).filter(
        TypingAnalysis.user_id == current_user.id
    ).order_by(TypingAnalysis.created_at.desc()).all()
    
    return [
        {
            "id": analysis.id,
            "session_id": analysis.session_id,
            "typing_speed": analysis.typing_speed,
            "depression_score": analysis.depression_indicator,
            "is_fake": analysis.is_fake,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]

