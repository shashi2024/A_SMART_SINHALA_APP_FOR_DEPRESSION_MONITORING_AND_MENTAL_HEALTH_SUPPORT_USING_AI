"""
Call Service for managing voice/video calls
Supports counselor calls and AI practice calls (Duolingo-style)
"""

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum
import uuid

from app.services.firestore_service import FirestoreService

class CallType(str, Enum):
    """Types of calls supported"""
    COUNSELOR = "counselor"  # Call with a human counselor
    AI_PRACTICE = "ai_practice"  # Practice call with AI chatbot
    EMERGENCY = "emergency"  # Emergency call

class CallStatus(str, Enum):
    """Call status states"""
    INITIATING = "initiating"
    RINGING = "ringing"
    CONNECTED = "connected"
    ENDED = "ended"
    REJECTED = "rejected"
    MISSED = "missed"
    CANCELLED = "cancelled"

class CallService:
    """Service for managing calls between users and counselors/AI"""
    
    def __init__(self):
        self.firestore_service = FirestoreService()
        # In-memory call tracking (for WebRTC signaling)
        self.active_calls: Dict[str, Dict] = {}
    
    def create_call(
        self,
        caller_id: str,
        call_type: CallType,
        callee_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict:
        """
        Create a new call session
        
        Args:
            caller_id: User ID of the caller
            call_type: Type of call (counselor, ai_practice, emergency)
            callee_id: User ID of callee (for counselor calls)
            language: Language for the call
        
        Returns:
            Call session data
        """
        call_id = str(uuid.uuid4())
        
        call_data = {
            "id": call_id,
            "caller_id": caller_id,
            "callee_id": callee_id if call_type == CallType.COUNSELOR else None,
            "call_type": call_type.value,
            "status": CallStatus.INITIATING.value,
            "language": language,
            "started_at": datetime.utcnow().isoformat(),
            "ended_at": None,
            "duration": 0,
            "webrtc_offer": None,
            "webrtc_answer": None,
            "ice_candidates": []
        }
        
        # Store in Firestore
        self.firestore_service.create_call(call_data)
        
        # Store in memory for signaling
        self.active_calls[call_id] = call_data
        
        return call_data
    
    def get_call(self, call_id: str) -> Optional[Dict]:
        """Get call by ID"""
        # Check memory first
        if call_id in self.active_calls:
            return self.active_calls[call_id]
        
        # Check Firestore
        return self.firestore_service.get_call_by_id(call_id)
    
    def update_call_status(
        self,
        call_id: str,
        status: CallStatus,
        webrtc_offer: Optional[str] = None,
        webrtc_answer: Optional[str] = None,
        ice_candidate: Optional[Dict] = None
    ) -> bool:
        """
        Update call status and WebRTC signaling data
        
        Args:
            call_id: Call ID
            status: New status
            webrtc_offer: WebRTC offer SDP
            webrtc_answer: WebRTC answer SDP
            ice_candidate: ICE candidate data
        
        Returns:
            True if updated successfully
        """
        call = self.get_call(call_id)
        if not call:
            return False
        
        updates = {
            "status": status.value
        }
        
        if webrtc_offer:
            updates["webrtc_offer"] = webrtc_offer
        if webrtc_answer:
            updates["webrtc_answer"] = webrtc_answer
        if ice_candidate:
            # Add ICE candidate to list
            if "ice_candidates" not in call:
                call["ice_candidates"] = []
            call["ice_candidates"].append(ice_candidate)
            updates["ice_candidates"] = call["ice_candidates"]
        
        if status == CallStatus.CONNECTED:
            updates["connected_at"] = datetime.utcnow().isoformat()
        elif status == CallStatus.ENDED:
            updates["ended_at"] = datetime.utcnow().isoformat()
            if "started_at" in call:
                start_time = datetime.fromisoformat(call["started_at"])
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                updates["duration"] = int(duration)
        
        # Update in memory
        if call_id in self.active_calls:
            self.active_calls[call_id].update(updates)
        
        # Update in Firestore
        self.firestore_service.update_call(call_id, updates)
        
        return True
    
    def end_call(self, call_id: str) -> bool:
        """End a call"""
        return self.update_call_status(call_id, CallStatus.ENDED)
    
    def get_user_calls(
        self,
        user_id: str,
        call_type: Optional[CallType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get call history for a user"""
        return self.firestore_service.get_user_calls(user_id, call_type, limit)
    
    def get_available_counselors(self, language: str = "en") -> List[Dict]:
        """
        Get list of available counselors
        
        Args:
            language: Preferred language
        
        Returns:
            List of available counselors
        """
        # This would query Firestore for counselors with status "available"
        # For now, return mock data
        return self.firestore_service.get_available_counselors(language)
    
    def assign_counselor_to_call(
        self,
        call_id: str,
        counselor_id: str
    ) -> bool:
        """Assign a counselor to a call"""
        call = self.get_call(call_id)
        if not call or call["call_type"] != CallType.COUNSELOR.value:
            return False
        
        updates = {
            "callee_id": counselor_id,
            "status": CallStatus.RINGING.value
        }
        
        if call_id in self.active_calls:
            self.active_calls[call_id].update(updates)
        
        self.firestore_service.update_call(call_id, updates)
        return True






