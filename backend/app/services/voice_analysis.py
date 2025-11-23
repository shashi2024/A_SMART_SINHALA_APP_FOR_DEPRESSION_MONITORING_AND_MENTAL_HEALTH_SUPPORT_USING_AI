"""
Voice analysis service for audio processing with depression detection
Supports Sinhala, Tamil, and English languages
Integrates with pre-trained depression recognition models
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path
import pickle
import tensorflow as tf
from google.cloud import speech
from google.cloud import texttospeech

class VoiceAnalysisService:
    """Service for analyzing voice patterns with depression detection"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.depression_model = None
        self.speech_client = None
        self.tts_client = None
        
        # Language codes for Google Speech-to-Text
        self.language_codes = {
            "sinhala": "si-LK",  # Sinhala (Sri Lanka)
            "tamil": "ta-IN",    # Tamil (India) - can use ta-LK for Sri Lanka
            "english": "en-US"
        }
        
        # Load depression model if available
        self._load_depression_model()
        self._initialize_speech_services()
    
    def _load_depression_model(self):
        """Load pre-trained depression recognition model"""
        try:
            model_path = os.getenv("DEPRESSION_MODEL_PATH", "./models/depression_model")
            
            # Try to load TensorFlow model
            if os.path.exists(f"{model_path}.h5") or os.path.exists(f"{model_path}/saved_model.pb"):
                try:
                    self.depression_model = tf.keras.models.load_model(model_path)
                    print(f"Loaded depression model from {model_path}")
                except Exception as e:
                    print(f"Could not load TensorFlow model: {e}")
            
            # Try to load pickle model (scikit-learn)
            if self.depression_model is None and os.path.exists(f"{model_path}.pkl"):
                try:
                    with open(f"{model_path}.pkl", "rb") as f:
                        self.depression_model = pickle.load(f)
                    print(f"Loaded depression model from {model_path}.pkl")
                except Exception as e:
                    print(f"Could not load pickle model: {e}")
            
            # If model from GitHub repo is available - check multiple possible paths
            if self.depression_model is None:
                # List of possible model directory paths
                possible_paths = [
                    "./models/Depression_Recognition",  # Original GitHub repo name
                    "./models/depression_recognision",  # User's directory (with spelling variation)
                    "./models/depression_recognition",  # Alternative spelling
                    "./models/Depression_Recognision",  # Capitalized version
                ]
                
                for github_model_path in possible_paths:
                    if os.path.exists(github_model_path):
                        print(f"Searching for model in: {github_model_path}")
                        # Try to find and load the model
                        for root, dirs, files in os.walk(github_model_path):
                            for file in files:
                                if file.endswith(('.h5', '.pkl', '.pb', '.keras')):
                                    model_file_path = os.path.join(root, file)
                                    try:
                                        if file.endswith(('.h5', '.keras')):
                                            self.depression_model = tf.keras.models.load_model(
                                                model_file_path
                                            )
                                            print(f"Loaded TensorFlow model from: {model_file_path}")
                                        elif file.endswith('.pkl'):
                                            with open(model_file_path, "rb") as f:
                                                self.depression_model = pickle.load(f)
                                            print(f"Loaded scikit-learn model from: {model_file_path}")
                                        elif file.endswith('.pb'):
                                            # SavedModel format
                                            self.depression_model = tf.keras.models.load_model(
                                                root  # Load from directory containing saved_model.pb
                                            )
                                            print(f"Loaded SavedModel from: {root}")
                                        
                                        if self.depression_model:
                                            break
                                    except Exception as e:
                                        print(f"Error loading model from {model_file_path}: {e}")
                                        continue
                            
                            if self.depression_model:
                                break
                    
                    if self.depression_model:
                        break
        
        except Exception as e:
            print(f"Error loading depression model: {e}")
            self.depression_model = None
    
    def _initialize_speech_services(self):
        """Initialize Google Cloud Speech-to-Text and Text-to-Speech clients"""
        try:
            # Only initialize if credentials are available
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                self.speech_client = speech.SpeechClient()
                self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Could not initialize Google Speech services: {e}")
            self.speech_client = None
            self.tts_client = None
    
    async def analyze_audio(
        self,
        audio_path: str,
        language: str = "sinhala"
    ) -> Dict[str, Any]:
        """
        Analyze audio file for depression indicators
        
        Args:
            audio_path: Path to audio file
            language: Language of the audio ('sinhala', 'tamil', 'english')
        
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = len(y) / sr
            
            # Extract features
            pitch = self._extract_pitch(y, sr)
            energy = self._extract_energy(y)
            mfcc_features = self._extract_mfcc(y, sr)
            spectral_features = self._extract_spectral_features(y, sr)
            
            # Transcribe audio to text (for text-based depression analysis)
            transcription = await self._transcribe_audio(audio_path, language)
            
            # Analyze for depression using model
            depression_score = await self._calculate_depression_score(
                pitch, energy, mfcc_features, spectral_features,
                transcription, language, duration
            )
            
            # Detect emotion
            emotion = self._detect_emotion(mfcc_features, pitch, energy, spectral_features)
            
            # Determine risk level
            risk_level = self._get_risk_level(depression_score)
            
            # Generate recommendations (in the selected language)
            recommendations = self._get_recommendations(
                depression_score, risk_level, language
            )
            
            return {
                "duration": duration,
                "pitch": float(pitch),
                "energy": float(energy),
                "mfcc_features": mfcc_features.tolist() if isinstance(mfcc_features, np.ndarray) else mfcc_features,
                "spectral_features": spectral_features,
                "emotion": emotion,
                "depression_score": float(depression_score),
                "risk_level": risk_level,
                "recommendations": recommendations,
                "transcription": transcription,
                "language": language
            }
        
        except Exception as e:
            # Return default values on error
            return {
                "duration": 0,
                "pitch": 0,
                "energy": 0,
                "mfcc_features": [],
                "spectral_features": {},
                "emotion": "neutral",
                "depression_score": 0.5,
                "risk_level": "moderate",
                "recommendations": [],
                "transcription": "",
                "language": language,
                "error": str(e)
            }
    
    async def _transcribe_audio(self, audio_path: str, language: str) -> str:
        """Transcribe audio to text using speech-to-text"""
        try:
            # Use Google Speech-to-Text if available
            if self.speech_client:
                language_code = self.language_codes.get(language.lower(), "en-US")
                
                with open(audio_path, "rb") as audio_file:
                    content = audio_file.read()
                
                audio = speech.RecognitionAudio(content=content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                )
                
                response = self.speech_client.recognize(config=config, audio=audio)
                
                if response.results:
                    return " ".join([result.alternatives[0].transcript 
                                    for result in response.results])
            
            # Fallback: return empty string if transcription not available
            return ""
        
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
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
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features"""
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
        
        return {
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "spectral_bandwidth": float(spectral_bandwidth),
            "zero_crossing_rate": float(zero_crossing_rate)
        }
    
    async def _calculate_depression_score(
        self,
        pitch: float,
        energy: float,
        mfcc_features: np.ndarray,
        spectral_features: Dict[str, float],
        transcription: str,
        language: str,
        duration: float
    ) -> float:
        """Calculate depression score using pre-trained model or fallback"""
        
        # If model is available, use it
        if self.depression_model is not None:
            try:
                # Prepare features for model
                feature_vector = self._prepare_features_for_model(
                    pitch, energy, mfcc_features, spectral_features, duration
                )
                
                # Predict using model
                if hasattr(self.depression_model, 'predict'):
                    prediction = self.depression_model.predict(
                        feature_vector.reshape(1, -1),
                        verbose=0
                    )
                    # Handle different model output formats
                    if isinstance(prediction, np.ndarray):
                        if prediction.shape[1] > 1:
                            # Multi-class: use probability of depression class
                            depression_score = float(prediction[0][1] if prediction.shape[1] > 1 else prediction[0][0])
                        else:
                            depression_score = float(prediction[0][0])
                    else:
                        depression_score = float(prediction)
                    
                    # Normalize to 0-1 range
                    depression_score = max(0.0, min(1.0, depression_score))
                    return depression_score
            except Exception as e:
                print(f"Error using depression model: {e}")
        
        # Fallback: rule-based depression detection
        return self._rule_based_depression_score(
            pitch, energy, mfcc_features, spectral_features, transcription, language
        )
    
    def _prepare_features_for_model(
        self,
        pitch: float,
        energy: float,
        mfcc_features: np.ndarray,
        spectral_features: Dict[str, float],
        duration: float
    ) -> np.ndarray:
        """Prepare feature vector for model input"""
        # Combine all features into a single vector
        features = [
            pitch,
            energy,
            duration,
            spectral_features["spectral_centroid"],
            spectral_features["spectral_rolloff"],
            spectral_features["spectral_bandwidth"],
            spectral_features["zero_crossing_rate"]
        ]
        
        # Add MFCC features
        if isinstance(mfcc_features, np.ndarray):
            features.extend(mfcc_features.tolist())
        else:
            features.extend(mfcc_features)
        
        return np.array(features)
    
    def _rule_based_depression_score(
        self,
        pitch: float,
        energy: float,
        mfcc_features: np.ndarray,
        spectral_features: Dict[str, float],
        transcription: str,
        language: str
    ) -> float:
        """Rule-based depression score calculation (fallback)"""
        
        # Lower pitch and energy typically indicate depression
        pitch_factor = max(0, 1 - (pitch / 300))  # Normalize pitch
        energy_factor = max(0, 1 - (energy * 10))  # Normalize energy
        
        # Lower spectral centroid suggests depression
        spectral_factor = max(0, 1 - (spectral_features["spectral_centroid"] / 3000))
        
        # Text-based analysis (if transcription available)
        text_factor = 0.0
        if transcription:
            # Language-specific depression keywords
            depression_keywords = self._get_depression_keywords(language)
            text_lower = transcription.lower()
            keyword_count = sum(1 for keyword in depression_keywords if keyword in text_lower)
            text_factor = min(1.0, keyword_count / 5.0)
        
        # Combine factors (weighted average)
        score = (
            pitch_factor * 0.25 +
            energy_factor * 0.25 +
            spectral_factor * 0.20 +
            text_factor * 0.30
        )
        
        return min(1.0, max(0.0, score))
    
    def _get_depression_keywords(self, language: str) -> list:
        """Get depression-related keywords for the specified language"""
        keywords = {
            "sinhala": [
                "දුක්", "නිරාශාව", "අවශ්‍යතාවයක්", "කම්පනය", "වේදනාව",
                "අවධානය", "අපේක්ෂාව", "සිතුවිලි", "කණගාටු", "බිය"
            ],
            "tamil": [
                "வருத்தம்", "நம்பிக்கையின்மை", "வேதனை", "தனிமை", "கவலை",
                "பயம்", "ஆற்றாமை", "விரக்தி", "சோர்வு", "வெறுப்பு"
            ],
            "english": [
                "sad", "depressed", "hopeless", "worthless", "tired", "empty",
                "suicide", "death", "pain", "lonely", "anxious", "worried"
            ]
        }
        return keywords.get(language.lower(), keywords["english"])
    
    def _detect_emotion(
        self,
        mfcc_features: np.ndarray,
        pitch: float,
        energy: float,
        spectral_features: Dict[str, float]
    ) -> str:
        """Detect emotion from voice features"""
        # Enhanced emotion detection
        if energy < 0.1 and pitch < 150:
            return "sad"
        elif energy > 0.3 and pitch > 250:
            return "happy"
        elif energy > 0.2 and spectral_features["spectral_centroid"] > 2000:
            return "neutral"
        elif energy < 0.15:
            return "calm"
        else:
            return "neutral"
    
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
    
    def _get_recommendations(
        self,
        depression_score: float,
        risk_level: str,
        language: str
    ) -> list:
        """Get recommendations based on depression score in the selected language"""
        recommendations = []
        
        if language.lower() == "sinhala":
            if risk_level == "severe":
                recommendations.append("කරුණාකර මානසික සෞඛ්‍ය වෛද්‍යවරයෙකු සමඟ කතා කිරීම සලකා බලන්න.")
                recommendations.append("අර්බුදයකදී හදිසි සේවා සමඟ සම්බන්ධ වන්න.")
            elif risk_level == "high":
                recommendations.append("චිකිත්සකයෙකු සමඟ රැස්වීමක් සැලසුම් කිරීම සලකා බලන්න.")
                recommendations.append("සිහිනය හා සන්සුන් කිරීමේ ක්‍රම පුරුදු කරන්න.")
            elif risk_level == "moderate":
                recommendations.append("නිතිපතා ශාරීරික ක්‍රියාකාරකම්වල නිරත වන්න.")
                recommendations.append("නිතිපතා නිදන කාලසටහනක් පවත්වා ගන්න.")
            else:
                recommendations.append("ඔබේ මානසික සෞඛ්‍යය නිරීක්ෂණය කරගෙන යන්න.")
                recommendations.append("ස්වයං සැලකිලි ක්‍රියාකාරකම් පුරුදු කරන්න.")
        
        elif language.lower() == "tamil":
            if risk_level == "severe":
                recommendations.append("தயவுசெய்து மனநல வல்லுநருடன் பேசுவதைக் கருத்தில் கொள்ளுங்கள்.")
                recommendations.append("நெருக்கடியின் போது அவசர சேவைகளைத் தொடர்பு கொள்ளுங்கள்.")
            elif risk_level == "high":
                recommendations.append("ஒரு சிகிச்சையாளருடன் சந்திப்பைத் திட்டமிடுவதைக் கருத்தில் கொள்ளுங்கள்.")
                recommendations.append("மனநிறைவு மற்றும் நிதானமான நுட்பங்களைப் பயிற்சி செய்யுங்கள்.")
            elif risk_level == "moderate":
                recommendations.append("வழக்கமான உடல் செயல்பாடுகளில் ஈடுபடுங்கள்.")
                recommendations.append("வழக்கமான தூக்க அட்டவணையை பராமரிக்கவும்.")
            else:
                recommendations.append("உங்கள் மனநலத்தை கண்காணித்து வரவும்.")
                recommendations.append("சுய பராமரிப்பு நடவடிக்கைகளைப் பயிற்சி செய்யுங்கள்.")
        
        else:  # English
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
