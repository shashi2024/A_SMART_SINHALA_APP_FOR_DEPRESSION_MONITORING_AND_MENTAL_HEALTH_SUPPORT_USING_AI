import json
import os
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Lazy initialization
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

def human_voice_stress_openai(audio_file: Any) -> dict:
    """Analyze an audio file using OpenAI (Whisper + GPT) and return a stress score and level."""
    try:
        client = get_client()

        # 1. Transcribe the audio using Whisper
        # We need to save it to a temporary file because Whisper API expects a file path or file-like object with a name
        import tempfile
        
        # Get extension if possible
        ext = ".m4a"
        if hasattr(audio_file, "filename"):
            _, ext = os.path.splitext(audio_file.filename)
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            if hasattr(audio_file, "file"):
                audio_file.file.seek(0)
                temp_audio.write(audio_file.file.read())
                audio_file.file.seek(0)
            else:
                audio_file.seek(0)
                temp_audio.write(audio_file.read())
                audio_file.seek(0)
            temp_path = temp_audio.name

        try:
            with open(temp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=f
                )
            
            text = transcription.text
            
            # 2. Analyze the transcript for stress/emotional cues
            prompt = (
                "You are a voice-stress analyst. Analyze the following transcript of a person speaking and judge their emotional stress level. "
                "Consider the word choice, repetition, and hesitation if apparent in text. "
                "Return ONLY a JSON object with two keys: 'score' (an integer from 0 to 10, where 10 is maximum stress) "
                "and 'level' (one of: 'low', 'medium', 'high'). "
                "The transcript is: " + text +
                "\nDo not include any other text or markdown formatting. Just the raw JSON object."
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content.strip()
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
                "transcript": text
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "score": None,
            "level": None,
        }
