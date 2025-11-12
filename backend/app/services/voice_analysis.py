"""
Voice analysis service for audio processing
"""

import numpy as np
import librosa
from typing import Dict, Any
import os

class VoiceAnalysisService:
    """Service for analyzing voice patterns"""
    
    def __init__(self):
        self.sample_rate = 22050
    
    async def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio file for depression indicators"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = len(y) / sr
            
            # Extract features
            pitch = self._extract_pitch(y, sr)
            energy = self._extract_energy(y)
            mfcc_features = self._extract_mfcc(y, sr)
            
            # Analyze for depression
            depression_score = self._calculate_depression_score(
                pitch, energy, mfcc_features, duration
            )
            
            # Detect emotion
            emotion = self._detect_emotion(mfcc_features, pitch, energy)
            
            # Determine risk level
            risk_level = self._get_risk_level(depression_score)
            
            # Generate recommendations
            recommendations = self._get_recommendations(depression_score, risk_level)
            
            return {
                "duration": duration,
                "pitch": float(pitch),
                "energy": float(energy),
                "mfcc_features": mfcc_features.tolist() if isinstance(mfcc_features, np.ndarray) else mfcc_features,
                "emotion": emotion,
                "depression_score": float(depression_score),
                "risk_level": risk_level,
                "recommendations": recommendations
            }
        
        except Exception as e:
            # Return default values on error
            return {
                "duration": 0,
                "pitch": 0,
                "energy": 0,
                "mfcc_features": [],
                "emotion": "neutral",
                "depression_score": 0.5,
                "risk_level": "moderate",
                "recommendations": []
            }
    
    def _extract_pitch(self, y: np.ndarray, sr: int) -> float:
        """Extract pitch from audio"""
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        return np.mean(pitch_values) if pitch_values else 0
    
    def _extract_energy(self, y: np.ndarray) -> float:
        """Extract energy from audio"""
        return float(np.mean(librosa.feature.rms(y=y)[0]))
    
    def _extract_mfcc(self, y: np.ndarray, sr: int, n_mfcc: int = 13) -> np.ndarray:
        """Extract MFCC features"""
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        return np.mean(mfccs, axis=1)
    
    def _calculate_depression_score(
        self, pitch: float, energy: float, mfcc_features: np.ndarray, duration: float
    ) -> float:
        """Calculate depression score from features"""
        # This is a simplified version - in production, use trained ML model
        # Lower pitch and energy typically indicate depression
        pitch_factor = max(0, 1 - (pitch / 300))  # Normalize pitch
        energy_factor = max(0, 1 - (energy * 10))  # Normalize energy
        
        # Combine factors (weighted average)
        score = (pitch_factor * 0.4 + energy_factor * 0.4 + 0.2) / 1.0
        return min(1.0, max(0.0, score))
    
    def _detect_emotion(self, mfcc_features: np.ndarray, pitch: float, energy: float) -> str:
        """Detect emotion from voice features"""
        # Simplified emotion detection
        if energy < 0.1 and pitch < 150:
            return "sad"
        elif energy > 0.3 and pitch > 250:
            return "happy"
        elif energy > 0.2:
            return "neutral"
        else:
            return "calm"
    
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
    
    def _get_recommendations(self, depression_score: float, risk_level: str) -> list:
        """Get recommendations based on depression score"""
        recommendations = []
        
        if risk_level == "severe":
            recommendations.append("Please consider speaking with a mental health professional immediately.")
            recommendations.append("Contact emergency services if you're in crisis.")
        elif risk_level == "high":
            recommendations.append("Consider scheduling an appointment with a therapist.")
            recommendations.append("Practice mindfulness and relaxation techniques.")
        elif risk_level == "moderate":
            recommendations.append("Engage in regular physical activity.")
            recommendations.append("Maintain a regular sleep schedule.")
        else:
            recommendations.append("Continue monitoring your mental health.")
            recommendations.append("Practice self-care activities.")
        
        return recommendations

