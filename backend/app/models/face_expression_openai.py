import json
import os
import base64
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

def human_face_expression_openai(image_file: Any) -> dict:
    """Analyze an image using OpenAI GPT-4o and return the predicted facial expression."""
    try:
        # Get the file content
        if hasattr(image_file, "file"):
            file_obj = image_file.file
        elif hasattr(image_file, "read"):
            file_obj = image_file
        else:
            return {
                "status": False,
                "error": "Invalid image input; expected file-like object",
                "expression": None,
            }

        # Seek to beginning
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        file_content = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        # Encode to base64
        base64_image = base64.b64encode(file_content).decode('utf-8')
        content_type = getattr(image_file, "content_type", "image/jpeg")

        client = get_client()

        prompt = (
            "You are a facial expression analyst. Analyze the facial expression in this image and classify it as exactly one of these emotions: "
            "angry, fear, happy, neutral, sad, surprise. "
            "Return ONLY a JSON object with this exact format: {\"expression\": \"emotion_name\"}. "
            "Do not include any other text or markdown formatting. Just the raw JSON object."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content.strip()
        parsed = json.loads(raw_content)
        expression = str(parsed.get("expression", "neutral")).lower()

        # Validate allowed expressions
        allowed_expressions = {"angry", "fear", "happy", "neutral", "sad", "surprise"}
        if expression not in allowed_expressions:
            expression = "neutral"

        # Map to stress level
        stress_level_map = {
            "angry": "high",
            "fear": "high",
            "happy": "low",
            "neutral": "low",
            "sad": "medium",
            "surprise": "medium"
        }
        stress_level = stress_level_map.get(expression, "medium")

        return {
            "status": True,
            "error": None,
            "expression": expression,
            "stress_level": stress_level
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "expression": None,
            "stress_level": None,
        }
