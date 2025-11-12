"""
Chatbot service for handling conversations
"""

import requests
from typing import Optional
from app.config import settings

class ChatbotService:
    """Service for chatbot interactions"""
    
    def __init__(self):
        self.rasa_url = settings.RASA_SERVER_URL
    
    async def get_response(self, message: str, user_id: int) -> str:
        """Get chatbot response for a message"""
        try:
            # Call Rasa server
            response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json={
                    "sender": str(user_id),
                    "message": message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0].get("text", "I'm sorry, I didn't understand that.")
            else:
                return "I'm having trouble processing your message. Please try again."
        
        except Exception as e:
            # Fallback response
            return "I'm here to help. Could you tell me more about how you're feeling?"
    
    async def detect_emotion(self, message: str) -> str:
        """Detect emotion from message"""
        # This would integrate with emotion detection model
        # For now, return a placeholder
        return "neutral"

