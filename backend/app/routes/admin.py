"""
Admin panel routes for hospital management
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db, User, Session as DBSession, AdminAlert, DigitalTwin
from app.routes.auth import get_current_user

router = APIRouter()

class AlertResponse(BaseModel):
    id: int
    user_id: int
    username: str
    alert_type: str
    severity: str
    message: str
    created_at: datetime

class UserDashboard(BaseModel):
    user_id: int
    username: str
    email: str
    total_sessions: int
    average_depression_score: float
    risk_level: str
    last_activity: datetime

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard data"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all users with their statistics
    users = db.query(User).filter(User.is_active == True).all()
    dashboard_data = []
    
    for user in users:
        sessions = db.query(DBSession).filter(DBSession.user_id == user.id).all()
        total_sessions = len(sessions)
        
        if sessions:
            avg_score = sum(s.depression_score or 0 for s in sessions) / total_sessions
            last_session = max(sessions, key=lambda s: s.start_time)
            risk_level = last_session.risk_level or "low"
            last_activity = last_session.start_time
        else:
            avg_score = 0
            risk_level = "low"
            last_activity = user.created_at
        
        dashboard_data.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "total_sessions": total_sessions,
            "average_depression_score": avg_score,
            "risk_level": risk_level,
            "last_activity": last_activity
        })
    
    return {"users": dashboard_data}

@router.get("/alerts")
async def get_alerts(
    resolved: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin alerts"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(AdminAlert)
    if resolved is not None:
        query = query.filter(AdminAlert.is_resolved == resolved)
    
    alerts = query.order_by(AdminAlert.created_at.desc()).all()
    
    result = []
    for alert in alerts:
        user = db.query(User).filter(User.id == alert.user_id).first()
        result.append({
            "id": alert.id,
            "user_id": alert.user_id,
            "username": user.username if user else "Unknown",
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "is_resolved": alert.is_resolved,
            "created_at": alert.created_at
        })
    
    return {"alerts": result}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alert = db.query(AdminAlert).filter(AdminAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert resolved", "alert_id": alert_id}

@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user profile"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get digital twin
    digital_twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == user_id).first()
    
    # Get all sessions
    sessions = db.query(DBSession).filter(DBSession.user_id == user_id).all()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "created_at": user.created_at
        },
        "digital_twin": digital_twin.mental_health_profile if digital_twin else None,
        "sessions": [
            {
                "id": s.id,
                "type": s.session_type,
                "start_time": s.start_time,
                "depression_score": s.depression_score,
                "risk_level": s.risk_level
            }
            for s in sessions
        ]
    }

