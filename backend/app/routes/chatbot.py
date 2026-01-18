"""
Enhanced Chatbot routes with PHQ-9 support and safety guardrails
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.routes.auth import get_current_user, get_current_user_optional
from app.services.chatbot_service import ChatbotService
from app.services.phq9_service import PHQ9Service
from app.services.chatbot_safety import ChatbotSafetyService
from app.services.depression_detection import DepressionDetectionService
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

# ========== Request/Response Models ==========

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = None  # 'en', 'si', 'ta'
    mood: Optional[str] = None  # Optional mood: 'Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad'

class ChatResponse(BaseModel):
    response: str
    session_id: str
    depression_score: Optional[float] = None
    risk_level: Optional[str] = None
    is_crisis: bool = False
    needs_escalation: bool = False
    language: Optional[str] = None
    intent: Optional[str] = None
    start_phq9: bool = False  # Flag to indicate PHQ-9 should be started
    phq9_question: Optional[str] = None  # First PHQ-9 question if starting

class PHQ9StartRequest(BaseModel):
    language: Optional[str] = 'en'
    mood: Optional[str] = None  # Optional mood

class PHQ9AnswerRequest(BaseModel):
    session_id: str
    answer: str  # Can be numeric (0-3) or text
    language: Optional[str] = 'en'

class PHQ9Response(BaseModel):
    question: str
    question_num: int
    session_id: str
    is_complete: bool = False
    language: str

class PHQ9Result(BaseModel):
    session_id: str
    score: int
    severity: str
    risk_level: str
    recommendation: str
    needs_escalation: bool
    language: str

# ========== Free Chat Endpoint ==========

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Send message to chatbot and get response
    Includes safety checks and depression detection
    Supports both authenticated and anonymous users (for first-time users)
    """
    chatbot_service = ChatbotService()
    user_id = current_user.get('id') if current_user else None
    
    # Validate mood if provided
    if chat_message.mood:
        valid_moods = ['Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad']
        if chat_message.mood not in valid_moods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
            )
    
    # Get or create session
    if chat_message.session_id:
        session = firestore_service.get_session_by_id(chat_message.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = session['id']
        session_type = session.get('session_type', 'chat')
        
        # Update session with mood if provided
        if chat_message.mood:
            firestore_service.update_session(session_id, {'mood': chat_message.mood})
    else:
        session_data = {
            'user_id': user_id,  # Can be None for anonymous users
            'session_type': 'chat',
            'language': chat_message.language or 'en',
            'is_anonymous': user_id is None  # Mark as anonymous session
        }
        # Add mood if provided
        if chat_message.mood:
            session_data['mood'] = chat_message.mood
            
        session_id = firestore_service.create_session(session_data)
        session = firestore_service.get_session_by_id(session_id)
        session_type = 'chat'
    
    # Check if this is a PHQ-9 session - if so, handle as PHQ-9 answer
    if session_type == 'phq9':
        phq9_service = PHQ9Service()
        language = session.get('language') or chat_message.language or 'en'
        # Ensure current_question is an int (Firestore might return string)
        current_question = session.get('phq9_current_question', 1)
        if isinstance(current_question, str):
            try:
                current_question = int(current_question)
            except (ValueError, TypeError):
                current_question = 1
        if not isinstance(current_question, int) or current_question < 1 or current_question > 9:
            current_question = 1
        
        # Parse answer
        answer_score = phq9_service.parse_answer(chat_message.message)
        if answer_score is None:
            # If answer can't be parsed, return error message with current question and options
            error_msg = {
                'en': "I couldn't understand your answer. Please respond with a number (0-3) or the exact text option.",
                'si': "මට ඔබේ පිළිතුර තේරුම් ගත නොහැකි විය. කරුණාකර අංකයක් (0-3) හෝ නිශ්චිත පෙළ විකල්පයක් සපයන්න.",
                'ta': "உங்கள் பதிலை நான் புரிந்து கொள்ள முடியவில்லை. தயவுசெய்து எண் (0-3) அல்லது சரியான உரை விருப்பத்தை வழங்கவும்."
            }
            # Re-display current question with options
            current_question_text = phq9_service.get_question(current_question, language)
            return ChatResponse(
                response=f"{error_msg.get(language, error_msg['en'])}\n\n{current_question_text}",
                session_id=session_id,
                language=language,
                intent='phq9_error',
                start_phq9=False,
                phq9_question=current_question_text
            )
        
        # Get existing answers - ensure keys are ints
        answers_raw = session.get('phq9_answers', {})
        answers = {}
        for key, value in answers_raw.items():
            # Convert string keys to int
            try:
                key_int = int(key) if isinstance(key, str) else key
                answers[key_int] = value
            except (ValueError, TypeError):
                continue
        # Add current answer
        answers[current_question] = answer_score
        
        # Check if complete
        if phq9_service.is_complete(answers):
            # Calculate score and save
            total_score = phq9_service.calculate_score(answers)
            interpretation = phq9_service.interpret_score(total_score)
            
            # Update session with results
            firestore_service.update_session(session_id, {
                'phq9_answers': answers,
                'phq9_score': total_score,
                'phq9_severity': interpretation['severity'],
                'phq9_risk_level': interpretation['risk_level'],
                'phq9_completed_at': datetime.utcnow().isoformat(),
                'depression_score': total_score / 27.0,  # Normalize to 0-1
                'risk_level': interpretation['risk_level']
            })
            
            # Create alert if needed
            if interpretation['needs_escalation']:
                message = f"PHQ-9 assessment completed with score {total_score}/27. Risk level: {interpretation['risk_level']}."
                firestore_service.create_alert({
                    'user_id': user_id,
                    'session_id': session_id,
                    'alert_type': 'phq9_high_score',
                    'phq9_score': total_score,
                    'risk_level': interpretation['risk_level'],
                    'severity': interpretation['severity'],
                    'message': message
                })
            
            # Return completion message
            completion_msg = {
                'en': f"Thank you for completing the assessment. Your score is {total_score}/27. {interpretation['recommendation']}",
                'si': f"ඇගයීම සම්පූර්ණ කිරීමට ස්තුතියි. ඔබේ ලකුණ {total_score}/27 කි. {interpretation.get('recommendation_si', interpretation['recommendation'])}",
                'ta': f"மதிப்பீட்டை முடித்ததற்கு நன்றி. உங்கள் மதிப்பெண் {total_score}/27. {interpretation.get('recommendation_ta', interpretation['recommendation'])}"
            }
            
            return ChatResponse(
                response=completion_msg.get(language, completion_msg['en']),
                session_id=session_id,
                depression_score=total_score / 27.0,
                risk_level=interpretation['risk_level'],
                language=language,
                intent='phq9_complete',
                start_phq9=False
            )
        
        # Get next question
        next_question_num = phq9_service.get_next_question(current_question)
        if next_question_num is None:
            # All questions answered - this shouldn't happen if is_complete check worked
            next_question_num = 9
        
        # Ensure answers dict and next_question_num are proper types for Firestore
        # Firestore can handle int keys in dicts, but we'll ensure consistency
        firestore_service.update_session(session_id, {
            'phq9_answers': answers,
            'phq9_current_question': int(next_question_num)  # Ensure it's an int
        })
        
        next_question = phq9_service.get_question(next_question_num, language)
        
        return ChatResponse(
            response=next_question,
            session_id=session_id,
            language=language,
            intent='phq9_question',
            start_phq9=False,
            phq9_question=next_question
        )
    
    # Regular chat flow
    # Get session context
    session_context = {
        'session_id': session_id,
        'session_type': session.get('session_type', 'chat'),
        'language': session.get('language') or chat_message.language or 'en'
    }
    
    # Get chatbot response with safety checks
    result = await chatbot_service.get_response(
        chat_message.message,
        user_id,
        session_context=session_context,
        language=chat_message.language
    )
    
    # Check if user wants to start PHQ-9
    intent = result.get('intent')
    language = result.get('language', 'en')
    start_phq9 = False
    phq9_question = None
    phq9_session_id = session_id
    
    if intent == 'start_phq9':
        # Start PHQ-9 questionnaire
        phq9_service = PHQ9Service()
        start_phq9 = True
        
        # Create or update session for PHQ-9
        phq9_session_data = {
            'user_id': user_id,  # Can be None for anonymous users
            'session_type': 'phq9',
            'language': language,
            'phq9_answers': {},
            'phq9_current_question': 1,
            'is_anonymous': user_id is None
        }
        # Include mood if provided in the chat message
        if chat_message.mood:
            phq9_session_data['mood'] = chat_message.mood
        
        phq9_session_id = firestore_service.create_session(phq9_session_data)
        
        # Get first question
        phq9_question = phq9_service.get_question(1, language)
        
        # Update response to include PHQ-9 question
        result['response'] = f"{result['response']}\n\n{phq9_question}"
    
    # Update session with latest data
    session_updates = {
        'depression_score': result.get('depression_score', 0),
        'risk_level': result.get('risk_level', 'low'),
        'last_message_time': datetime.utcnow().isoformat()
    }
    
    # If crisis detected, create admin alert (only for authenticated users)
    if (result.get('is_crisis') or result.get('needs_escalation')) and user_id:
        risk_level = result.get('risk_level', 'severe')
        firestore_service.create_alert({
            'user_id': user_id,
            'session_id': session_id,
            'alert_type': 'crisis' if result.get('is_crisis') else 'high_risk',
            'message': chat_message.message,
            'risk_level': risk_level,
            'severity': risk_level,  # Add severity field for consistency
            'depression_score': result.get('depression_score', 0)
        })
        session_updates['needs_escalation'] = True
        session_updates['escalated_at'] = datetime.utcnow().isoformat()
    elif (result.get('is_crisis') or result.get('needs_escalation')) and not user_id:
        # For anonymous users, still mark session but don't create alert
        session_updates['needs_escalation'] = True
        session_updates['escalated_at'] = datetime.utcnow().isoformat()
        # Log crisis for anonymous user (could be stored separately if needed)
        print(f"[WARNING] Crisis detected for anonymous user in session {session_id}")
    
    firestore_service.update_session(session_id, session_updates)
    
    return ChatResponse(
        response=result['response'],
        session_id=phq9_session_id if start_phq9 else session_id,
        depression_score=result.get('depression_score'),
        risk_level=result.get('risk_level'),
        is_crisis=result.get('is_crisis', False),
        needs_escalation=result.get('needs_escalation', False),
        language=result.get('language', 'en'),
        intent=result.get('intent'),
        start_phq9=start_phq9,
        phq9_question=phq9_question
    )

# ========== PHQ-9 Endpoints ==========

@router.post("/phq9/start", response_model=PHQ9Response)
async def start_phq9(
    request: PHQ9StartRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start PHQ-9 questionnaire
    Returns first question
    """
    # Validate mood if provided
    if request.mood:
        valid_moods = ['Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad']
        if request.mood not in valid_moods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
            )
    
    phq9_service = PHQ9Service()
    user_id = current_user.get('id')
    language = request.language or 'en'
    
    # Create PHQ-9 session
    session_data = {
        'user_id': user_id,
        'session_type': 'phq9',
        'language': language,
        'phq9_answers': {},
        'phq9_current_question': 1
    }
    # Include mood if provided
    if request.mood:
        session_data['mood'] = request.mood
    
    session_id = firestore_service.create_session(session_data)
    
    # Get first question
    question = phq9_service.get_question(1, language)
    
    return PHQ9Response(
        question=question,
        question_num=1,
        session_id=session_id,
        is_complete=False,
        language=language
    )

@router.post("/phq9/answer", response_model=PHQ9Response)
async def answer_phq9_question(
    request: PHQ9AnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Answer a PHQ-9 question
    Returns next question or completion status
    """
    phq9_service = PHQ9Service()
    user_id = current_user.get('id')
    language = request.language or 'en'
    
    # Get session
    session = firestore_service.get_session_by_id(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="PHQ-9 session not found")
    
    if session.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")
    
    if session.get('session_type') != 'phq9':
        raise HTTPException(status_code=400, detail="Session is not a PHQ-9 session")
    
    # Get current question number
    current_question = session.get('phq9_current_question', 1)
    if current_question > 9:
        raise HTTPException(status_code=400, detail="All questions already answered")
    
    # Parse answer
    answer_score = phq9_service.parse_answer(request.answer)
    if answer_score is None:
        raise HTTPException(
            status_code=400, 
            detail=f"Could not parse answer. Please provide a number (0-3) or text response."
        )
    
    # Get existing answers
    answers = session.get('phq9_answers', {})
    answers[current_question] = answer_score
    
    # Check if complete
    if phq9_service.is_complete(answers):
        # Calculate score and save
        total_score = phq9_service.calculate_score(answers)
        interpretation = phq9_service.interpret_score(total_score)
        
        # Update session with results
        firestore_service.update_session(request.session_id, {
            'phq9_answers': answers,
            'phq9_score': total_score,
            'phq9_severity': interpretation['severity'],
            'phq9_risk_level': interpretation['risk_level'],
            'phq9_completed_at': datetime.utcnow().isoformat(),
            'depression_score': total_score / 27.0,  # Normalize to 0-1
            'risk_level': interpretation['risk_level']
        })
        
        # Create alert if needed
        if interpretation['needs_escalation']:
            message = f"PHQ-9 assessment completed with score {total_score}/27. Risk level: {interpretation['risk_level']}."
            firestore_service.create_alert({
                'user_id': user_id,
                'session_id': request.session_id,
                'alert_type': 'phq9_high_score',
                'phq9_score': total_score,
                'risk_level': interpretation['risk_level'],
                'severity': interpretation.get('severity', interpretation['risk_level']),
                'message': message
            })
        
        return PHQ9Response(
            question="",  # Empty for completion
            question_num=9,
            session_id=request.session_id,
            is_complete=True,
            language=language
        )
    
    # Get next question
    next_question_num = phq9_service.get_next_question(current_question)
    
    # Update session
    firestore_service.update_session(request.session_id, {
        'phq9_answers': answers,
        'phq9_current_question': next_question_num
    })
    
    # Get next question text
    next_question = phq9_service.get_question(next_question_num, language)
    
    return PHQ9Response(
        question=next_question,
        question_num=next_question_num,
        session_id=request.session_id,
        is_complete=False,
        language=language
    )

@router.get("/phq9/result/{session_id}", response_model=PHQ9Result)
async def get_phq9_result(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get PHQ-9 questionnaire results
    """
    phq9_service = PHQ9Service()
    user_id = current_user.get('id')
    
    # Get session
    session = firestore_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if session.get('session_type') != 'phq9':
        raise HTTPException(status_code=400, detail="Not a PHQ-9 session")
    
    # Check if completed
    if 'phq9_score' not in session:
        raise HTTPException(status_code=400, detail="PHQ-9 questionnaire not completed")
    
    score = session.get('phq9_score')
    language = session.get('language', 'en')
    
    # Get interpretation
    interpretation = phq9_service.interpret_score(score)
    
    return PHQ9Result(
        session_id=session_id,
        score=score,
        severity=interpretation['severity'],
        risk_level=interpretation['risk_level'],
        recommendation=interpretation['recommendation'],
        needs_escalation=interpretation['needs_escalation'],
        language=language
    )

# ========== Session Management ==========

@router.get("/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat sessions from Firestore"""
    user_id = current_user.get('id')
    sessions = firestore_service.get_user_sessions(user_id, session_type="chat")
    
    return [
        {
            "id": session.get('id'),
            "start_time": session.get('start_time'),
            "end_time": session.get('end_time'),
            "depression_score": session.get('depression_score'),
            "risk_level": session.get('risk_level'),
            "needs_escalation": session.get('needs_escalation', False),
            "session_type": session.get('session_type', 'chat')
        }
        for session in sessions
    ]

@router.get("/phq9/sessions")
async def get_phq9_sessions(
    current_user: dict = Depends(get_current_user)
):
    """Get user's PHQ-9 sessions"""
    user_id = current_user.get('id')
    sessions = firestore_service.get_user_sessions(user_id, session_type="phq9")
    
    return [
        {
            "id": session.get('id'),
            "start_time": session.get('start_time'),
            "phq9_score": session.get('phq9_score'),
            "phq9_severity": session.get('phq9_severity'),
            "phq9_risk_level": session.get('phq9_risk_level'),
            "completed_at": session.get('phq9_completed_at')
        }
        for session in sessions
    ]
