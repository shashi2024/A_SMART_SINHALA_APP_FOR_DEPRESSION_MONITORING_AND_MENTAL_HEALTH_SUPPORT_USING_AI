"""
Chatbot routes for text and voice conversations - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.routes.auth import get_current_user
from app.services.chatbot_service import ChatbotService
from app.services.depression_detection import DepressionDetectionService
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None  # Changed from int to str for Firestore

class ChatResponse(BaseModel):
    response: str
    session_id: str  # Changed from int to str for Firestore
    depression_score: Optional[float] = None
    risk_level: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send message to chatbot and get response"""
    chatbot_service = ChatbotService()
    depression_service = DepressionDetectionService()
    
    user_id = current_user.get('id')
    
    # Get or create session
    if chat_message.session_id:
        session = firestore_service.get_session_by_id(chat_message.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = firestore_service.create_session({
            'user_id': user_id,
            'session_type': 'chat'
        })
        session = firestore_service.get_session_by_id(session_id)
    
    # Get chatbot response
    response = await chatbot_service.get_response(chat_message.message, user_id)
    
    # Analyze for depression
    depression_score = await depression_service.analyze_text(chat_message.message)
    risk_level = depression_service.get_risk_level(depression_score)
    
    # Update session
    firestore_service.update_session(session['id'], {
        'depression_score': depression_score,
        'risk_level': risk_level
    })
    
    return ChatResponse(
        response=response,
        session_id=session['id'],
        depression_score=depression_score,
        risk_level=risk_level
    )

@router.get("/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat sessions from Firestore"""
    user_id = current_user.get('id')
    sessions = firestore_service.get_user_sessions(user_id, session_type="chat")
    
    return [
        {
            "id": session.get('id'),
            "start_time": session.get('start_time'),
            "end_time": session.get('end_time'),
            "depression_score": session.get('depression_score'),
            "risk_level": session.get('risk_level')
        }
        for session in sessions
    ]

