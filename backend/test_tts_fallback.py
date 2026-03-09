import asyncio
import os
import sys
import base64
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.voice_call_service import VoiceCallService
from app.config import settings

async def test_tts_fallback():
    print("Testing OpenAI TTS Fallback...")
    service = VoiceCallService()
    
    # Test text
    test_text = "Hello! This is a test of the Sahana AI voice fallback using OpenAI."
    
    # Force Google TTS to fail by setting client to None after init
    service._tts_client = None
    
    print(f"Generating audio for: '{test_text}'")
    audio_data = service.text_to_speech(test_text, language='en')
    
    if audio_data:
        file_path = "test_tts_output.mp3"
        with open(file_path, "wb") as f:
            f.write(audio_data)
        print(f"✅ Success! Audio saved to {file_path} ({len(audio_data)} bytes)")
    else:
        print("❌ Failed to generate audio.")

if __name__ == "__main__":
    asyncio.run(test_tts_fallback())
