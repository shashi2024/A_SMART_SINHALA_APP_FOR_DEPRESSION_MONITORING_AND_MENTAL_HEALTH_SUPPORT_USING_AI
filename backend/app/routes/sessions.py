"""
Session management routes - for updating sessions with mood
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.routes.auth import get_current_user
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class SessionMoodUpdateRequest(BaseModel):
    mood: Optional[str] = None  # Mood is optional

@router.put("/{session_id}/mood")
async def update_session_mood(
    session_id: str,
    mood_data: SessionMoodUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update session with mood (optional)"""
    user_id = str(current_user.get('id'))
    
    # Get session to verify ownership
    session = firestore_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to current user (or admin can update any)
    if str(session.get('user_id')) != user_id and not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Not authorized to update this session")
    
    # Validate mood if provided
    if mood_data.mood:
        valid_moods = ['Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad']
        if mood_data.mood not in valid_moods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
            )
    
    # Update session with mood
    updates = {}
    if mood_data.mood:
        updates['mood'] = mood_data.mood
    else:
        # If mood is explicitly None, remove it
        updates['mood'] = None
    
    firestore_service.update_session(session_id, updates)
    
    # Get updated session
    updated_session = firestore_service.get_session_by_id(session_id)
    
    return {
        "message": "Session mood updated successfully",
        "session_id": session_id,
        "mood": updated_session.get('mood')
    }

@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get session details"""
    user_id = str(current_user.get('id'))
    
    session = firestore_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to current user (or admin can view any)
    if str(session.get('user_id')) != user_id and not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
    
    return {
        "id": session.get('id'),
        "user_id": session.get('user_id'),
        "session_type": session.get('session_type'),
        "mood": session.get('mood'),
        "start_time": session.get('start_time'),
        "end_time": session.get('end_time'),
        "depression_score": session.get('depression_score'),
        "risk_level": session.get('risk_level'),
        "language": session.get('language')
    }

