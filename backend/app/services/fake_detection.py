"""
Fake user detection service for voice and typing patterns
"""

import numpy as np
from typing import Dict, Any, List

class FakeDetectionService:
    """Service for detecting fake users"""
    
    def __init__(self):
        self.voice_threshold = 0.7  # Confidence threshold for fake voice
        self.typing_threshold = 0.6  # Confidence threshold for fake typing
    
    async def detect_fake_voice(self, audio_path: str, voice_features: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if voice is fake or synthetic"""
        try:
            # Check for synthetic voice patterns
            pitch_consistency = self._check_pitch_consistency(voice_features.get("pitch", 0))
            energy_patterns = self._check_energy_patterns(voice_features.get("energy", 0))
            mfcc_anomalies = self._check_mfcc_anomalies(voice_features.get("mfcc_features", []))
            
            # Combine indicators
            fake_score = (
                pitch_consistency * 0.3 +
                energy_patterns * 0.3 +
                mfcc_anomalies * 0.4
            )
            
            is_fake = fake_score > self.voice_threshold
            
            return {
                "is_fake": is_fake,
                "confidence": float(fake_score),
                "indicators": {
                    "pitch_consistency": pitch_consistency,
                    "energy_patterns": energy_patterns,
                    "mfcc_anomalies": mfcc_anomalies
                }
            }
        
        except Exception as e:
            return {
                "is_fake": False,
                "confidence": 0.0,
                "indicators": {}
            }
    
    async def detect_fake_typing(
        self,
        keystroke_timings: List[float],
        typing_speed: float,
        pause_duration: float
    ) -> Dict[str, Any]:
        """Detect if typing patterns are fake or automated"""
        try:
            # Check for robotic patterns
            timing_regularity = self._check_timing_regularity(keystroke_timings)
            speed_consistency = self._check_speed_consistency(typing_speed)
            pause_patterns = self._check_pause_patterns(pause_duration)
            
            # Combine indicators
            fake_score = (
                timing_regularity * 0.4 +
                speed_consistency * 0.3 +
                pause_patterns * 0.3
            )
            
            is_fake = fake_score > self.typing_threshold
            
            return {
                "is_fake": is_fake,
                "confidence": float(fake_score),
                "indicators": {
                    "timing_regularity": timing_regularity,
                    "speed_consistency": speed_consistency,
                    "pause_patterns": pause_patterns
                }
            }
        
        except Exception as e:
            return {
                "is_fake": False,
                "confidence": 0.0,
                "indicators": {}
            }
    
    def _check_pitch_consistency(self, pitch: float) -> float:
        """Check if pitch is too consistent (synthetic)"""
        # Real voices have natural variation
        # Too consistent pitch suggests synthetic voice
        # This is simplified - in production, analyze pitch variation over time
        return 0.3  # Placeholder
    
    def _check_energy_patterns(self, energy: float) -> float:
        """Check energy patterns for anomalies"""
        # Real voices have natural energy variations
        # Flat energy suggests synthetic
        return 0.2  # Placeholder
    
    def _check_mfcc_anomalies(self, mfcc_features: List[float]) -> float:
        """Check MFCC features for synthetic patterns"""
        if not mfcc_features:
            return 0.0
        
        # Check for unusual patterns in MFCC
        # Synthetic voices often have distinct MFCC signatures
        variance = np.var(mfcc_features) if isinstance(mfcc_features, (list, np.ndarray)) else 0
        return min(1.0, variance / 10.0)  # Normalized variance
    
    def _check_timing_regularity(self, timings: List[float]) -> float:
        """Check if keystroke timings are too regular (robotic)"""
        if not timings or len(timings) < 2:
            return 0.0
        
        # Calculate coefficient of variation
        mean_timing = np.mean(timings)
        std_timing = np.std(timings)
        
        if mean_timing == 0:
            return 0.0
        
        cv = std_timing / mean_timing
        
        # Very low CV suggests robotic typing
        # Normal human typing has CV around 0.2-0.5
        if cv < 0.1:
            return 0.8  # Highly regular, likely fake
        elif cv < 0.15:
            return 0.5  # Somewhat regular
        else:
            return 0.2  # Natural variation
    
    def _check_speed_consistency(self, speed: float) -> float:
        """Check if typing speed is too consistent"""
        # Real users have speed variations
        # This would need historical data for comparison
        return 0.3  # Placeholder
    
    def _check_pause_patterns(self, pause_duration: float) -> float:
        """Check pause patterns for anomalies"""
        # Real users have natural pause variations
        # Too uniform pauses suggest automation
        return 0.2  # Placeholder

