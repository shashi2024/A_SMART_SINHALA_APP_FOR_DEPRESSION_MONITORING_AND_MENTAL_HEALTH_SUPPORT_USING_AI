"""
Voice Call Service for AI-powered voice chat
Integrates Speech-to-Text, Chatbot, and Text-to-Speech
"""

import base64
import io
import os
import tempfile
import json
from typing import Optional, Dict, Any
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech
from app.services.chatbot_service import ChatbotService
from app.services.voice_analysis import VoiceAnalysisService
from app.services.call_bot_detection import CallBotDetectionService
from app.services.fake_detection import FakeDetectionService
from app.services.firestore_service import FirestoreService
from app.services.batch_fake_detection import BatchFakeDetectionService
from openai import OpenAI
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)

class VoiceCallService:
    """Service for handling voice calls with AI chatbot"""
    
    def __init__(self):
        self.chatbot_service = ChatbotService()
        self.firestore_service = FirestoreService()
        self.voice_analysis_service = VoiceAnalysisService()
        self.call_bot_service = CallBotDetectionService()
        self.fake_detection_service = FakeDetectionService()
        self.batch_fake_service = BatchFakeDetectionService()
        self._speech_client = None
        self._tts_client = None
        
        # OpenAI client for fallback (using isolated voice key)
        try:
            from app.config import settings
            self.openai_client = OpenAI(api_key=settings.VOICE_OPENAI_API_KEY)
        except Exception as e:
            print(f"[WARNING] Could not initialize OpenAI client: {e}")
            self.openai_client = None
        
        # Greeting messages by language
        self.greetings = {
            'en': "Hello friend! I'm Sahana, your mental health support assistant. How are you feeling today?",
            'si': "හෙලෝ මිත්‍රයා! මම සහනා, ඔබේ මානසික සෞඛ්‍ය සහාය සහකාරිය. අද ඔබට කොහොමද?",
            'ta': "வணக்கம் நண்பரே! நான் சஹானா, உங்கள் மனநல ஆதரவு உதவியாளர். இன்று நீங்கள் எப்படி உணர்கிறீர்கள்?"
        }
    
    @property
    def speech_client(self):
        """Lazy load speech client"""
        if self._speech_client is None:
            try:
                self._speech_client = speech.SpeechClient()
            except Exception as e:
                print(f"[WARNING] Could not initialize Speech client: {e}")
        return self._speech_client
    
    @property
    def tts_client(self):
        """Lazy load TTS client"""
        if self._tts_client is None:
            try:
                self._tts_client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"[WARNING] Could not initialize TTS client: {e}")
        return self._tts_client
    
    def get_greeting(self, language: str = 'en') -> Dict[str, Any]:
        """Get greeting message with audio"""
        text = self.greetings.get(language, self.greetings['en'])
        
        result = {
            'text': text,
            'audio': None,
            'language': language
        }
        
        # Generate audio
        audio_data = self.text_to_speech(text, language)
        if audio_data:
            result['audio'] = base64.b64encode(audio_data).decode('utf-8')
        
        return result
    
    def speech_to_text(self, audio_data: bytes, language: str = 'en') -> Optional[str]:
        """Convert speech audio to text"""
        if not self.speech_client:
            print("[WARNING] Speech client not available")
            return None
        
        try:
            # Map language codes
            language_codes = {
                'en': 'en-US',
                'si': 'si-LK',
                'ta': 'ta-LK'
            }
            language_code = language_codes.get(language, 'en-US')
            
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcript
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                print(f"[STT] Recognized: {transcript}")
                return transcript
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Speech-to-text failed: {e}")
            return None
    
    def text_to_speech(self, text: str, language: str = 'en') -> Optional[bytes]:
        """Convert text to speech audio"""
        if not self.tts_client:
            print("[WARNING] Google TTS client not available. Trying OpenAI fallback...")
            return self._openai_text_to_speech(text, language)
        
        try:
            # Map language codes and voices
            voice_configs = {
                'en': ('en-US', 'en-US-Neural2-F'),
                'si': ('si-LK', 'si-LK-Standard-A'),
                'ta': ('ta-IN', 'ta-IN-Standard-A')
            }
            
            lang_code, voice_name = voice_configs.get(language, voice_configs['en'])
            
            # Set up synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_name
            )
            
            # Configure audio output
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,  # Slightly slower for clarity
                pitch=0.0
            )
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            print(f"[TTS] Generated audio for: {text[:50]}...")
            return response.audio_content
            
        except Exception as e:
            print(f"[WARNING] Google Text-to-speech failed: {e}. Trying OpenAI fallback...")
            audio = self._openai_text_to_speech(text, language)
            if audio:
                return audio
            
            print(f"[WARNING] OpenAI Text-to-speech failed. Trying gTTS fallback...")
            return self._gtts_text_to_speech(text, language)
    
    def _openai_text_to_speech(self, text: str, language: str = 'en') -> Optional[bytes]:
        """Fallback to OpenAI TTS"""
        if not self.openai_client:
            print("[WARNING] OpenAI client not available for fallback")
            return None
        
        try:
            # Map voices
            # OpenAI doesn't support Sinhala/Tamil officially for all voices, 
            # but 'nova' or 'alloy' work reasonably well for many languages
            voice = "nova" if language in ['si', 'ta'] else "alloy"
            
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            print(f"[TTS] Generated OpenAI audio for: {text[:50]}...")
            return response.content
            
        except Exception as e:
            print(f"[ERROR] OpenAI Text-to-speech failed: {e}")
            return None

    def _gtts_text_to_speech(self, text: str, language: str = 'en') -> Optional[bytes]:
        """Emergency fallback to gTTS (Free, no API key)"""
        try:
            # Map language codes for gTTS
            gtts_lang = language if language in ['en', 'si', 'ta'] else 'en'
            
            # Create gTTS object
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to buffer
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            print(f"[TTS] Generated gTTS audio for: {text[:50]}...")
            return fp.read()
            
        except Exception as e:
            print(f"[ERROR] gTTS failed: {e}")
            return None
    
    async def process_voice_message(
        self,
        audio_data: bytes,
        user_id: str,
        session_id: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Process incoming voice message:
        1. Convert speech to text
        2. Perform biometric analysis
        3. Get chatbot response
        4. Convert response to speech
        """
        result = {
            'user_text': None,
            'bot_text': None,
            'bot_audio': None,
            'language': language,
            'error': None
        }
        
        # Step 1: Speech to Text
        user_text = self.speech_to_text(audio_data, language)
        if not user_text:
            result['error'] = 'Could not understand audio'
            # Return a helpful response
            result['bot_text'] = self._get_retry_message(language)
            audio = self.text_to_speech(result['bot_text'], language)
            if audio:
                result['bot_audio'] = base64.b64encode(audio).decode('utf-8')
            return result
        
        result['user_text'] = user_text
        
        # Step 2: Biometric Analysis (Asynchronous to not block conversation)
        try:
            # We need to save the audio to a temp file for the analysis services
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_path = temp_audio.name
            
            try:
                # Basic voice features
                # Use "english" if language is not "sinhala" or "tamil" for the model
                analysis_lang = language if language in ["sinhala", "tamil", "english"] else "english"
                voice_features = await self.voice_analysis_service.analyze_audio(temp_path, analysis_lang)
                
                # Check for call bot / fake voice
                bot_result = await self.call_bot_service.detect_call_bot(
                    temp_path,
                    language=analysis_lang,
                    voice_features=voice_features,
                    transcript=user_text
                )
                
                fake_result = await self.fake_detection_service.detect_fake_voice(temp_path, voice_features)
                
                is_fake = bot_result.get("is_fake", False) or fake_result.get("is_fake", False)
                fake_confidence = max(bot_result.get("confidence", 0.0), fake_result.get("confidence", 0.0))
                
                # Save analysis to Firestore
                self.firestore_service.create_voice_analysis({
                    'user_id': user_id,
                    'session_id': session_id,
                    'audio_file_path': temp_path,
                    'duration': voice_features.get("duration", 0),
                    'pitch': voice_features.get("pitch", 0),
                    'energy': voice_features.get("energy", 0),
                    'mfcc_features': json.dumps(voice_features.get("mfcc_features", [])),
                    'emotion_detected': voice_features.get("emotion", "neutral"),
                    'depression_indicator': voice_features.get("depression_score", 0),
                    'is_fake': is_fake,
                    'fake_confidence': fake_confidence
                })
                
                # Update user profile with real-time fake status for dashboard
                user_data = self.firestore_service.get_user_by_id(user_id)
                current_fake_status = user_data.get('fake_status', {}) if user_data else {}
                
                if fake_confidence > current_fake_status.get('fake_score', 0):
                    print(f"[BIOMETRICS] Updating real-time fake status for {user_id}: {fake_confidence:.2f}")
                    self.firestore_service.update_user_fake_status(user_id, {
                        'fake_score': fake_confidence,
                        'batch_type': 'voice_realtime',
                        'is_fake': is_fake
                    })
                
                print(f"[BIOMETRICS] Saved voice analysis for user {user_id}, confidence: {fake_confidence:.2f}")
                
            finally:
                # Note: We keep the file in the upload directory if it's production
                # but for simplicity here we just use the temp path
                # In a real system, we'd move it to settings.UPLOAD_DIR
                pass
                
        except Exception as e:
            print(f"[WARNING] Biometric analysis failed: {e}")
            # Don't let biometrics crash the call
        
        # Step 3: Get chatbot response
        try:
            chat_response = self.chatbot_service.get_response(
                message=user_text,
                user_id=user_id,
                session_id=session_id,
                language=language
            )
            bot_text = chat_response.get('response', self._get_error_message(language))
        except Exception as e:
            print(f"[ERROR] Chatbot failed: {e}")
            bot_text = self._get_error_message(language)
        
        result['bot_text'] = bot_text
        
        # Step 3: Text to Speech
        audio = self.text_to_speech(bot_text, language)
        if audio:
            result['bot_audio'] = base64.b64encode(audio).decode('utf-8')
        
        return result
    
    def _get_retry_message(self, language: str) -> str:
        """Get message asking user to repeat"""
        messages = {
            'en': "I'm sorry, I couldn't hear you clearly. Could you please repeat that?",
            'si': "සමාවන්න, මට පැහැදිලිව ඇසුණේ නැහැ. කරුණාකර නැවත කියන්න පුළුවන්ද?",
            'ta': "மன்னிக்கவும், நான் தெளிவாக கேட்கவில்லை. தயவுசெய்து மீண்டும் சொல்ல முடியுமா?"
        }
        return messages.get(language, messages['en'])
    
    def _get_error_message(self, language: str) -> str:
        """Get error message"""
        messages = {
            'en': "I'm having trouble responding right now. Please try again in a moment.",
            'si': "මට දැන් ප්‍රතිචාර දීමට අපහසුයි. කරුණාකර මොහොතකින් නැවත උත්සාහ කරන්න.",
            'ta': "எனக்கு இப்போது பதிலளிப்பதில் சிக்கல் உள்ளது. சிறிது நேரத்தில் மீண்டும் முயற்சிக்கவும்."
        }
        return messages.get(language, messages['en'])


# Singleton instance
voice_call_service = VoiceCallService()

