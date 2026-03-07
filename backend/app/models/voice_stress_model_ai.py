import json
import os
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Lazy initialization
_client = None

def get_client():
    """Get or create Gemini client"""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client

def human_voice_stress(audio_file: Any) -> dict:
    """Analyze an audio file using Google Gemini and return a stress score and level."""
    try:
        # Get the file content from FastAPI UploadFile or file-like object
        if hasattr(audio_file, "file"):
            file_obj = audio_file.file
        elif hasattr(audio_file, "read"):
            file_obj = audio_file
        else:
            return {
                "status": False,
                "error": "Invalid audio input; expected file-like object",
                "score": None,
                "level": None,
            }

        # Seek to beginning
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        file_content = file_obj.read()
        
        # Reset position
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content_type = getattr(audio_file, "content_type", "audio/mpeg")
        client = get_client()

        prompt = (
            "You are a voice-stress analyst. Analyze the emotional tone and stress level in this audio recording. "
            "Return ONLY a JSON object with two keys: 'score' (an integer from 0 to 10, where 10 is maximum stress) "
            "and 'level' (one of: 'low', 'medium', 'high'). "
            "Do not include any other text or markdown formatting. Just the raw JSON object."
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=content_type),
                prompt
            ]
        )

        raw_content = response.text.strip()
        # Remove potential markdown code blocks
        if raw_content.startswith("```"):
            import re
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                raw_content = json_match.group()

        parsed = json.loads(raw_content)

        score = float(parsed.get("score", 0))
        level = str(parsed.get("level", "medium")).lower()

        score = max(0.0, min(10.0, score))
        if level not in {"low", "medium", "high"}:
            level = "medium"

        return {
            "status": True,
            "error": None,
            "score": score,
            "level": level,
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "score": None,
            "level": None,
        }
