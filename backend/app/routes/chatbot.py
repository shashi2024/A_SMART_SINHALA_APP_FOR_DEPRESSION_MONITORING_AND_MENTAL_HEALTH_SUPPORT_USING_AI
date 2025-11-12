"""
Chatbot routes for text and voice conversations
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db, User, Session as DBSession
from app.routes.auth import get_current_user
from app.services.chatbot_service import ChatbotService
from app.services.depression_detection import DepressionDetectionService

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    session_id: int
    depression_score: Optional[float] = None
    risk_level: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to chatbot and get response"""
    chatbot_service = ChatbotService()
    depression_service = DepressionDetectionService()
    
    # Get or create session
    if chat_message.session_id:
        session = db.query(DBSession).filter(DBSession.id == chat_message.session_id).first()
    else:
        session = DBSession(
            user_id=current_user.id,
            session_type="chat",
            start_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get chatbot response
    response = await chatbot_service.get_response(chat_message.message, current_user.id)
    
    # Analyze for depression
    depression_score = await depression_service.analyze_text(chat_message.message)
    risk_level = depression_service.get_risk_level(depression_score)
    
    # Update session
    session.depression_score = depression_score
    session.risk_level = risk_level
    db.commit()
    
    return ChatResponse(
        response=response,
        session_id=session.id,
        depression_score=depression_score,
        risk_level=risk_level
    )

@router.get("/sessions")
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    sessions = db.query(DBSession).filter(
        DBSession.user_id == current_user.id,
        DBSession.session_type == "chat"
    ).order_by(DBSession.start_time.desc()).all()
    
    return [
        {
            "id": session.id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "depression_score": session.depression_score,
            "risk_level": session.risk_level
        }
        for session in sessions
    ]

