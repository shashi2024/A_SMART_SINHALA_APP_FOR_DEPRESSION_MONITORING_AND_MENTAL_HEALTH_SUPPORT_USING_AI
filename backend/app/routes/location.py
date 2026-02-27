"""
Location tracking routes - Using Firestore
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from firebase_admin import firestore

from app.routes.auth import get_current_user, get_current_user_optional
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    phone_number: Optional[str] = None
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    timestamp: Optional[str] = None

class LocationResponse(BaseModel):
    user_id: str
    username: str
    phone_number: Optional[str]
    latitude: float
    longitude: float
    accuracy: Optional[float]
    last_updated: str
    address: Optional[str] = None

@router.post("/update")
async def update_location(
    location: LocationUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Update user location (can be called from mobile app with phone number)"""
    try:
        user_id = None
        username = "Unknown"
        
        # If authenticated, use current user
        if current_user:
            user_id = current_user.get('id')
            username = current_user.get('username', 'Unknown')
            phone_number = current_user.get('phone_number') or location.phone_number
        elif location.phone_number:
            # Find user by phone number
            user = firestore_service.get_user_by_phone(location.phone_number)
            if user:
                user_id = user.get('id')
                username = user.get('username', 'Unknown')
                phone_number = location.phone_number
            else:
                raise HTTPException(status_code=404, detail="User not found with this phone number")
        else:
            raise HTTPException(status_code=400, detail="Phone number required for unauthenticated requests")
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create location data
        location_data = {
            'user_id': user_id,
            'username': username,
            'phone_number': phone_number,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'accuracy': location.accuracy,
            'altitude': location.altitude,
            'speed': location.speed,
            'timestamp': location.timestamp or datetime.now(timezone.utc).isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        # Save to Firestore in user_locations collection
        location_ref = firestore_service.db.collection('user_locations').document()
        location_data['id'] = location_ref.id
        location_ref.set(location_data)
        
        # Also update the latest location in users collection
        user_ref = firestore_service.db.collection('users').document(user_id)
        user_ref.update({
            'last_location': {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'accuracy': location.accuracy,
                'timestamp': location_data['last_updated']
            },
            'last_location_update': datetime.now(timezone.utc).isoformat()
        })
        
        print(f"[INFO] Location updated for user {username} ({phone_number}): {location.latitude}, {location.longitude}")
        
        return {
            "message": "Location updated successfully",
            "location_id": location_ref.id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update location: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")

@router.get("/all")
async def get_all_locations(
    current_user: dict = Depends(get_current_user)
):
    """Get all user locations (admin/nurse/doctor only)"""
    is_admin = current_user.get('is_admin', False) or current_user.get('is_sub_admin', False)
    is_nurse = current_user.get('role') == 'nurse'
    is_doctor = current_user.get('role') == 'doctor'
    
    if not (is_admin or is_nurse or is_doctor):
        raise HTTPException(status_code=403, detail="Only admins, nurses, and doctors can view locations")
    
    try:
        # Get latest location for each user from users collection
        users_ref = firestore_service.db.collection('users')
        locations = []
        
        for doc in users_ref.stream():
            user_data = doc.to_dict()
            if not user_data:
                continue
            
            # Only include patients (not admins/sub-admins)
            if user_data.get('is_active', True) and not user_data.get('is_admin', False) and not user_data.get('is_sub_admin', False):
                last_location = user_data.get('last_location')
                if last_location:
                    location_info = {
                        'user_id': doc.id,
                        'username': user_data.get('username', 'Unknown'),
                        'email': user_data.get('email', 'N/A'),
                        'phone_number': user_data.get('phone_number'),
                        'latitude': last_location.get('latitude'),
                        'longitude': last_location.get('longitude'),
                        'accuracy': last_location.get('accuracy'),
                        'last_updated': last_location.get('timestamp') or user_data.get('last_location_update', 'N/A'),
                        'address': None  # Can be geocoded later
                    }
                    locations.append(location_info)
        
        return {"locations": locations}
    except Exception as e:
        print(f"[ERROR] Failed to get locations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to retrieve locations")

@router.get("/user/{phone_number}")
async def get_user_location_by_phone(
    phone_number: str,
    current_user: dict = Depends(get_current_user)
):
    """Get location for a specific user by phone number"""
    is_admin = current_user.get('is_admin', False) or current_user.get('is_sub_admin', False)
    is_nurse = current_user.get('role') == 'nurse'
    is_doctor = current_user.get('role') == 'doctor'
    
    if not (is_admin or is_nurse or is_doctor):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        user = firestore_service.get_user_by_phone(phone_number)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        last_location = user.get('last_location')
        if not last_location:
            raise HTTPException(status_code=404, detail="No location data found for this user")
        
        return {
            "user_id": user.get('id'),
            "username": user.get('username', 'Unknown'),
            "phone_number": phone_number,
            "latitude": last_location.get('latitude'),
            "longitude": last_location.get('longitude'),
            "accuracy": last_location.get('accuracy'),
            "last_updated": last_location.get('timestamp') or user.get('last_location_update', 'N/A')
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get user location: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve location")

@router.get("/history/{phone_number}")
async def get_location_history(
    phone_number: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get location history for a user by phone number"""
    is_admin = current_user.get('is_admin', False) or current_user.get('is_sub_admin', False)
    is_nurse = current_user.get('role') == 'nurse'
    is_doctor = current_user.get('role') == 'doctor'
    
    if not (is_admin or is_nurse or is_doctor):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        user = firestore_service.get_user_by_phone(phone_number)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user.get('id')
        
        # Get location history from user_locations collection
        locations_ref = firestore_service.db.collection('user_locations')
        query = locations_ref.where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        
        history = []
        for doc in query.stream():
            loc_data = doc.to_dict()
            history.append({
                'latitude': loc_data.get('latitude'),
                'longitude': loc_data.get('longitude'),
                'accuracy': loc_data.get('accuracy'),
                'timestamp': loc_data.get('timestamp'),
                'speed': loc_data.get('speed'),
                'altitude': loc_data.get('altitude')
            })
        
        return {"history": history}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get location history: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to retrieve location history")

