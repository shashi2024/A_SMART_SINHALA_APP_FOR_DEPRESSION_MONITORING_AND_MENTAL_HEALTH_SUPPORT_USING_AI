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


def human_face_expression(image_file: Any) -> dict:
    """Analyze an image file-like object and return the predicted facial expression."""
    try:
        # Get the file object from FastAPI UploadFile
        if hasattr(image_file, "file"):
            file_obj = image_file.file
            filename = getattr(image_file, "filename", "image.jpg")
        elif hasattr(image_file, "read"):
            file_obj = image_file
            filename = getattr(image_file, "name", "image.jpg")
        else:
            return {
                "status": False,
                "error": "Invalid image input; expected file-like object",
                "expression": None,
            }

        # Seek to beginning
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        client = get_client()

        # Read the file content
        file_content = file_obj.read()

        # Reset position if needed for future reads
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        # Create base64 encoded image for OpenAI vision API
        import base64
        try:
            image_base64 = base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode image to base64: {e}")

        # Determine content type (assume jpeg if not specified)
        content_type = getattr(image_file, "content_type", "image/jpeg")
        if not content_type.startswith('image/'):
            content_type = "image/jpeg"

        # Check if image is too large (OpenAI has limits)
        if len(image_base64) > 20 * 1024 * 1024:  # 20MB limit
            raise ValueError("Image is too large. Maximum size is 20MB.")

        prompt = (
            "You are a facial expression analyst. Analyze the facial expression in this image and classify it as exactly one of these emotions: "
            "angry, fear, happy, neutral, sad, surprise. "
            "Return ONLY a JSON object with this exact format: {\"expression\": \"emotion_name\"}. "
            "Do not include any other text, explanations, or formatting. Just the JSON object."
        )

        completion = client.chat.completions.create(
            model="gpt-4o",  # Use gpt-4o for better vision capabilities
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is the facial expression in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
        )

        raw_content = completion.choices[0].message.content
        
        # Debug: print the raw response
        print(f"OpenAI raw response: '{raw_content}'")
        
        # Validate response
        if not raw_content or not raw_content.strip():
            raise ValueError("Empty response from OpenAI API")
        
        # Try to parse JSON, with fallback cleaning
        try:
            parsed = json.loads(raw_content.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response if it contains extra text
            import re
            json_match = re.search(r'\{.*\}', raw_content.strip())
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    # Fallback: try to extract emotion from text
                    text_lower = raw_content.lower()
                    for emotion in ["angry", "fear", "happy", "neutral", "sad", "surprise"]:
                        if emotion in text_lower:
                            parsed = {"expression": emotion}
                            break
                    else:
                        raise ValueError(f"Could not parse JSON or extract emotion from response: {raw_content}")
            else:
                # Fallback: try to extract emotion from text
                text_lower = raw_content.lower()
                for emotion in ["angry", "fear", "happy", "neutral", "sad", "surprise"]:
                    if emotion in text_lower:
                        parsed = {"expression": emotion}
                        break
                else:
                    raise ValueError(f"No JSON found and could not extract emotion from response: {raw_content}")

        expression = str(parsed.get("expression", "neutral")).lower()

        # Validate that the expression is one of the allowed values
        allowed_expressions = {"angry", "fear", "happy", "neutral", "sad", "surprise"}
        if expression not in allowed_expressions:
            expression = "neutral"

        # Map expression to stress level
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
