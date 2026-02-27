"""
Voice Call Service for AI-powered voice chat
Integrates Speech-to-Text, Chatbot, and Text-to-Speech
"""

import base64
import io
from typing import Optional, Dict, Any
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech
from app.services.chatbot_service import ChatbotService

class VoiceCallService:
    """Service for handling voice calls with AI chatbot"""
    
    def __init__(self):
        self.chatbot_service = ChatbotService()
        self._speech_client = None
        self._tts_client = None
        
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
            print("[WARNING] TTS client not available")
            return None
        
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
            print(f"[ERROR] Text-to-speech failed: {e}")
            return None
    
    def process_voice_message(
        self,
        audio_data: bytes,
        user_id: str,
        session_id: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Process incoming voice message:
        1. Convert speech to text
        2. Get chatbot response
        3. Convert response to speech
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
        
        # Step 2: Get chatbot response
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

