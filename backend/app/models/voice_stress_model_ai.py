import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# Lazy initialization to avoid startup errors if API key is missing
_client = None


def get_client():
    """Get or create OpenAI client"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def human_voice_stress(audio_file: Any) -> dict:
    """Analyze an audio file-like object and return a stress score (0-10) and level (low/medium/high)."""
    try:
        # Get the file object from FastAPI UploadFile
        if hasattr(audio_file, "file"):
            file_obj = audio_file.file
            filename = getattr(audio_file, "filename", "audio.wav")
        elif hasattr(audio_file, "read"):
            file_obj = audio_file
            filename = getattr(audio_file, "name", "audio.wav")
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

        client = get_client()
        
        # ✅ FIX: OpenAI expects a tuple (filename, file_content, content_type)
        # Read the file content
        file_content = file_obj.read()
        
        # Reset position if needed for future reads
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        
        # Create a tuple with filename and content
        file_tuple = (filename, file_content)
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=file_tuple,
            response_format="text",
        )

        prompt = (
            "You are a voice-stress analyst. Given only the transcript text, infer the stress level. "
            "Return JSON with keys: score (integer 0-10, higher means more stress) and level "
            "(one of: low, medium, high). Respond with JSON only."
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript:\n{transcript}"},
            ],
            temperature=0,
        )

        raw_content = completion.choices[0].message.content
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
