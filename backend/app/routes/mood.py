"""
Mood check-in routes - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.routes.auth import get_current_user
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class MoodCheckInRequest(BaseModel):
    mood: str
    notes: Optional[str] = None

class MoodCheckInResponse(BaseModel):
    id: str
    user_id: str
    mood: str
    notes: Optional[str] = None
    created_at: datetime
    date: str

@router.post("/checkin", response_model=MoodCheckInResponse)
async def create_mood_checkin(
    mood_data: MoodCheckInRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new mood check-in and update risk level"""
    user_id = str(current_user.get('id'))
    
    # Validate mood value
    valid_moods = ['Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad']
    if mood_data.mood not in valid_moods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
        )
    
    # Try to find the most recent session (within last 2 hours) to link mood
    # This links mood to the session the user is likely currently in
    recent_sessions = firestore_service.get_user_sessions(user_id)
    session_to_update = None
    
    if recent_sessions:
        from datetime import timedelta
        now = datetime.utcnow()
        two_hours_ago = now - timedelta(hours=2)
        
        # Helper function to parse datetime from various formats
        def parse_datetime(dt_value):
            if dt_value is None:
                return None
            if isinstance(dt_value, datetime):
                return dt_value
            # Handle Firestore Timestamp
            if hasattr(dt_value, 'timestamp'):
                try:
                    return datetime.fromtimestamp(dt_value.timestamp())
                except:
                    pass
            if isinstance(dt_value, str):
                try:
                    # Try ISO format
                    return datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
                except:
                    pass
            return None
        
        # Find the most recent session (prefer active ones without end_time, then most recent within 2 hours)
        active_sessions = []
        recent_sessions_list = []
        
        for session in recent_sessions:
            start_time = parse_datetime(session.get('start_time'))
            end_time = session.get('end_time')
            
            # Check if session is active (no end_time)
            if not end_time and start_time:
                active_sessions.append((session, start_time))
            
            # Check if session started within last 2 hours
            if start_time and start_time >= two_hours_ago:
                recent_sessions_list.append((session, start_time))
        
        # Prioritize active sessions
        if active_sessions:
            # Sort by start_time, most recent first
            active_sessions.sort(key=lambda x: x[1], reverse=True)
            session_to_update = active_sessions[0][0]
        elif recent_sessions_list:
            # If no active sessions, use most recent within 2 hours
            recent_sessions_list.sort(key=lambda x: x[1], reverse=True)
            session_to_update = recent_sessions_list[0][0]
        elif recent_sessions:
            # Fallback: use the first (most recent) session
            session_to_update = recent_sessions[0]
    
    # Create mood check-in
    mood_checkin_data = {
        'user_id': user_id,
        'username': current_user.get('username'),
        'mood': mood_data.mood,
        'notes': mood_data.notes
    }
    
    # Link to session if found
    if session_to_update:
        session_id = session_to_update.get('id')
        if session_id:
            mood_checkin_data['session_id'] = session_id
    
    checkin_id = firestore_service.create_mood_checkin(mood_checkin_data)
    
    # Update the session with mood if we found a recent session
    if session_to_update:
        try:
            session_id = session_to_update.get('id')
            if session_id:
                firestore_service.update_session(session_id, {'mood': mood_data.mood})
                print(f"[INFO] Updated session {session_id} with mood {mood_data.mood}")
        except Exception as e:
            print(f"[WARNING] Failed to update session with mood: {e}")
            import traceback
            traceback.print_exc()
    
    # Update digital twin profile to recalculate risk level with new mood data
    try:
        from app.services.digital_twin_service import DigitalTwinService
        digital_twin_service = DigitalTwinService()
        await digital_twin_service.update_profile(user_id)
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.warning(f"Failed to update digital twin after mood check-in: {e}")
    
    # Retrieve the created check-in
    checkins = firestore_service.get_user_mood_checkins(user_id, limit=1)
    if not checkins:
        raise HTTPException(status_code=500, detail="Failed to create mood check-in")
    
    checkin = checkins[0]
    return MoodCheckInResponse(
        id=checkin['id'],
        user_id=checkin['user_id'],
        mood=checkin['mood'],
        notes=checkin.get('notes'),
        created_at=checkin['created_at'],
        date=checkin.get('date', datetime.now().date().isoformat())
    )

@router.get("/history", response_model=List[MoodCheckInResponse])
async def get_mood_history(
    limit: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get mood check-in history for the current user"""
    user_id = str(current_user.get('id'))
    
    checkins = firestore_service.get_user_mood_checkins(
        user_id=user_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        MoodCheckInResponse(
            id=checkin['id'],
            user_id=checkin['user_id'],
            mood=checkin['mood'],
            notes=checkin.get('notes'),
            created_at=checkin['created_at'],
            date=checkin.get('date', datetime.now().date().isoformat())
        )
        for checkin in checkins
    ]

@router.get("/admin/all")
async def get_all_mood_checkins_admin(
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all mood check-ins (accessible by admin and sub-admin)"""
    if not (current_user.get('is_admin', False) or current_user.get('is_sub_admin', False)):
        raise HTTPException(status_code=403, detail="Admin or sub-admin access required")
    
    checkins = firestore_service.get_all_mood_checkins(
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )
    
    # Enrich with user information
    result = []
    for checkin in checkins:
        user = firestore_service.get_user_by_id(checkin['user_id'])
        result.append({
            'id': checkin['id'],
            'user_id': checkin['user_id'],
            'username': user.get('username', 'Unknown') if user else 'Unknown',
            'email': user.get('email', '') if user else '',
            'mood': checkin['mood'],
            'notes': checkin.get('notes'),
            'created_at': checkin['created_at'],
            'date': checkin.get('date', datetime.now().date().isoformat())
        })
    
    return {"checkins": result}

