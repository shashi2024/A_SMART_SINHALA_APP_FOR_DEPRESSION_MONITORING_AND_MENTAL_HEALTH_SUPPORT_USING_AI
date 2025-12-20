"""
Digital Twin service for mental health profile management - Using Firestore
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.services.firestore_service import FirestoreService

class DigitalTwinService:
    """Service for managing digital twin profiles"""
    
    def __init__(self):
        self.firestore_service = FirestoreService()
    
    async def create_profile(self, user_id: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Create initial digital twin profile in Firestore"""
        profile = {
            "baseline_metrics": {},
            "trends": {},
            "risk_factors": [],
            "strengths": [],
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.firestore_service.create_or_update_digital_twin(user_id, {
            'mental_health_profile': json.dumps(profile),
            'risk_factors': json.dumps([])
        })
        
        return profile
    
    async def update_profile(self, user_id: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Update digital twin with latest data from Firestore"""
        digital_twin = self.firestore_service.get_digital_twin(user_id)
        
        if not digital_twin:
            return await self.create_profile(user_id, db)
        
        # Get all sessions
        sessions = self.firestore_service.get_user_sessions(user_id)
        
        # Get voice analyses
        voice_analyses = self.firestore_service.get_user_voice_analyses(user_id)
        
        # Get typing analyses
        typing_analyses = self.firestore_service.get_user_typing_analyses(user_id)
        
        # Build comprehensive profile
        profile = {
            "total_sessions": len(sessions),
            "average_depression_score": self._calculate_avg_score(sessions),
            "voice_analyses_count": len(voice_analyses),
            "typing_analyses_count": len(typing_analyses),
            "risk_level": self._determine_overall_risk(sessions),
            "trends": self._calculate_trends(sessions),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        risk_factors = self._identify_risk_factors(sessions, voice_analyses, typing_analyses)
        
        # Update in Firestore
        self.firestore_service.create_or_update_digital_twin(user_id, {
            'mental_health_profile': json.dumps(profile),
            'risk_factors': json.dumps(risk_factors)
        })
        
        return profile
    
    async def get_analytics(self, user_id: str, db: Optional[Any] = None) -> Dict[str, Any]:
        """Get analytics from digital twin in Firestore"""
        digital_twin = self.firestore_service.get_digital_twin(user_id)
        
        if not digital_twin:
            return {}
        
        mental_health_profile = digital_twin.get('mental_health_profile', {})
        if isinstance(mental_health_profile, str):
            profile = json.loads(mental_health_profile)
        else:
            profile = mental_health_profile or {}
        
        risk_factors_data = digital_twin.get('risk_factors', [])
        if isinstance(risk_factors_data, str):
            risk_factors = json.loads(risk_factors_data)
        else:
            risk_factors = risk_factors_data or []
        
        return {
            "profile": profile,
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(profile, risk_factors)
        }
    
    def _calculate_avg_score(self, sessions: list) -> float:
        """Calculate average depression score"""
        scores = [s.get('depression_score') for s in sessions if s.get('depression_score') is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _determine_overall_risk(self, sessions: list) -> str:
        """Determine overall risk level"""
        if not sessions:
            return "low"
        
        # Sort by start_time (handle both datetime objects and timestamps)
        def get_start_time(s):
            start_time = s.get('start_time')
            if isinstance(start_time, datetime):
                return start_time
            return datetime.now()  # Fallback
        
        recent_sessions = sorted(sessions, key=get_start_time, reverse=True)[:5]
        risk_levels = [s.get('risk_level') for s in recent_sessions if s.get('risk_level')]
        
        if "severe" in risk_levels:
            return "severe"
        elif "high" in risk_levels:
            return "high"
        elif "moderate" in risk_levels:
            return "moderate"
        else:
            return "low"
    
    def _calculate_trends(self, sessions: list) -> Dict[str, Any]:
        """Calculate trends over time"""
        if len(sessions) < 2:
            return {}
        
        def get_start_time(s):
            start_time = s.get('start_time')
            if isinstance(start_time, datetime):
                return start_time
            return datetime.now()
        
        sorted_sessions = sorted(sessions, key=get_start_time)
        recent_scores = [s.get('depression_score') for s in sorted_sessions[-5:] if s.get('depression_score') is not None]
        earlier_scores = [s.get('depression_score') for s in sorted_sessions[:-5] if s.get('depression_score') is not None]
        
        if not recent_scores or not earlier_scores:
            return {}
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        trend = "improving" if recent_avg < earlier_avg else "declining" if recent_avg > earlier_avg else "stable"
        
        return {
            "trend": trend,
            "change": recent_avg - earlier_avg
        }
    
    def _identify_risk_factors(
        self,
        sessions: list,
        voice_analyses: list,
        typing_analyses: list
    ) -> list:
        """Identify risk factors"""
        risk_factors = []
        
        # Check for high depression scores
        high_scores = [s for s in sessions if s.get('depression_score') and s.get('depression_score') > 0.7]
        if high_scores:
            risk_factors.append("Consistently high depression scores")
        
        # Check for fake detections
        fake_voice = [v for v in voice_analyses if v.get('is_fake', False)]
        fake_typing = [t for t in typing_analyses if t.get('is_fake', False)]
        
        if fake_voice:
            risk_factors.append("Suspicious voice patterns detected")
        if fake_typing:
            risk_factors.append("Suspicious typing patterns detected")
        
        # Check for increasing trend
        trends = self._calculate_trends(sessions)
        if trends.get("trend") == "declining":
            risk_factors.append("Declining mental health trend")
        
        return risk_factors
    
    def _generate_recommendations(self, profile: Dict[str, Any], risk_factors: list) -> list:
        """Generate recommendations based on profile and risk factors"""
        recommendations = []
        
        if risk_factors:
            recommendations.append("Consider professional mental health consultation")
        
        risk_level = profile.get("risk_level", "low")
        if risk_level in ["high", "severe"]:
            recommendations.append("Immediate professional support recommended")
            recommendations.append("Contact emergency services if in crisis")
        
        trends = profile.get("trends", {})
        if trends.get("trend") == "declining":
            recommendations.append("Monitor closely and seek support")
        
        return recommendations

