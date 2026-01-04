"""
Enhanced Chatbot Service with PHQ-9, Safety Guardrails, and Controlled Responses
Hybrid approach: Rule-based + Pattern matching (NO full LLM access)
"""

import re
from typing import Dict, Optional, Tuple, List
from app.services.phq9_service import PHQ9Service
from app.services.chatbot_safety import ChatbotSafetyService
from app.services.depression_detection import DepressionDetectionService

class ChatbotService:
    """Enhanced chatbot service with safety and PHQ-9 support"""
    
    # Intent patterns for detecting user intent
    INTENT_PATTERNS = {
        'start_phq9': {
            'en': [r'phq', r'questionnaire', r'assessment', r'screening', r'test', r'evaluate'],
            'si': [r'ප්‍රශ්නාවලිය', r'ඇගයීම', r'පරීක්ෂණය'],
            'ta': [r'கேள்வி', r'மதிப்பீடு', r'சோதனை']
        },
        'want_to_chat': {
            'en': [r'chat', r'talk', r'conversation', r'speak', r'discuss'],
            'si': [r'කතා', r'සංවාද', r'අදහස්'],
            'ta': [r'பேச', r'உரையாடல்', r'விவாத']
        },
        'greeting': {
            'en': [r'hello', r'hi', r'hey', r'good morning', r'good evening'],
            'si': [r'හෙලෝ', r'ආයුබෝවන්', r'කොහොමද'],
            'ta': [r'வணக்கம்', r'வணக்க', r'எப்படி']
        },
        'feeling_sad': {
            'en': [r'sad', r'depressed', r'down', r'hopeless', r'unhappy', r'miserable'],
            'si': [r'දුක්බර', r'කම්පනය', r'නිරාශාව', r'කනගාටුව'],
            'ta': [r'வருத்தம்', r'மனச்சோர்வு', r'விரக்தி', r'சோகம்']
        },
        'feeling_anxious': {
            'en': [r'anxious', r'worried', r'nervous', r'stressed', r'panic'],
            'si': [r'කලබල', r'කරදර', r'පීඩාව', r'බිය'],
            'ta': [r'கவலை', r'பதட்டம்', r'பயம்', r'ஆத்திரம்']
        },
        'need_help': {
            'en': [r'help', r'support', r'assistance', r'need help', r'can you help'],
            'si': [r'උදව්', r'සහාය', r'ආධාරය'],
            'ta': [r'உதவி', r'ஆதரவு', r'ஆதரவு']
        }
    }
    
    # Response templates by intent and language
    RESPONSE_TEMPLATES = {
        'greeting': {
            'en': [
                "Hello! I'm here to support you. Would you like to take a quick mental health assessment (PHQ-9), or would you prefer to chat freely?",
                "Hi there! I'm here to listen. How can I help you today? You can take a mental health assessment or just chat with me.",
                "Welcome! I'm here to help. Would you like to start with a mental health questionnaire, or would you prefer to have a conversation?"
            ],
            'si': [
                "ආයුබෝවන්! මම ඔබට සහාය වීමට මෙහි සිටිමි. ඔබට මානසික සෞඛ්‍ය ඇගයීමක් (PHQ-9) කිරීමට අවශ්‍යද, නැතහොත් නිදහසේ කතා කිරීමට අවශ්‍යද?",
                "ආයුබෝවන්! මම ඔබට සවන් දීමට මෙහි සිටිමි. අද මම ඔබට කෙසේ උදව් කළ හැකිද? ඔබට මානසික සෞඛ්‍ය ඇගයීමක් කිරීමට හෝ මා සමඟ කතා කිරීමට හැකියි.",
                "සාදරයෙන් පිළිගනිමු! මම උදව් කිරීමට මෙහි සිටිමි. ඔබට මානසික සෞඛ්‍ය ප්‍රශ්නාවලියකින් ආරම්භ කිරීමට අවශ්‍යද, නැතහොත් සංවාදයක් කිරීමට අවශ්‍යද?"
            ],
            'ta': [
                "வணக்கம்! நான் உங்களுக்கு ஆதரவளிக்க இங்கே இருக்கிறேன். நீங்கள் விரைவான மனநல மதிப்பீட்டை (PHQ-9) எடுக்க விரும்புகிறீர்களா, அல்லது சுதந்திரமாக பேச விரும்புகிறீர்களா?",
                "வணக்கம்! நான் கேட்க இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்? நீங்கள் மனநல மதிப்பீட்டை எடுக்கலாம் அல்லது என்னுடன் பேசலாம்.",
                "வரவேற்கிறோம்! நான் உதவ இங்கே இருக்கிறேன். நீங்கள் மனநல கேள்வித்தாளுடன் தொடங்க விரும்புகிறீர்களா, அல்லது உரையாடலை விரும்புகிறீர்களா?"
            ]
        },
        'feeling_sad': {
            'en': [
                "I'm sorry you're feeling this way. It takes courage to share these feelings. Would you like to talk more about what's making you feel sad?",
                "Thank you for sharing that with me. Feeling sad can be really difficult. I'm here to listen. What's been going on?",
                "I understand that feeling sad can be overwhelming. You're not alone in this. Would you like to continue talking about it?"
            ],
            'si': [
                "ඔබ මේ ආකාරයට හැඟෙනවාට කණගාටුයි. මෙම හැඟීම් බෙදාගැනීමට නිර්භීතකම අවශ්‍යයි. ඔබට දුක්බර හැඟීමට හේතුව ගැන තවත් කතා කිරීමට අවශ්‍යද?",
                "මා සමඟ එය බෙදාගැනීමට ස්තුතියි. දුක්බර හැඟීම ඇත්තෙන්ම අපහසු විය හැකියි. මම මෙහි සවන් දෙනවා. කුමක් සිදුවෙමින් තිබුණාද?",
                "දුක්බර හැඟීම අධික විය හැකි බව මට තේරෙනවා. මෙය තුළ ඔබ තනි නොවේ. ඔබට එය ගැන කතා කිරීම දිගටම කරගෙන යාමට අවශ්‍යද?"
            ],
            'ta': [
                "நீங்கள் இப்படி உணர்வதற்கு வருந்துகிறேன். இந்த உணர்வுகளைப் பகிர்ந்து கொள்ள தைரியம் தேவை. உங்களை சோகமாக உணர வைக்கும் விஷயத்தைப் பற்றி மேலும் பேச விரும்புகிறீர்களா?",
                "அதை என்னுடன் பகிர்ந்தமைக்கு நன்றி. சோகமாக உணர்வது மிகவும் கடினமாக இருக்கும். நான் கேட்க இங்கே இருக்கிறேன். என்ன நடந்து கொண்டிருக்கிறது?",
                "சோகமாக உணர்வது அதிகமாக இருக்கும் என்பதை நான் புரிந்துகொள்கிறேன். இதில் நீங்கள் தனியாக இல்லை. அதைப் பற்றி தொடர்ந்து பேச விரும்புகிறீர்களா?"
            ]
        },
        'feeling_anxious': {
            'en': [
                "Feeling anxious can be really challenging. I'm here to listen. What's been making you feel anxious?",
                "Thank you for sharing that. Anxiety can feel overwhelming. Would you like to talk about what's been worrying you?",
                "I understand that anxiety can be difficult to manage. You're not alone. What would be most helpful right now?"
            ],
            'si': [
                "කලබල වීම ඇත්තෙන්ම අභියෝගයක් විය හැකියි. මම මෙහි සවන් දෙනවා. ඔබට කලබල වීමට හේතුව කුමක්ද?",
                "එය බෙදාගැනීමට ස්තුතියි. කලබලය අධික විය හැකියි. ඔබට කරදර වන දේ ගැන කතා කිරීමට අවශ්‍යද?",
                "කලබලය කළමනාකරණය කිරීම අපහසු විය හැකි බව මට තේරෙනවා. ඔබ තනි නොවේ. දැන් වඩාත්ම ප්‍රයෝජනවත් වන්නේ කුමක්ද?"
            ],
            'ta': [
                "பதட்டமாக உணர்வது மிகவும் சவாலானதாக இருக்கும். நான் கேட்க இங்கே இருக்கிறேன். உங்களை பதட்டமாக உணர வைக்கும் விஷயம் என்ன?",
                "அதை பகிர்ந்தமைக்கு நன்றி. பதட்டம் அதிகமாக இருக்கும். உங்களை கவலைப்படுத்தும் விஷயத்தைப் பற்றி பேச விரும்புகிறீர்களா?",
                "பதட்டத்தை நிர்வகிப்பது கடினமாக இருக்கும் என்பதை நான் புரிந்துகொள்கிறேன். நீங்கள் தனியாக இல்லை. இப்போது மிகவும் உதவியாக இருக்கும் என்ன?"
            ]
        },
        'need_help': {
            'en': [
                "I'm here to help. Would you like to take a mental health assessment, or would you prefer to chat about what's on your mind?",
                "Of course, I'm here to support you. What would be most helpful right now?",
                "I'm ready to help. How can I best support you today?"
            ],
            'si': [
                "මම උදව් කිරීමට මෙහි සිටිමි. ඔබට මානසික සෞඛ්‍ය ඇගයීමක් කිරීමට අවශ්‍යද, නැතහොත් ඔබේ හිතේ ඇති දේ ගැන කතා කිරීමට අවශ්‍යද?",
                "ඇත්තෙන්ම, මම ඔබට සහාය වීමට මෙහි සිටිමි. දැන් වඩාත්ම ප්‍රයෝජනවත් වන්නේ කුමක්ද?",
                "මම උදව් කිරීමට සූදානම්. අද මම ඔබට හොඳම ආධාරය කළ හැක්කේ කෙසේද?"
            ],
            'ta': [
                "நான் உதவ இங்கே இருக்கிறேன். நீங்கள் மனநல மதிப்பீட்டை எடுக்க விரும்புகிறீர்களா, அல்லது உங்கள் மனதில் உள்ளதைப் பற்றி பேச விரும்புகிறீர்களா?",
                "நிச்சயமாக, நான் உங்களுக்கு ஆதரவளிக்க இங்கே இருக்கிறேன். இப்போது மிகவும் உதவியாக இருக்கும் என்ன?",
                "நான் உதவ தயாராக இருக்கிறேன். இன்று நான் உங்களுக்கு சிறந்த ஆதரவை எவ்வாறு வழங்க முடியும்?"
            ]
        },
        'default': {
            'en': [
                "I'm here to listen. Can you tell me more about how you're feeling?",
                "Thank you for sharing. How does that make you feel?",
                "I understand. Would you like to continue talking about it?",
                "That sounds challenging. I'm here to support you. What would be helpful?"
            ],
            'si': [
                "මම මෙහි සවන් දෙනවා. ඔබට හැඟෙන ආකාරය ගැන තවත් කියන්න පුළුවන්ද?",
                "බෙදාගැනීමට ස්තුතියි. එය ඔබට කෙසේ හැඟෙනවාද?",
                "මට තේරෙනවා. ඔබට එය ගැන කතා කිරීම දිගටම කරගෙන යාමට අවශ්‍යද?",
                "එය අභියෝගයක් විය හැකියි. මම ඔබට සහාය වීමට මෙහි සිටිමි. කුමක් ප්‍රයෝජනවත් වේද?"
            ],
            'ta': [
                "நான் கேட்க இங்கே இருக்கிறேன். நீங்கள் எப்படி உணர்கிறீர்கள் என்பதைப் பற்றி மேலும் சொல்ல முடியுமா?",
                "பகிர்ந்தமைக்கு நன்றி. அது உங்களுக்கு எப்படி உணர்த்துகிறது?",
                "நான் புரிந்துகொள்கிறேன். அதைப் பற்றி தொடர்ந்து பேச விரும்புகிறீர்களா?",
                "அது சவாலானது போல் தெரிகிறது. நான் உங்களுக்கு ஆதரவளிக்க இங்கே இருக்கிறேன். என்ன உதவியாக இருக்கும்?"
            ]
        }
    }
    
    def __init__(self):
        self.phq9_service = PHQ9Service()
        self.safety_service = ChatbotSafetyService()
        self.depression_service = DepressionDetectionService()
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text (simple heuristic)
        Returns: 'en', 'si', or 'ta'
        """
        # Check for Sinhala characters
        if re.search(r'[\u0D80-\u0DFF]', text):
            return 'si'
        # Check for Tamil characters
        elif re.search(r'[\u0B80-\u0BFF]', text):
            return 'ta'
        # Default to English
        else:
            return 'en'
    
    def detect_intent(self, message: str, language: str) -> str:
        """
        Detect user intent from message using pattern matching
        Returns: intent name or 'default'
        """
        message_lower = message.lower()
        lang = language.lower()[:2]
        
        # Check each intent pattern
        for intent, patterns in self.INTENT_PATTERNS.items():
            if lang in patterns:
                for pattern in patterns[lang]:
                    if re.search(pattern, message_lower):
                        return intent
        
        return 'default'
    
    def get_response_template(self, intent: str, language: str) -> str:
        """
        Get response template for intent and language
        Returns random template from available options
        """
        import random
        
        lang = language.lower()[:2]
        if lang not in ['en', 'si', 'ta']:
            lang = 'en'
        
        # Get templates for intent, fallback to default
        templates = self.RESPONSE_TEMPLATES.get(intent, {}).get(lang, [])
        if not templates:
            templates = self.RESPONSE_TEMPLATES.get('default', {}).get(lang, [])
        
        if templates:
            return random.choice(templates)
        
        # Ultimate fallback
        return self.safety_service.get_safe_response(language)
    
    async def get_response(
        self, 
        message: str, 
        user_id: str,
        session_context: Optional[Dict] = None,
        language: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get chatbot response with safety checks and depression detection
        Returns dict with response, metadata, and safety flags
        """
        # Detect language if not provided
        if not language:
            language = self.detect_language(message)
        
        # Safety check - CRISIS DETECTION (highest priority)
        is_crisis = self.safety_service.detect_crisis(message, language)
        if is_crisis:
            return {
                "response": self.safety_service.get_crisis_message(language),
                "is_crisis": True,
                "needs_escalation": True,
                "risk_level": "severe",
                "language": language,
                "intent": "crisis"
            }
        
        # Safety analysis
        safety_analysis = self.safety_service.analyze_message_safety(message, language)
        
        # Detect intent
        intent = self.detect_intent(message, language)
        
        # Get response template
        response = self.get_response_template(intent, language)
        
        # Validate response safety
        is_safe, error = self.safety_service.validate_response(response, language)
        if not is_safe:
            # Use safe fallback
            response = self.safety_service.get_safe_response(language)
        
        # Depression detection from message
        depression_score = await self.depression_service.analyze_text(message)
        risk_level = self.depression_service.get_risk_level(depression_score)
        
        # Check if escalation needed based on depression score
        needs_escalation = safety_analysis["needs_escalation"] or risk_level in ["high", "severe"]
        
        # Add escalation message if needed
        if needs_escalation and not is_crisis:
            escalation_msg = self.safety_service.get_escalation_message(language)
            response = f"{response}\n\n{escalation_msg}"
        
        return {
            "response": response,
            "is_crisis": False,
            "needs_escalation": needs_escalation,
            "risk_level": risk_level,
            "depression_score": depression_score,
            "language": language,
            "intent": intent,
            "safety_analysis": safety_analysis
        }
    
    async def detect_emotion(self, message: str) -> str:
        """
        Detect emotion from message
        Returns: emotion label
        """
        # Simple emotion detection based on keywords
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['sad', 'depressed', 'hopeless', 'down']):
            return "sad"
        elif any(word in message_lower for word in ['anxious', 'worried', 'nervous', 'stressed']):
            return "anxious"
        elif any(word in message_lower for word in ['angry', 'frustrated', 'mad', 'irritated']):
            return "angry"
        elif any(word in message_lower for word in ['happy', 'good', 'great', 'fine', 'well']):
            return "happy"
        else:
            return "neutral"
