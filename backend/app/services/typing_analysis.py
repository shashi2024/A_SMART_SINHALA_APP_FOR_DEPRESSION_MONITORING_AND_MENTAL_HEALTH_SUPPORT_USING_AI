"""
Typing pattern analysis service
"""

import numpy as np
from typing import Dict, Any, List, Optional

class TypingAnalysisService:
    """Service for analyzing typing patterns"""
    
    def __init__(self):
        self.normal_typing_speed = 40  # Words per minute (baseline)
        self.normal_pause_duration = 0.5  # seconds
    
    async def analyze_patterns(
        self,
        keystroke_timings: List[float],
        typing_speed: float,
        pause_duration: float,
        error_rate: float,
        pressure_patterns: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Analyze typing patterns for depression indicators"""
        
        # Calculate features
        timing_variance = np.var(keystroke_timings) if keystroke_timings else 0
        timing_mean = np.mean(keystroke_timings) if keystroke_timings else 0
        
        # Analyze patterns
        depression_score = self._calculate_depression_score(
            typing_speed, pause_duration, error_rate, timing_variance, timing_mean
        )
        
        risk_level = self._get_risk_level(depression_score)
        
        insights = {
            "typing_speed_deviation": typing_speed - self.normal_typing_speed,
            "pause_analysis": "longer_than_normal" if pause_duration > self.normal_pause_duration else "normal",
            "consistency": "inconsistent" if timing_variance > 0.5 else "consistent",
            "error_pattern": "high_errors" if error_rate > 0.1 else "normal"
        }
        
        return {
            "depression_score": float(depression_score),
            "risk_level": risk_level,
            "insights": insights
        }
    
    def _calculate_depression_score(
        self,
        typing_speed: float,
        pause_duration: float,
        error_rate: float,
        timing_variance: float,
        timing_mean: float
    ) -> float:
        """Calculate depression score from typing patterns"""
        # Slower typing indicates potential depression
        speed_factor = max(0, 1 - (typing_speed / self.normal_typing_speed))
        
        # Longer pauses indicate hesitation/depression
        pause_factor = min(1, pause_duration / (self.normal_pause_duration * 2))
        
        # Higher error rate indicates stress
        error_factor = min(1, error_rate * 10)
        
        # Inconsistent timing indicates emotional instability
        variance_factor = min(1, timing_variance / 1.0)
        
        # Weighted combination
        score = (
            speed_factor * 0.3 +
            pause_factor * 0.3 +
            error_factor * 0.2 +
            variance_factor * 0.2
        )
        
        return min(1.0, max(0.0, score))
    
    def _get_risk_level(self, depression_score: float) -> str:
        """Get risk level from depression score"""
        if depression_score >= 0.75:
            return "severe"
        elif depression_score >= 0.5:
            return "high"
        elif depression_score >= 0.25:
            return "moderate"
        else:
            return "low"

