"""
Digital Twin service for mental health profile management - Using Firestore
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
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
            "created_at": datetime.now(timezone.utc).isoformat()
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
        
        # Get mood check-ins (last 30 days for daily risk updates)
        from datetime import timedelta
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
        mood_checkins = self.firestore_service.get_user_mood_checkins(
            user_id=user_id,
            limit=100,
            start_date=thirty_days_ago
        )
        
        # Build comprehensive profile
        profile = {
            "total_sessions": len(sessions),
            "average_depression_score": self._calculate_avg_score(sessions),
            "voice_analyses_count": len(voice_analyses),
            "typing_analyses_count": len(typing_analyses),
            "mood_checkins_count": len(mood_checkins),
            "risk_level": self._determine_overall_risk(sessions, mood_checkins),
            "trends": self._calculate_trends(sessions),
            "mood_trends": self._calculate_mood_trends(mood_checkins),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        risk_factors = self._identify_risk_factors(sessions, voice_analyses, typing_analyses, mood_checkins)
        
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
    
    def _determine_overall_risk(self, sessions: list, mood_checkins: list = None) -> str:
        """Determine overall risk level including mood check-ins"""
        mood_checkins = mood_checkins or []
        
        # Get risk from sessions
        session_risk = "low"
        if sessions:
            # Sort by start_time (handle both datetime objects and timestamps)
            def get_start_time(s):
                start_time = s.get('start_time')
                if isinstance(start_time, datetime):
                    return start_time
                return datetime.now()  # Fallback
            
            recent_sessions = sorted(sessions, key=get_start_time, reverse=True)[:5]
            risk_levels = [s.get('risk_level') for s in recent_sessions if s.get('risk_level')]
            
            if "severe" in risk_levels:
                session_risk = "severe"
            elif "high" in risk_levels:
                session_risk = "high"
            elif "moderate" in risk_levels:
                session_risk = "moderate"
        
        # Get risk from mood check-ins (last 7 days for daily updates)
        mood_risk = self._calculate_mood_risk(mood_checkins)
        
        # Combine risks - take the higher risk level
        risk_levels_order = ["low", "moderate", "high", "severe"]
        session_index = risk_levels_order.index(session_risk) if session_risk in risk_levels_order else 0
        mood_index = risk_levels_order.index(mood_risk) if mood_risk in risk_levels_order else 0
        
        final_risk_index = max(session_index, mood_index)
        return risk_levels_order[final_risk_index]
    
    def _calculate_mood_risk(self, mood_checkins: list) -> str:
        """Calculate risk level based on mood check-ins"""
        if not mood_checkins:
            return "low"
        
        # Get recent mood check-ins (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        recent_moods = []
        for checkin in mood_checkins:
            created_at = checkin.get('created_at')
            if isinstance(created_at, datetime):
                if created_at >= seven_days_ago:
                    recent_moods.append(checkin.get('mood'))
            elif isinstance(created_at, str):
                try:
                    checkin_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if checkin_time >= seven_days_ago:
                        recent_moods.append(checkin.get('mood'))
                except:
                    pass
        
        if not recent_moods:
            return "low"
        
        # Count negative moods
        negative_moods = ['Sad', 'Anxious']
        negative_count = sum(1 for mood in recent_moods if mood in negative_moods)
        negative_ratio = negative_count / len(recent_moods)
        
        # Determine risk based on mood patterns
        if negative_ratio >= 0.7:  # 70% or more negative moods
            return "severe"
        elif negative_ratio >= 0.5:  # 50-70% negative moods
            return "high"
        elif negative_ratio >= 0.3:  # 30-50% negative moods
            return "moderate"
        else:
            return "low"
    
    def _calculate_mood_trends(self, mood_checkins: list) -> Dict[str, Any]:
        """Calculate mood trends over time"""
        if len(mood_checkins) < 2:
            return {}
        
        # Get moods from last 7 days vs previous 7 days
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)
        
        recent_moods = []
        earlier_moods = []
        
        for checkin in mood_checkins:
            created_at = checkin.get('created_at')
            mood = checkin.get('mood')
            
            if isinstance(created_at, datetime):
                checkin_time = created_at
            elif isinstance(created_at, str):
                try:
                    checkin_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    continue
            else:
                continue
            
            if seven_days_ago <= checkin_time <= now:
                recent_moods.append(mood)
            elif fourteen_days_ago <= checkin_time < seven_days_ago:
                earlier_moods.append(mood)
        
        if not recent_moods or not earlier_moods:
            return {}
        
        # Calculate negative mood ratio
        negative_moods = ['Sad', 'Anxious']
        recent_negative = sum(1 for m in recent_moods if m in negative_moods) / len(recent_moods)
        earlier_negative = sum(1 for m in earlier_moods if m in negative_moods) / len(earlier_moods)
        
        trend = "improving" if recent_negative < earlier_negative else "declining" if recent_negative > earlier_negative else "stable"
        
        return {
            "trend": trend,
            "recent_negative_ratio": recent_negative,
            "earlier_negative_ratio": earlier_negative
        }
    
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
        typing_analyses: list,
        mood_checkins: list = None
    ) -> list:
        """Identify risk factors including mood patterns"""
        mood_checkins = mood_checkins or []
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
        
        # Check mood patterns (last 7 days)
        if mood_checkins:
            from datetime import timedelta
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            recent_moods = []
            for checkin in mood_checkins:
                created_at = checkin.get('created_at')
                if isinstance(created_at, datetime):
                    if created_at >= seven_days_ago:
                        recent_moods.append(checkin.get('mood'))
                elif isinstance(created_at, str):
                    try:
                        checkin_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if checkin_time >= seven_days_ago:
                            recent_moods.append(checkin.get('mood'))
                    except:
                        pass
            
            if recent_moods:
                negative_moods = ['Sad', 'Anxious']
                negative_count = sum(1 for mood in recent_moods if mood in negative_moods)
                negative_ratio = negative_count / len(recent_moods)
                
                if negative_ratio >= 0.7:
                    risk_factors.append("Frequent negative mood check-ins (70%+ in last 7 days)")
                elif negative_ratio >= 0.5:
                    risk_factors.append("Elevated negative mood patterns (50%+ in last 7 days)")
                elif negative_ratio >= 0.3:
                    risk_factors.append("Some negative mood patterns detected (30%+ in last 7 days)")
        
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

