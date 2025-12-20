"""
Admin panel routes for hospital management - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.routes.auth import get_current_user
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class AlertResponse(BaseModel):
    id: str  # Changed from int to str for Firestore
    user_id: str  # Changed from int to str
    username: str
    alert_type: str
    severity: str
    message: str
    created_at: datetime

class UserDashboard(BaseModel):
    user_id: str  # Changed from int to str for Firestore
    username: str
    email: str
    total_sessions: int
    average_depression_score: float
    risk_level: str
    last_activity: datetime

@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get admin dashboard data from Firestore"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all active users
    users = firestore_service.get_all_active_users()
    dashboard_data = []
    
    for user in users:
        user_id = user.get('id')
        stats = firestore_service.get_user_statistics(user_id)
        
        dashboard_data.append({
            "user_id": user_id,
            "username": user.get('username'),
            "email": user.get('email'),
            "total_sessions": stats.get('total_sessions', 0),
            "average_depression_score": stats.get('average_depression_score', 0),
            "risk_level": stats.get('risk_level', 'low'),
            "last_activity": stats.get('last_activity')
        })
    
    return {"users": dashboard_data}

@router.get("/alerts")
async def get_alerts(
    resolved: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get admin alerts from Firestore"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alerts = firestore_service.get_alerts(resolved=resolved)
    
    result = []
    for alert in alerts:
        user_id = alert.get('user_id')
        user = firestore_service.get_user_by_id(user_id) if user_id else None
        
        result.append({
            "id": alert.get('id'),
            "user_id": user_id,
            "username": user.get('username', 'Unknown') if user else "Unknown",
            "alert_type": alert.get('alert_type'),
            "severity": alert.get('severity'),
            "message": alert.get('message'),
            "is_resolved": alert.get('is_resolved', False),
            "created_at": alert.get('created_at')
        })
    
    return {"alerts": result}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,  # Changed from int to str
    current_user: dict = Depends(get_current_user)
):
    """Resolve an alert in Firestore"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if alert exists
    alerts = firestore_service.get_alerts()
    alert_exists = any(a.get('id') == alert_id for a in alerts)
    
    if not alert_exists:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    firestore_service.resolve_alert(alert_id)
    
    return {"message": "Alert resolved", "alert_id": alert_id}

@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,  # Changed from int to str
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user profile from Firestore"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = firestore_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get digital twin
    digital_twin = firestore_service.get_digital_twin(user_id)
    
    # Get all sessions
    sessions = firestore_service.get_user_sessions(user_id)
    
    return {
        "user": {
            "id": user.get('id'),
            "username": user.get('username'),
            "email": user.get('email'),
            "phone_number": user.get('phone_number'),
            "created_at": user.get('created_at')
        },
        "digital_twin": digital_twin.get('mental_health_profile') if digital_twin else None,
        "sessions": [
            {
                "id": s.get('id'),
                "type": s.get('session_type'),
                "start_time": s.get('start_time'),
                "depression_score": s.get('depression_score'),
                "risk_level": s.get('risk_level')
            }
            for s in sessions
        ]
    }

