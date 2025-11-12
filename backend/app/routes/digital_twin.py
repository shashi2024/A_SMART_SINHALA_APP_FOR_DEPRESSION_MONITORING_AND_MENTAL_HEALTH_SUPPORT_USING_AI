"""
Digital Twin routes for mental health profile management
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db, User, DigitalTwin, Session as DBSession
from app.routes.auth import get_current_user
from app.services.digital_twin_service import DigitalTwinService

router = APIRouter()

class DigitalTwinResponse(BaseModel):
    user_id: int
    mental_health_profile: Dict[str, Any]
    risk_factors: Dict[str, Any]
    recommendations: list
    last_updated: datetime

@router.get("/profile", response_model=DigitalTwinResponse)
async def get_digital_twin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's digital twin profile"""
    digital_twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == current_user.id).first()
    
    if not digital_twin:
        # Create new digital twin
        twin_service = DigitalTwinService()
        profile = await twin_service.create_profile(current_user.id, db)
        digital_twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == current_user.id).first()
    
    return DigitalTwinResponse(
        user_id=digital_twin.user_id,
        mental_health_profile=json.loads(digital_twin.mental_health_profile) if digital_twin.mental_health_profile else {},
        risk_factors=json.loads(digital_twin.risk_factors) if digital_twin.risk_factors else {},
        recommendations=[],
        last_updated=digital_twin.last_updated
    )

@router.post("/update")
async def update_digital_twin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update digital twin with latest data"""
    twin_service = DigitalTwinService()
    updated_profile = await twin_service.update_profile(current_user.id, db)
    
    return {"message": "Digital twin updated", "profile": updated_profile}

@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics from digital twin"""
    twin_service = DigitalTwinService()
    analytics = await twin_service.get_analytics(current_user.id, db)
    
    return analytics

