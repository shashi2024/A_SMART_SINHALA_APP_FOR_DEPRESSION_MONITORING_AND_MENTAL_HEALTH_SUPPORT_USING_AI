"""
PHQ-9 Questionnaire Service
Handles the Patient Health Questionnaire-9 depression screening
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class PHQ9Question(Enum):
    """PHQ-9 Questions"""
    Q1 = 1  # Little interest or pleasure
    Q2 = 2  # Feeling down, depressed, hopeless
    Q3 = 3  # Sleep problems
    Q4 = 4  # Feeling tired or low energy
    Q5 = 5  # Poor appetite or overeating
    Q6 = 6  # Feeling bad about yourself
    Q7 = 7  # Trouble concentrating
    Q8 = 8  # Moving/speaking slowly or fast
    Q9 = 9  # Thoughts of self-harm

class PHQ9Service:
    """Service for handling PHQ-9 questionnaire"""
    
    # PHQ-9 Questions in multiple languages
    QUESTIONS = {
        'en': {
            1: "Over the last 2 weeks, how often have you had little interest or pleasure in doing things?",
            2: "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
            3: "Over the last 2 weeks, how often have you had trouble falling or staying asleep, or sleeping too much?",
            4: "Over the last 2 weeks, how often have you felt tired or had little energy?",
            5: "Over the last 2 weeks, how often have you had poor appetite or overeating?",
            6: "Over the last 2 weeks, how often have you felt bad about yourself or that you are a failure?",
            7: "Over the last 2 weeks, how often have you had trouble concentrating on things?",
            8: "Over the last 2 weeks, how often have you been moving or speaking so slowly that others noticed, or the opposite - being so fidgety or restless that you have been moving around a lot?",
            9: "Over the last 2 weeks, how often have you had thoughts that you would be better off dead, or of hurting yourself?"
        },
        'si': {
            1: "අවසන් සති 2 කදී, කර්මාන්ත කිරීමට අඩු උනන්දුවක් හෝ සතුටක් තිබීම කොපමණ වාර ගණනක් ඔබට තිබුණාද?",
            2: "අවසන් සති 2 කදී, කොපමණ වාර ගණනක් ඔබට දුක්බර, කම්පනයට පත් හෝ බලාපොරොත්තු රහිත යැයි හැඟී ඇත්ද?",
            3: "අවසන් සති 2 කදී, නින්දට යාමට හෝ නින්දේ රැඳීමට අපහසුතාවයක් හෝ අධික නින්ද තිබීම කොපමණ වාර ගණනක් ඔබට තිබුණාද?",
            4: "අවසන් සති 2 කදී, කොපමණ වාර ගණනක් ඔබට වෙහෙසකාරී හෝ අඩු ශක්තියක් තිබීම හැඟී ඇත්ද?",
            5: "අවසන් සති 2 කදී, දුර්වල ආහාර රුචියක් හෝ අධික ආහාර ගැනීම කොපමණ වාර ගණනක් ඔබට තිබුණාද?",
            6: "අවසන් සති 2 කදී, ඔබ ගැන නරක හැඟීමක් හෝ ඔබ අසාර්ථකයෙක් යැයි හැඟීම කොපමණ වාර ගණනක් ඔබට තිබුණාද?",
            7: "අවසන් සති 2 කදී, දේවල් වලට අවධානය යොමු කිරීමේ අපහසුතාවයක් කොපමණ වාර ගණනක් ඔබට තිබුණාද?",
            8: "අවසන් සති 2 කදී, ඔබ එතරම් සෙමින් ගමන් කර හෝ කතා කර ඇති අතර අන් අය දැනගෙන ඇත, හෝ ප්රතිවිරුද්ධව - එතරම් කලබල වී හෝ නිශ්ශබ්ද වී ඇති අතර ඔබ බොහෝ ගමන් කර ඇත?",
            9: "අවසන් සති 2 කදී, ඔබ මිය යාම වඩා හොඳ වනු ඇතැයි හෝ ඔබවම රැවටීමේ සිතුවිලි කොපමණ වාර ගණනක් ඔබට තිබුණාද?"
        },
        'ta': {
            1: "கடந்த 2 வாரங்களில், விஷயங்களைச் செய்வதில் சிறிது ஆர்வம் அல்லது மகிழ்ச்சி இருந்தது எத்தனை முறை?",
            2: "கடந்த 2 வாரங்களில், மனச்சோர்வு, மனச்சோர்வு அல்லது நம்பிக்கையின்மை உணர்ந்தது எத்தனை முறை?",
            3: "கடந்த 2 வாரங்களில், தூங்குவதில் அல்லது தூங்குவதில் சிக்கல், அல்லது அதிகமாக தூங்குவது எத்தனை முறை?",
            4: "கடந்த 2 வாரங்களில், சோர்வாக அல்லது குறைந்த ஆற்றல் இருந்தது எத்தனை முறை?",
            5: "கடந்த 2 வாரங்களில், மோசமான பசி அல்லது அதிகமாக சாப்பிடுவது எத்தனை முறை?",
            6: "கடந்த 2 வாரங்களில், உங்களைப் பற்றி மோசமாக உணர்ந்தது அல்லது நீங்கள் தோல்வியடைந்தவர் என்று எத்தனை முறை?",
            7: "கடந்த 2 வாரங்களில், விஷயங்களில் கவனம் செலுத்துவதில் சிக்கல் எத்தனை முறை?",
            8: "கடந்த 2 வாரங்களில், மற்றவர்கள் கவனித்த அளவுக்கு மெதுவாக அல்லது வேகமாக நகர்ந்தது அல்லது பேசியது எத்தனை முறை?",
            9: "கடந்த 2 வாரங்களில், நீங்கள் இறந்தால் நல்லது அல்லது உங்களைத் துன்புறுத்தும் எண்ணங்கள் எத்தனை முறை?"
        }
    }
    
    # Answer options in multiple languages
    ANSWER_OPTIONS = {
        'en': {
            0: "Not at all",
            1: "Several days",
            2: "More than half the days",
            3: "Nearly every day"
        },
        'si': {
            0: "කිසිසේත් නැත",
            1: "දින කිහිපයක්",
            2: "දින අඩකට වඩා",
            3: "දිනපතාම"
        },
        'ta': {
            0: "இல்லை",
            1: "சில நாட்கள்",
            2: "பாதிக்கும் மேற்பட்ட நாட்கள்",
            3: "கிட்டத்தட்ட ஒவ்வொரு நாளும்"
        }
    }
    
    def __init__(self):
        self.total_questions = 9
    
    def get_question(self, question_num: int, language: str = 'en') -> str:
        """Get PHQ-9 question in specified language with answer options"""
        if question_num < 1 or question_num > 9:
            raise ValueError("Question number must be between 1 and 9")
        
        lang = language.lower()[:2]  # Get first 2 chars (en, si, ta)
        if lang not in self.QUESTIONS:
            lang = 'en'  # Default to English
        
        question = self.QUESTIONS[lang].get(question_num, "")
        options = self.get_answer_options(lang)
        
        # Format question with answer options
        options_text = "\n".join([f"{num}. {text}" for num, text in options.items()])
        
        return f"{question}\n\nPlease answer with a number (0-3) or the exact text:\n{options_text}"
    
    def get_answer_options(self, language: str = 'en') -> Dict[int, str]:
        """Get answer options in specified language"""
        lang = language.lower()[:2]
        if lang not in self.ANSWER_OPTIONS:
            lang = 'en'
        
        return self.ANSWER_OPTIONS[lang]
    
    def parse_answer(self, answer: str) -> Optional[int]:
        """
        Parse user answer to PHQ-9 score (0-3)
        Handles both numeric and text responses
        """
        if not answer:
            return None
            
        answer_clean = answer.strip().lower()
        
        # Direct numeric answers (0, 1, 2, 3)
        if answer_clean.isdigit():
            score = int(answer_clean)
            if 0 <= score <= 3:
                return score
        
        # Extract first number from answer if it contains a number
        import re
        numbers = re.findall(r'\d+', answer_clean)
        if numbers:
            score = int(numbers[0])
            if 0 <= score <= 3:
                return score
        
        # Exact text matches (English) - must match exactly or be contained
        text_to_score = {
            # Score 0
            'not at all': 0, 'never': 0, 'none': 0, 
            # Score 1
            'several days': 1, 'some days': 1, 'sometimes': 1, 'few days': 1,
            # Score 2
            'more than half the days': 2, 'more than half': 2, 'half the days': 2, 'often': 2,
            # Score 3
            'nearly every day': 3, 'every day': 3, 'daily': 3, 'most days': 3, 'always': 3
        }
        
        # Check for exact or partial matches
        for key, value in text_to_score.items():
            if key in answer_clean:
                return value
        
        # Sinhala text answers
        si_to_score = {
            'කිසිසේත් නැත': 0, 'නැත': 0,
            'දින කිහිපයක්': 1, 'සමහර දින': 1,
            'දින අඩකට වඩා': 2, 'බොහෝ විට': 2,
            'දිනපතාම': 3, 'සැමදා': 3
        }
        
        for key, value in si_to_score.items():
            if key in answer_clean:
                return value
        
        # Tamil text answers
        ta_to_score = {
            'இல்லை': 0, 'ஒருபோதும்': 0,
            'சில நாட்கள்': 1, 'சில': 1,
            'பாதிக்கும் மேற்பட்ட': 2, 'பெரும்பாலும்': 2,
            'கிட்டத்தட்ட ஒவ்வொரு நாளும்': 3, 'ஒவ்வொரு நாளும்': 3
        }
        
        for key, value in ta_to_score.items():
            if key in answer_clean:
                return value
        
        return None  # Could not parse
    
    def calculate_score(self, answers: Dict[Any, int]) -> int:
        """
        Calculate total PHQ-9 score from answers
        answers: Dict with question_num (1-9) as key and score (0-3) as value
        Handles both int and string keys.
        """
        total = 0
        for q_num in range(1, 10):
            # Try both int and string keys
            score = answers.get(q_num)
            if score is None:
                score = answers.get(str(q_num))
            
            if score is None:
                raise ValueError(f"Question {q_num} is missing")
            
            if not (0 <= score <= 3):
                raise ValueError(f"Invalid score {score} for question {q_num}")
            total += score
        
        return total
    
    RECOMMENDATIONS = {
        'en': {
            'minimal': "Your responses suggest minimal depression symptoms. Continue monitoring your mental health.",
            'mild': "Your responses suggest mild depression. Consider speaking with a mental health professional.",
            'moderate': "Your responses suggest moderate depression. We recommend speaking with a mental health professional or calling 1926.",
            'moderately_severe': "Your responses suggest moderately severe depression. Please consider immediate support. Call 1926 or speak with a mental health professional.",
            'severe': "Your responses suggest severe depression. Please seek immediate support. Call 1926 now or contact a mental health professional urgently."
        },
        'si': {
            'minimal': "ඔබේ ප්‍රතිචාර වලට අනුව අවම අවදානමක් පෙන්නුම් කරයි. දිගටම ඔබේ මානසික සෞඛ්‍යය ගැන සැලකිලිමත් වන්න.",
            'mild': "ඔබේ ප්‍රතිචාර වලට අනුව සුළු විශාද තත්වයක් පෙන්නුම් කරයි. මානසික සෞඛ්‍ය උපදේශකයෙකු හමුවීම ගැන සලකා බලන්න.",
            'moderate': "ඔබේ ප්‍රතිචාර වලට අනුව මධ්‍යස්ථ විශාද තත්වයක් පෙන්නුම් කරයි. මානසික සෞඛ්‍ය උපදේශකයෙකු හමුවීමට හෝ 1926 අමතන ලෙස අපි නිර්දේශ කරමු.",
            'moderately_severe': "ඔබේ ප්‍රතිචාර වලට අනුව මධ්‍යස්ථ බරපතල විශාද තත්වයක් පෙන්නුම් කරයි. කරුණාකර වහාම සහාය ලබා ගන්න. 1926 අමතන්න හෝ මානසික සෞඛ්‍ය උපදේශකයෙකු හමුවන්න.",
            'severe': "ඔබේ ප්‍රතිචාර වලට අනුව බරපතල විශාද තත්වයක් පෙන්නුම් කරයි. කරුණාකර වහාම සහාය ලබා ගන්න. දැන්ම 1926 අමතන්න හෝ වහාම මානසික සෞඛ්‍ය උපදේශකයෙකු හමුවන්න."
        },
        'ta': {
            'minimal': "உங்கள் பதில்கள் குறைந்தபட்ச மனச்சோர்வு அறிகுறிகளைக் காட்டுகின்றன. உங்கள் மன ஆரோக்கியத்தைத் தொடர்ந்து கண்காணித்து வரவும்.",
            'mild': "உங்கள் பதில்கள் லேசான மனச்சோர்வைக் காட்டுகின்றன. மனநல நிபுணருடன் பேசுவதைக் கருத்தில் கொள்ளவும்.",
            'moderate': "உங்கள் பதில்கள் மிதமான மனச்சோர்வைக் காட்டுகின்றன. மனநல நிபுணருடன் பேச அல்லது 1926 ஐ அழைக்க பரிந்துரைக்கிறோம்.",
            'moderately_severe': "உங்கள் பதில்கள் மிதமான கடுமையான மனச்சோர்வைக் காட்டுகின்றன. தயவுசெய்து உடனடி ஆதரவைக் கருத்தில் கொள்ளவும். 1926 ஐ அழைக்கவும் அல்லது மனநல நிபுணருடன் பேசவும்.",
            'severe': "உங்கள் பதில்கள் கடுமையான மனச்சோர்வைக் காட்டுகின்றன. தயவுசெய்து உடனடி ஆதரவைப் பெறவும். இப்போது 1926 ஐ அழைக்கவும் அல்லது அவசரமாக மனநல நிபுணரைத் தொடர்பு கொள்ளவும்."
        }
    }

    def interpret_score(self, score: int, language: str = 'en') -> Dict[str, any]:
        """
        Interpret PHQ-9 score and return severity level
        Returns: Dict with severity, level, recommendation
        """
        if score < 0 or score > 27:
            raise ValueError("Score must be between 0 and 27")
        
        lang = language.lower()[:2]
        if lang not in self.RECOMMENDATIONS:
            lang = 'en'

        if score <= 4:
            severity = "minimal"
            level = "low"
        elif score <= 9:
            severity = "mild"
            level = "moderate"
        elif score <= 14:
            severity = "moderate"
            level = "high"
        elif score <= 19:
            severity = "moderately_severe"
            level = "severe"
        else:  # 20-27
            severity = "severe"
            level = "severe"
        
        recommendation = self.RECOMMENDATIONS[lang].get(severity, self.RECOMMENDATIONS['en'][severity])
        
        return {
            "score": score,
            "severity": severity,
            "risk_level": level,
            "recommendation": recommendation,
            "needs_escalation": score >= 15  # Escalate if moderately severe or severe
        }
    
    def get_next_question(self, current_question: Optional[int]) -> Optional[int]:
        """Get next question number, or None if completed"""
        if current_question is None:
            return 1
        if current_question < 9:
            return current_question + 1
        return None
    
    def is_complete(self, answers: Dict[Any, int]) -> bool:
        """Check if all 9 questions are answered (handles int or string keys)"""
        for q in range(1, 10):
            if q not in answers and str(q) not in answers:
                return False
        return True
    
    def format_question_with_options(self, question_num: int, language: str = 'en') -> str:
        """Format question with answer options for display"""
        question = self.get_question(question_num, language)
        options = self.get_answer_options(language)
        
        options_text = "\n".join([f"{num}. {text}" for num, text in options.items()])
        
        return f"{question}\n\n{options_text}"














