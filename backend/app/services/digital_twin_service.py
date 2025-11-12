"""
Digital Twin service for mental health profile management
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import DigitalTwin, Session as DBSession, VoiceAnalysis, TypingAnalysis

class DigitalTwinService:
    """Service for managing digital twin profiles"""
    
    async def create_profile(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Create initial digital twin profile"""
        profile = {
            "baseline_metrics": {},
            "trends": {},
            "risk_factors": [],
            "strengths": [],
            "created_at": datetime.utcnow().isoformat()
        }
        
        digital_twin = DigitalTwin(
            user_id=user_id,
            mental_health_profile=json.dumps(profile),
            risk_factors=json.dumps([]),
            last_updated=datetime.utcnow()
        )
        
        db.add(digital_twin)
        db.commit()
        db.refresh(digital_twin)
        
        return profile
    
    async def update_profile(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Update digital twin with latest data"""
        digital_twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == user_id).first()
        
        if not digital_twin:
            return await self.create_profile(user_id, db)
        
        # Get all sessions
        sessions = db.query(DBSession).filter(DBSession.user_id == user_id).all()
        
        # Get voice analyses
        voice_analyses = db.query(VoiceAnalysis).filter(VoiceAnalysis.user_id == user_id).all()
        
        # Get typing analyses
        typing_analyses = db.query(TypingAnalysis).filter(TypingAnalysis.user_id == user_id).all()
        
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
        
        digital_twin.mental_health_profile = json.dumps(profile)
        digital_twin.risk_factors = json.dumps(risk_factors)
        digital_twin.last_updated = datetime.utcnow()
        
        db.commit()
        
        return profile
    
    async def get_analytics(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get analytics from digital twin"""
        digital_twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == user_id).first()
        
        if not digital_twin:
            return {}
        
        profile = json.loads(digital_twin.mental_health_profile) if digital_twin.mental_health_profile else {}
        risk_factors = json.loads(digital_twin.risk_factors) if digital_twin.risk_factors else []
        
        return {
            "profile": profile,
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(profile, risk_factors)
        }
    
    def _calculate_avg_score(self, sessions: list) -> float:
        """Calculate average depression score"""
        scores = [s.depression_score for s in sessions if s.depression_score is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _determine_overall_risk(self, sessions: list) -> str:
        """Determine overall risk level"""
        if not sessions:
            return "low"
        
        recent_sessions = sorted(sessions, key=lambda s: s.start_time, reverse=True)[:5]
        risk_levels = [s.risk_level for s in recent_sessions if s.risk_level]
        
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
        
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
        recent_scores = [s.depression_score for s in sorted_sessions[-5:] if s.depression_score is not None]
        earlier_scores = [s.depression_score for s in sorted_sessions[:-5] if s.depression_score is not None]
        
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
        high_scores = [s for s in sessions if s.depression_score and s.depression_score > 0.7]
        if high_scores:
            risk_factors.append("Consistently high depression scores")
        
        # Check for fake detections
        fake_voice = [v for v in voice_analyses if v.is_fake]
        fake_typing = [t for t in typing_analyses if t.is_fake]
        
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

