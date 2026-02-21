"""
LLM Service for Dynamic Chatbot Responses using Google Gemini
"""

import os
from google import genai
from google.genai import types
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service to handle interactions with Google Gemini LLM"""
    
    def __init__(self):
        from app.config import settings
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables. LLM features will be disabled.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            
    async def generate_response(
        self, 
        user_message: str, 
        language: str = 'en',
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a response using Gemini
        """
        if not self.client:
            return None
            
        try:
            # Construct system prompt based on language
            system_instruction = self._get_system_instruction(language)
            
            # Construct prompt
            prompt = user_message
            if context:
                prompt = f"Context: {context}\n\n{user_message}"
                
            # Generate response with retry logic
            from google.genai.errors import ClientError
            
            max_retries = 3
            base_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        )
                    )
                    return response.text
                except ClientError as e:
                    if e.code == 429 and attempt < max_retries - 1:
                        import asyncio
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited (429). Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return None
            
    def _get_system_instruction(self, language: str) -> str:
        """Get system instruction based on language"""
        base_instruction = """
        You are a compassionate, empathetic mental health support companion for the 1926 National Mental Health Helpline in Sri Lanka.
        
        CRITICAL SAFETY RULES:
        1. NEVER give medical advice, diagnoses, or prescribe medication.
        2. IF the user mentions suicide, self-harm, or immediate danger, you must NOT provide counseling. Instead, gently urge them to contact the 1926 hotline immediately.
        3. Maintain a warm, non-judgmental, and supportive tone.
        4. Keep responses concise (2-3 sentences max usually) to encourage conversation.
        5. Use active listening techniques.
        """
        
        if language == 'si':
            return base_instruction + "\n\nIMPORTANT: Respond in SINHALA (සිංහල). Use natural, spoken-style Sinhala that is warm and empathetic."
        elif language == 'ta':
            return base_instruction + "\n\nIMPORTANT: Respond in TAMIL (தமிழ்). Use natural, spoken-style Tamil that is warm and empathetic."
        else:
            return base_instruction + "\n\nIMPORTANT: Respond in ENGLISH."
