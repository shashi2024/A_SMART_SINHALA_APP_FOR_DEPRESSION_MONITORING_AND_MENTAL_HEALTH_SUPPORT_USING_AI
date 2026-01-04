"""
Chatbot Safety Guardrails
Filters responses to prevent medical advice and harmful content
"""

import re
from typing import Dict, List, Tuple, Optional

class ChatbotSafetyService:
    """Service for ensuring chatbot responses are safe and controlled"""
    
    # Medical advice keywords to block
    MEDICAL_ADVICE_KEYWORDS = {
        'en': [
            'prescribe', 'medication', 'drug', 'pill', 'dosage', 'take this medicine',
            'diagnosis', 'diagnose', 'you have', 'you are suffering from',
            'treatment plan', 'therapy technique', 'exercise this way',
            'you should take', 'recommend you take', 'try this medication'
        ],
        'si': [
            'වෛද්‍ය', 'ඖෂධ', 'ගත යුතු', 'නිර්දේශ', 'රෝග විනිශ්චය',
            'ඖෂධයක්', 'ප්‍රතිකාර', 'ඔබට ඇති', 'ඔබ පෙළෙනවා'
        ],
        'ta': [
            'மருந்து', 'மாத்திரை', 'சிகிச்சை', 'நோயறிதல்',
            'உங்களுக்கு உள்ளது', 'நீங்கள் பாதிக்கப்பட்டுள்ளீர்கள்'
        ]
    }
    
    # Suicide/self-harm keywords (IMMEDIATE ESCALATION)
    CRISIS_KEYWORDS = {
        'en': [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'hurt myself', 'cut myself', 'overdose', 'jump off',
            'no reason to live', 'better off dead', 'self harm'
        ],
        'si': [
            'ආත්ම ඝාතනය', 'මාව මරාගන්න', 'මිය යන්න', 'ජීවිතය අවසන්',
            'මාවම හානි', 'කපාගන්න', 'මරණය'
        ],
        'ta': [
            'தற்கொலை', 'நானே கொல்ல', 'இறக்க', 'வாழ்வில் அர்த்தம் இல்லை',
            'தற்கொலை செய்து', 'நானே வலி'
        ]
    }
    
    # Harmful suggestions to block
    HARMFUL_SUGGESTIONS = {
        'en': [
            'just ignore it', 'it\'s all in your head', 'snap out of it',
            'you\'re being dramatic', 'others have it worse'
        ],
        'si': [
            'එය නොසලකා හරින්න', 'එය සියල්ල හිසේ', 'එයින් ඉවත් වන්න'
        ],
        'ta': [
            'அதை புறக்கணிக்க', 'அது எல்லாம் உங்கள் தலையில்', 'வெளியேற'
        ]
    }
    
    # Safe empathetic responses (whitelist)
    SAFE_RESPONSES = {
        'en': [
            "I understand this is difficult. I'm here to listen.",
            "Thank you for sharing. How does that make you feel?",
            "That sounds really challenging. Would you like to talk more about it?",
            "I'm sorry you're going through this. You're not alone.",
            "It takes courage to talk about these feelings. Thank you for trusting me.",
            "I can hear that this is really affecting you. Let's explore this together.",
            "Your feelings are valid. Would you like to continue talking?",
            "I'm here to support you. What would be most helpful right now?",
            "Thank you for being open with me. How can I best support you?",
            "I appreciate you sharing this with me. Let's take this one step at a time."
        ],
        'si': [
            "මට තේරෙනවා මෙය අපහසුයි. මම මෙහි සවන් දෙනවා.",
            "බෙදාගැනීමට ස්තුතියි. එය ඔබට කෙසේ හැඟෙනවාද?",
            "එය ඇත්තෙන්ම අභියෝගයක් විය හැකියි. ඔබට එය ගැන තවත් කතා කිරීමට අවශ්‍යද?",
            "මෙය හරහා යනවාට කණගාටුයි. ඔබ තනි නොවේ.",
            "මෙම හැඟීම් ගැන කතා කිරීමට නිර්භීතකම අවශ්‍යයි. මට විශ්වාස කිරීමට ස්තුතියි.",
            "මට ඇසෙනවා මෙය ඔබට ඇත්තෙන්ම බලපානවා. අපි මෙය එකට ගවේෂණය කරමු.",
            "ඔබේ හැඟීම් වලංගුයි. ඔබට කතා කිරීම දිගටම කරගෙන යාමට අවශ්‍යද?",
            "මම මෙහි ඔබට සහාය වීමට සිටිමි. දැන් වඩාත්ම ප්‍රයෝජනවත් වන්නේ කුමක්ද?",
            "මා සමඟ විවෘත වීමට ස්තුතියි. මම ඔබට හොඳම ආධාරය කළ හැක්කේ කෙසේද?",
            "මා සමඟ මෙය බෙදාගැනීමට ස්තුතියි. අපි මෙය පියවරෙන් පියවර ගනිමු."
        ],
        'ta': [
            "இது கடினம் என்பதை நான் புரிந்துகொள்கிறேன். நான் இங்கே கேட்கிறேன்.",
            "பகிர்ந்தமைக்கு நன்றி. அது உங்களுக்கு எப்படி உணர்த்துகிறது?",
            "அது மிகவும் சவாலானது போல் தெரிகிறது. அதைப் பற்றி மேலும் பேச விரும்புகிறீர்களா?",
            "நீங்கள் இதைச் சந்திக்கிறீர்கள் என்பதற்கு வருந்துகிறேன். நீங்கள் தனியாக இல்லை.",
            "இந்த உணர்வுகளைப் பற்றி பேச தைரியம் தேவை. என்னை நம்பியதற்கு நன்றி.",
            "இது உங்களை மிகவும் பாதிக்கிறது என்பதை நான் கேட்கிறேன். இதை ஒன்றாக ஆராய்வோம்.",
            "உங்கள் உணர்வுகள் செல்லுபடியாகும். நீங்கள் தொடர்ந்து பேச விரும்புகிறீர்களா?",
            "நான் உங்களுக்கு ஆதரவளிக்க இங்கே இருக்கிறேன். இப்போது மிகவும் உதவியாக இருக்கும் என்ன?",
            "என்னுடன் திறந்த மனதுடன் இருந்ததற்கு நன்றி. நான் உங்களுக்கு சிறந்த ஆதரவை எவ்வாறு வழங்க முடியும்?",
            "இதை என்னுடன் பகிர்ந்தமைக்கு நன்றி. இதை படிப்படியாக எடுத்துக்கொள்வோம்."
        ]
    }
    
    def __init__(self):
        pass
    
    def detect_crisis(self, message: str, language: str = 'en') -> bool:
        """
        Detect if message contains crisis/suicide keywords
        Returns True if crisis detected (needs immediate escalation)
        """
        message_lower = message.lower()
        lang = language.lower()[:2]
        
        if lang not in self.CRISIS_KEYWORDS:
            lang = 'en'
        
        keywords = self.CRISIS_KEYWORDS[lang]
        
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def contains_medical_advice(self, text: str, language: str = 'en') -> bool:
        """
        Check if text contains medical advice keywords
        Returns True if medical advice detected
        """
        text_lower = text.lower()
        lang = language.lower()[:2]
        
        if lang not in self.MEDICAL_ADVICE_KEYWORDS:
            lang = 'en'
        
        keywords = self.MEDICAL_ADVICE_KEYWORDS[lang]
        
        for keyword in keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def contains_harmful_suggestion(self, text: str, language: str = 'en') -> bool:
        """
        Check if text contains harmful suggestions
        Returns True if harmful content detected
        """
        text_lower = text.lower()
        lang = language.lower()[:2]
        
        if lang not in self.HARMFUL_SUGGESTIONS:
            lang = 'en'
        
        suggestions = self.HARMFUL_SUGGESTIONS[lang]
        
        for suggestion in suggestions:
            if suggestion in text_lower:
                return True
        
        return False
    
    def validate_response(self, response: str, language: str = 'en') -> Tuple[bool, Optional[str]]:
        """
        Validate chatbot response for safety
        Returns (is_safe, error_message)
        """
        # Check for medical advice
        if self.contains_medical_advice(response, language):
            return False, "Response contains medical advice"
        
        # Check for harmful suggestions
        if self.contains_harmful_suggestion(response, language):
            return False, "Response contains harmful suggestions"
        
        return True, None
    
    def get_safe_response(self, language: str = 'en') -> str:
        """
        Get a random safe empathetic response
        Falls back to English if language not available
        """
        lang = language.lower()[:2]
        
        if lang not in self.SAFE_RESPONSES:
            lang = 'en'
        
        import random
        responses = self.SAFE_RESPONSES[lang]
        return random.choice(responses)
    
    def sanitize_response(self, response: str, language: str = 'en') -> str:
        """
        Sanitize response by replacing unsafe content with safe alternatives
        If response is unsafe, returns a safe fallback
        """
        is_safe, _ = self.validate_response(response, language)
        
        if not is_safe:
            # Return safe fallback
            return self.get_safe_response(language)
        
        return response
    
    def get_escalation_message(self, language: str = 'en') -> str:
        """
        Get escalation message for high-risk cases
        """
        escalation_messages = {
            'en': "I'm concerned about your wellbeing. Let me connect you with a counselor. For immediate support, please call 1926.",
            'si': "මම ඔබේ යහපැවැත්ම ගැන කරදර වෙමි. මට ඔබව උපදේශකයෙකු සමඟ සම්බන්ධ කිරීමට ඉඩ දෙන්න. වහාම සහාය සඳහා, කරුණාකර 1926 අමතන්න.",
            'ta': "உங்கள் நல்வாழ்வு குறித்து நான் கவலைப்படுகிறேன். உங்களை ஒரு ஆலோசகருடன் இணைக்க அனுமதியுங்கள். உடனடி ஆதரவுக்கு, தயவுசெய்து 1926 ஐ அழையுங்கள்."
        }
        
        lang = language.lower()[:2]
        if lang not in escalation_messages:
            lang = 'en'
        
        return escalation_messages[lang]
    
    def get_crisis_message(self, language: str = 'en') -> str:
        """
        Get crisis intervention message
        """
        crisis_messages = {
            'en': "I'm very concerned about what you've shared. Your life has value. Please call 1926 immediately or go to your nearest hospital. You are not alone, and help is available.",
            'si': "ඔබ බෙදාගත් දේ ගැන මම බොහෝ කරදර වෙමි. ඔබේ ජීවිතයට වටිනාකමක් ඇත. කරුණාකර වහාම 1926 අමතන්න හෝ ඔබේ ආසන්නතම රෝහලට යන්න. ඔබ තනි නොවේ, සහාය ලබා ගත හැකිය.",
            'ta': "நீங்கள் பகிர்ந்ததைப் பற்றி நான் மிகவும் கவலைப்படுகிறேன். உங்கள் வாழ்க்கைக்கு மதிப்பு உள்ளது. தயவுசெய்து உடனடியாக 1926 ஐ அழையுங்கள் அல்லது உங்கள் அருகிலுள்ள மருத்துவமனைக்குச் செல்லுங்கள். நீங்கள் தனியாக இல்லை, உதவி கிடைக்கிறது."
        }
        
        lang = language.lower()[:2]
        if lang not in crisis_messages:
            lang = 'en'
        
        return crisis_messages[lang]
    
    def analyze_message_safety(self, message: str, language: str = 'en') -> Dict[str, any]:
        """
        Comprehensive safety analysis of user message
        Returns dict with safety flags and recommendations
        """
        is_crisis = self.detect_crisis(message, language)
        has_medical_advice = self.contains_medical_advice(message, language)
        has_harmful = self.contains_harmful_suggestion(message, language)
        
        return {
            "is_crisis": is_crisis,
            "has_medical_advice": has_medical_advice,
            "has_harmful_content": has_harmful,
            "needs_escalation": is_crisis,  # Always escalate crisis
            "risk_level": "severe" if is_crisis else ("high" if has_medical_advice or has_harmful else "low")
        }












