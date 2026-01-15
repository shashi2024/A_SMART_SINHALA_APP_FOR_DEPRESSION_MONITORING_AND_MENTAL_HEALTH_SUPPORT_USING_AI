"""
Fake call bot detection service for detecting synthetic/automated voices in calls
This service detects when users are using call bots or synthetic voice systems
Integrates custom PyTorch model and algorithm for enhanced detection
"""

import numpy as np
import librosa
from typing import Dict, Any, List, Optional
import os
from scipy import stats
from scipy.signal import find_peaks
import torch
from app.services.algorithm import FakeCallAlgorithm

class CallBotDetectionService:
    """Service for detecting fake call bots and synthetic voices"""
    
    def __init__(self):
        # Thresholds for fake detection
        self.pitch_consistency_threshold = 0.15  # Low variation suggests synthetic
        self.energy_flatness_threshold = 0.1  # Flat energy suggests synthetic
        self.mfcc_anomaly_threshold = 0.7  # High anomaly score suggests fake
        self.spectral_centroid_threshold = 0.12  # Unusual patterns suggest fake
        self.zero_crossing_threshold = 0.08  # Unusual ZCR suggests synthetic
        
        # Combined fake detection threshold
        self.fake_confidence_threshold = 0.65
        
        # Load custom PyTorch model
        self.custom_model = None
        self.model_loaded = False
        self._load_custom_model()
        
        # Initialize algorithm
        self.algorithm = FakeCallAlgorithm()
    
    def _load_custom_model(self):
        """Load custom PyTorch fake call detector model"""
        try:
            # Try multiple possible paths
            possible_paths = [
                os.path.join("models", "fake_call_detector", "fakecall_model.pth"),  # From backend directory
                os.path.join("..", "models", "fake_call_detector", "fakecall_model.pth"),  # From app/services
                os.path.join("backend", "models", "fake_call_detector", "fakecall_model.pth"),  # From project root
                os.path.join(".", "backend", "models", "fake_call_detector", "fakecall_model.pth"),  # Alternative
            ]
            
            model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path and os.path.exists(model_path):
                try:
                    # Load PyTorch model
                    self.custom_model = torch.load(model_path, map_location='cpu')
                    if hasattr(self.custom_model, 'eval'):
                        self.custom_model.eval()  # Set to evaluation mode
                    self.model_loaded = True
                    print(f"[INFO] Loaded custom fake call detector model from {model_path}")
                except Exception as e:
                    print(f"[WARNING] Could not load PyTorch model: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[WARNING] Custom fake call detector model not found at {model_path}. Using rule-based detection only.")
        
        except Exception as e:
            print(f"[ERROR] Error loading custom model: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
    
    def _prepare_features_for_model(self, features: Dict[str, Any]) -> torch.Tensor:
        """
        Prepare audio features in the format expected by the PyTorch model
        Modify this based on your model's expected input format
        """
        # Extract feature vectors - adjust based on your model's input requirements
        feature_vector = []
        
        # Pitch features
        pitch_seq = features.get('pitch_sequence', np.array([0]))
        if len(pitch_seq) > 0:
            feature_vector.extend([
                float(np.mean(pitch_seq)),
                float(np.std(pitch_seq)),
                float(np.min(pitch_seq)),
                float(np.max(pitch_seq))
            ])
        else:
            feature_vector.extend([0.0, 0.0, 0.0, 0.0])
        
        # Energy features
        energy_seq = features.get('energy_sequence', np.array([0]))
        if len(energy_seq) > 0:
            feature_vector.extend([
                float(np.mean(energy_seq)),
                float(np.std(energy_seq))
            ])
        else:
            feature_vector.extend([0.0, 0.0])
        
        # MFCC features (flatten and take statistics)
        mfcc = features.get('mfcc_features', np.array([[0]]))
        if mfcc.size > 0:
            mfcc_flat = mfcc.flatten()
            feature_vector.extend([
                float(np.mean(mfcc_flat)),
                float(np.std(mfcc_flat)),
                float(np.min(mfcc_flat)),
                float(np.max(mfcc_flat))
            ])
        else:
            feature_vector.extend([0.0, 0.0, 0.0, 0.0])
        
        # Spectral features
        spectral_centroids = features.get('spectral_centroids', np.array([0]))
        spectral_rolloff = features.get('spectral_rolloff', np.array([0]))
        spectral_bandwidth = features.get('spectral_bandwidth', np.array([0]))
        
        feature_vector.extend([
            float(np.mean(spectral_centroids)),
            float(np.std(spectral_centroids)),
            float(np.mean(spectral_rolloff)),
            float(np.std(spectral_rolloff)),
            float(np.mean(spectral_bandwidth)),
            float(np.std(spectral_bandwidth))
        ])
        
        # ZCR features
        zcr_seq = features.get('zcr_sequence', np.array([0]))
        if len(zcr_seq) > 0:
            feature_vector.extend([
                float(np.mean(zcr_seq)),
                float(np.std(zcr_seq))
            ])
        else:
            feature_vector.extend([0.0, 0.0])
        
        # Duration
        feature_vector.append(float(features.get('duration', 0)))
        
        # Convert to tensor
        feature_tensor = torch.FloatTensor(feature_vector).unsqueeze(0)  # Add batch dimension
        return feature_tensor
    
    def _predict_with_custom_model(self, features: Dict[str, Any]) -> Optional[float]:
        """
        Use custom PyTorch model to predict fake call probability
        Returns probability (0-1) or None if model not available
        """
        if not self.model_loaded or self.custom_model is None:
            return None
        
        try:
            # Prepare features
            feature_tensor = self._prepare_features_for_model(features)
            
            # Predict
            with torch.no_grad():
                prediction = self.custom_model(feature_tensor)
                
                # Handle different output formats
                if isinstance(prediction, torch.Tensor):
                    prediction = prediction.cpu().numpy()
                
                # Extract probability
                if isinstance(prediction, np.ndarray):
                    if prediction.shape[1] == 1:
                        # Binary classification (fake probability)
                        fake_prob = float(prediction[0][0])
                    else:
                        # Multi-class (e.g., [real_prob, fake_prob])
                        fake_prob = float(prediction[0][1]) if prediction.shape[1] > 1 else float(prediction[0][0])
                    
                    # Apply sigmoid if needed (if model outputs logits)
                    if fake_prob < 0 or fake_prob > 1:
                        fake_prob = 1.0 / (1.0 + np.exp(-fake_prob))  # Sigmoid
                    
                    return float(np.clip(fake_prob, 0.0, 1.0))
                else:
                    return float(prediction) if isinstance(prediction, (int, float)) else None
        
        except Exception as e:
            print(f"[ERROR] Error predicting with custom model: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    async def detect_call_bot(
        self,
        audio_path: str,
        language: str = "sinhala",
        voice_features: Optional[Dict[str, Any]] = None,
        transcript: str = "",
        call_duration_sec: float = 0.0,
        repeat_call_count_last_hour: int = 0,
        depression_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Detect if the call is using a bot or synthetic voice
        Now integrates custom PyTorch model and algorithm
        
        Args:
            audio_path: Path to audio file
            language: Language of the call ('sinhala', 'tamil', 'english')
            voice_features: Pre-computed voice features (optional)
            transcript: Text transcript from speech-to-text
            call_duration_sec: Duration of the call in seconds
            repeat_call_count_last_hour: Number of calls from same user in last hour
            depression_score: Depression score from depression model (optional)
        
        Returns:
            Dictionary with detection results
        """
        try:
            # Load audio if features not provided
            if voice_features is None:
                y, sr = librosa.load(audio_path, sr=22050)
            else:
                y, sr = None, None
                # Extract features from provided data if available
                if 'audio_data' in voice_features:
                    y = voice_features['audio_data']
                    sr = voice_features.get('sample_rate', 22050)
                else:
                    y, sr = librosa.load(audio_path, sr=22050)
            
            # Extract comprehensive features for bot detection
            features = await self._extract_bot_detection_features(y, sr, language)
            
            # Try to use custom PyTorch model first
            p_fake_model = self._predict_with_custom_model(features)
            
            # If model not available, use rule-based detection
            if p_fake_model is None:
                # Fallback to rule-based detection
                pitch_analysis = self._analyze_pitch_consistency(features['pitch_sequence'])
                energy_analysis = self._analyze_energy_patterns(features['energy_sequence'])
                mfcc_analysis = self._analyze_mfcc_anomalies(features['mfcc_features'])
                spectral_analysis = self._analyze_spectral_characteristics(features)
                zcr_analysis = self._analyze_zero_crossing_rate(features['zcr_sequence'])
                formant_analysis = self._analyze_formant_patterns(features['formants'])
                
                bot_indicators = {
                    'pitch_consistency': pitch_analysis['bot_score'],
                    'energy_flatness': energy_analysis['bot_score'],
                    'mfcc_anomalies': mfcc_analysis['bot_score'],
                    'spectral_anomalies': spectral_analysis['bot_score'],
                    'zcr_anomalies': zcr_analysis['bot_score'],
                    'formant_irregularities': formant_analysis['bot_score']
                }
                
                # Calculate overall fake confidence score
                p_fake_model = (
                    bot_indicators['pitch_consistency'] * 0.20 +
                    bot_indicators['energy_flatness'] * 0.15 +
                    bot_indicators['mfcc_anomalies'] * 0.25 +
                    bot_indicators['spectral_anomalies'] * 0.15 +
                    bot_indicators['zcr_anomalies'] * 0.10 +
                    bot_indicators['formant_irregularities'] * 0.15
                )
            
            # Use algorithm to combine model prediction with text and behavior features
            algorithm_result = self.algorithm.analyze_call(
                transcript=transcript,
                p_fake_model=p_fake_model,
                call_duration_sec=call_duration_sec,
                repeat_call_count_last_hour=repeat_call_count_last_hour,
                depression_score=depression_score
            )
            
            # Get final fake score from algorithm
            final_fake_score = algorithm_result.fake_score
            is_fake = final_fake_score >= 0.4  # Use algorithm's threshold
            
            # Determine bot type if fake
            bot_type = None
            if is_fake:
                if final_fake_score >= 0.7:
                    bot_type = "high_risk_fake"
                elif final_fake_score >= 0.4:
                    bot_type = "medium_risk_fake"
                else:
                    bot_type = "low_risk_fake"
            
            # Format result dictionary
            result_dict = self.algorithm.format_result_dict(algorithm_result)
            
            return {
                "is_fake": is_fake,
                "is_call_bot": is_fake,
                "confidence": float(final_fake_score),
                "bot_type": bot_type,
                "risk_label": algorithm_result.risk_label,
                "action": algorithm_result.action,
                "suspicious_words": algorithm_result.suspicious_words,
                "word_contributions": algorithm_result.word_contributions,
                "model_used": "custom_pytorch" if self.model_loaded else "rule_based",
                "base_model_score": float(p_fake_model),
                "algorithm_enhanced_score": float(final_fake_score),
                "language": language,
                "text_features": {
                    "token_count": algorithm_result.text_features.token_count,
                    "nonsense_ratio": algorithm_result.text_features.nonsense_ratio,
                    "unique_word_ratio": algorithm_result.text_features.unique_word_ratio,
                    "joke_word_count": algorithm_result.text_features.joke_word_count,
                    "abuse_word_count": algorithm_result.text_features.abuse_word_count,
                },
                "behavior_features": {
                    "call_duration_sec": algorithm_result.behavior_features.call_duration_sec,
                    "repeat_call_count_last_hour": algorithm_result.behavior_features.repeat_call_count_last_hour,
                }
            }
        
        except Exception as e:
            # Return safe default on error
            print(f"[ERROR] Error in detect_call_bot: {e}")
            import traceback
            traceback.print_exc()
            return {
                "is_fake": False,
                "is_call_bot": False,
                "confidence": 0.0,
                "bot_type": None,
                "risk_label": "low_fake_risk",
                "action": "treat_as_normal",
                "suspicious_words": [],
                "word_contributions": {},
                "error": str(e),
                "language": language
            }
    
    async def _extract_bot_detection_features(
        self,
        y: np.ndarray,
        sr: int,
        language: str
    ) -> Dict[str, Any]:
        """Extract comprehensive features for bot detection"""
        
        # Pitch tracking over time
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_sequence = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_sequence.append(pitch)
        
        # Energy over time
        energy_sequence = librosa.feature.rms(y=y)[0]
        
        # MFCC features
        mfcc_features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        # Zero crossing rate
        zcr_sequence = librosa.feature.zero_crossing_rate(y)[0]
        
        # Formants (simplified - using spectral peaks)
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        formants = []
        for frame in magnitude.T:
            peaks, _ = find_peaks(frame[:len(frame)//2], height=np.max(frame) * 0.1)
            if len(peaks) > 0:
                formant_freqs = librosa.fft_frequencies(sr=sr)[peaks[:3]]  # First 3 formants
                formants.append(formant_freqs)
        
        return {
            'pitch_sequence': np.array(pitch_sequence) if pitch_sequence else np.array([0]),
            'energy_sequence': energy_sequence,
            'mfcc_features': mfcc_features,
            'spectral_centroids': spectral_centroids,
            'spectral_rolloff': spectral_rolloff,
            'spectral_bandwidth': spectral_bandwidth,
            'zcr_sequence': zcr_sequence,
            'formants': formants if formants else [np.array([0, 0, 0])],
            'duration': len(y) / sr
        }
    
    def _analyze_pitch_consistency(self, pitch_sequence: np.ndarray) -> Dict[str, Any]:
        """Analyze pitch consistency - synthetic voices are often too consistent"""
        if len(pitch_sequence) < 2:
            return {'bot_score': 0.0, 'variation': 0.0, 'mean_pitch': 0.0}
        
        mean_pitch = np.mean(pitch_sequence)
        std_pitch = np.std(pitch_sequence)
        cv = std_pitch / mean_pitch if mean_pitch > 0 else 0
        
        # Very low coefficient of variation suggests synthetic voice
        # Real human voices have CV typically > 0.15
        if cv < self.pitch_consistency_threshold:
            bot_score = 1.0 - (cv / self.pitch_consistency_threshold)
        else:
            bot_score = max(0.0, 0.3 - (cv - self.pitch_consistency_threshold) * 2)
        
        return {
            'bot_score': float(min(1.0, max(0.0, bot_score))),
            'variation': float(cv),
            'mean_pitch': float(mean_pitch),
            'std_pitch': float(std_pitch)
        }
    
    def _analyze_energy_patterns(self, energy_sequence: np.ndarray) -> Dict[str, Any]:
        """Analyze energy patterns - synthetic voices often have flat energy"""
        if len(energy_sequence) < 2:
            return {'bot_score': 0.0, 'flatness': 0.0}
        
        # Calculate energy variation
        energy_std = np.std(energy_sequence)
        energy_mean = np.mean(energy_sequence)
        flatness = energy_std / energy_mean if energy_mean > 0 else 0
        
        # Very flat energy suggests synthetic
        if flatness < self.energy_flatness_threshold:
            bot_score = 1.0 - (flatness / self.energy_flatness_threshold)
        else:
            bot_score = max(0.0, 0.2 - (flatness - self.energy_flatness_threshold) * 2)
        
        return {
            'bot_score': float(min(1.0, max(0.0, bot_score))),
            'flatness': float(flatness),
            'mean_energy': float(energy_mean),
            'std_energy': float(energy_std)
        }
    
    def _analyze_mfcc_anomalies(self, mfcc_features: np.ndarray) -> Dict[str, Any]:
        """Analyze MFCC features for synthetic patterns"""
        if mfcc_features.size == 0:
            return {'bot_score': 0.0, 'anomaly_score': 0.0}
        
        # Calculate MFCC statistics
        mfcc_mean = np.mean(mfcc_features, axis=1)
        mfcc_std = np.std(mfcc_features, axis=1)
        
        # Synthetic voices often have unusual MFCC patterns
        # Check for unusual variance patterns
        variance_pattern = np.var(mfcc_std)
        
        # Normalize anomaly score
        anomaly_score = min(1.0, variance_pattern / 0.5)
        
        # Check for too-regular patterns (synthetic)
        regularity = 1.0 - (np.std(mfcc_std) / (np.mean(mfcc_std) + 1e-6))
        regularity_score = max(0.0, regularity)
        
        bot_score = (anomaly_score * 0.4 + regularity_score * 0.6)
        
        return {
            'bot_score': float(min(1.0, max(0.0, bot_score))),
            'anomaly_score': float(anomaly_score),
            'regularity_score': float(regularity_score)
        }
    
    def _analyze_spectral_characteristics(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spectral characteristics for bot detection"""
        spectral_centroids = features['spectral_centroids']
        spectral_rolloff = features['spectral_rolloff']
        spectral_bandwidth = features['spectral_bandwidth']
        
        # Calculate variation in spectral features
        centroid_cv = np.std(spectral_centroids) / (np.mean(spectral_centroids) + 1e-6)
        rolloff_cv = np.std(spectral_rolloff) / (np.mean(spectral_rolloff) + 1e-6)
        bandwidth_cv = np.std(spectral_bandwidth) / (np.mean(spectral_bandwidth) + 1e-6)
        
        # Synthetic voices often have unusual spectral patterns
        avg_cv = (centroid_cv + rolloff_cv + bandwidth_cv) / 3
        
        if avg_cv < self.spectral_centroid_threshold:
            bot_score = 1.0 - (avg_cv / self.spectral_centroid_threshold)
        else:
            bot_score = max(0.0, 0.3 - (avg_cv - self.spectral_centroid_threshold) * 2)
        
        return {
            'bot_score': float(min(1.0, max(0.0, bot_score))),
            'centroid_variation': float(centroid_cv),
            'rolloff_variation': float(rolloff_cv),
            'bandwidth_variation': float(bandwidth_cv)
        }
    
    def _analyze_zero_crossing_rate(self, zcr_sequence: np.ndarray) -> Dict[str, Any]:
        """Analyze zero crossing rate for bot detection"""
        if len(zcr_sequence) < 2:
            return {'bot_score': 0.0, 'variation': 0.0}
        
        zcr_mean = np.mean(zcr_sequence)
        zcr_std = np.std(zcr_sequence)
        zcr_cv = zcr_std / (zcr_mean + 1e-6)
        
        # Synthetic voices may have unusual ZCR patterns
        if zcr_cv < self.zero_crossing_threshold:
            bot_score = 1.0 - (zcr_cv / self.zero_crossing_threshold)
        else:
            bot_score = max(0.0, 0.2 - (zcr_cv - self.zero_crossing_threshold) * 2)
        
        return {
            'bot_score': float(min(1.0, max(0.0, bot_score))),
            'variation': float(zcr_cv),
            'mean_zcr': float(zcr_mean)
        }
    
    def _analyze_formant_patterns(self, formants: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze formant patterns for bot detection"""
        if not formants or len(formants) == 0:
            return {'bot_score': 0.0, 'irregularity': 0.0}
        
        # Extract first formant (F1) values
        f1_values = [f[0] if len(f) > 0 and f[0] > 0 else 0 for f in formants]
        f1_values = [f for f in f1_values if f > 0]
        
        if len(f1_values) < 2:
            return {'bot_score': 0.0, 'irregularity': 0.0}
        
        # Calculate formant variation
        f1_mean = np.mean(f1_values)
        f1_std = np.std(f1_values)
        f1_cv = f1_std / (f1_mean + 1e-6)
        
        # Too consistent formants suggest synthetic
        if f1_cv < 0.1:
            bot_score = 0.8
        elif f1_cv < 0.15:
            bot_score = 0.5
        else:
            bot_score = 0.2
        
        return {
            'bot_score': float(bot_score),
            'irregularity': float(f1_cv),
            'mean_f1': float(f1_mean)
        }
    
    def _classify_bot_type(
        self,
        bot_indicators: Dict[str, float],
        features: Dict[str, Any]
    ) -> str:
        """Classify the type of bot detected"""
        # High pitch consistency + high energy flatness = TTS bot
        if (bot_indicators['pitch_consistency'] > 0.7 and 
            bot_indicators['energy_flatness'] > 0.6):
            return "tts_synthetic"
        
        # High MFCC anomalies = Voice cloning bot
        if bot_indicators['mfcc_anomalies'] > 0.7:
            return "voice_cloning"
        
        # High spectral anomalies = Automated call system
        if bot_indicators['spectral_anomalies'] > 0.7:
            return "automated_call_system"
        
        # General bot
        return "unknown_bot"

