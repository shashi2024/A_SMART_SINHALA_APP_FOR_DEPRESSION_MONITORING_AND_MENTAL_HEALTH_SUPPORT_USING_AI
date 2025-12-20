"""
Digital Twin routes for mental health profile management - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json

from app.routes.auth import get_current_user
from app.services.digital_twin_service import DigitalTwinService
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class DigitalTwinResponse(BaseModel):
    user_id: str  # Changed from int to str for Firestore
    mental_health_profile: Dict[str, Any]
    risk_factors: Dict[str, Any]
    recommendations: list
    last_updated: datetime

@router.get("/profile", response_model=DigitalTwinResponse)
async def get_digital_twin(
    current_user: dict = Depends(get_current_user)
):
    """Get user's digital twin profile from Firestore"""
    user_id = current_user.get('id')
    digital_twin = firestore_service.get_digital_twin(user_id)
    
    if not digital_twin:
        # Create new digital twin
        twin_service = DigitalTwinService()
        profile = await twin_service.create_profile(user_id, None)  # Pass None instead of db
        digital_twin = firestore_service.get_digital_twin(user_id)
    
    # Parse JSON strings if they exist
    mental_health_profile = digital_twin.get('mental_health_profile', {})
    if isinstance(mental_health_profile, str):
        mental_health_profile = json.loads(mental_health_profile)
    
    risk_factors = digital_twin.get('risk_factors', {})
    if isinstance(risk_factors, str):
        risk_factors = json.loads(risk_factors)
    
    return DigitalTwinResponse(
        user_id=user_id,
        mental_health_profile=mental_health_profile or {},
        risk_factors=risk_factors or {},
        recommendations=[],
        last_updated=digital_twin.get('last_updated', datetime.now())
    )

@router.post("/update")
async def update_digital_twin(
    current_user: dict = Depends(get_current_user)
):
    """Update digital twin with latest data in Firestore"""
    user_id = current_user.get('id')
    twin_service = DigitalTwinService()
    updated_profile = await twin_service.update_profile(user_id, None)  # Pass None instead of db
    
    return {"message": "Digital twin updated", "profile": updated_profile}

@router.get("/analytics")
async def get_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get analytics from digital twin in Firestore"""
    user_id = current_user.get('id')
    twin_service = DigitalTwinService()
    analytics = await twin_service.get_analytics(user_id, None)  # Pass None instead of db
    
    return analytics

