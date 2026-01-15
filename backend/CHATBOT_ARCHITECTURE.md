 # 🤖 Chatbot Architecture for Depression Detection

## Overview

This document describes the architecture for a **safe, controlled chatbot** designed for depression detection in the 1926 Mental Health Calling Center system. The chatbot uses a **hybrid approach** combining structured questionnaires (PHQ-9) with real-time depression detection from natural conversations.

---

## 🎯 Design Principles

### 1. **Safety First**
- ❌ **NO medical advice, prescriptions, or diagnoses**
- ✅ **Controlled responses** using predefined templates
- ✅ **Safety guardrails** to filter harmful content
- ✅ **Escalation to human counselors** for high-risk cases

### 2. **Dual Detection Methods**
- **PHQ-9 Questionnaire**: Structured, validated depression screening
- **Real-time Chat Analysis**: Continuous depression detection from conversation

### 3. **Multi-language Support**
- Sinhala (සිංහල)
- Tamil (தமிழ்)
- English

### 4. **Controlled AI (No Full LLM Access)**
- Rule-based response system
- Pattern matching for intent detection
- Predefined safe response templates
- No open-ended AI generation

---

## 🏗️ Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Chat Interface                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Chatbot Router/Orchestrator                     │
│  - Determines mode: PHQ-9 or Free Chat                      │
│  - Routes to appropriate handler                            │
└──────┬──────────────────────────────┬───────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────┐            ┌─────────────────────┐
│  PHQ-9 Mode │            │   Free Chat Mode    │
│  Handler    │            │   Handler           │
└──────┬───────┘            └──────┬──────────────┘
       │                          │
       ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Safety Guardrails Layer                         │
│  - Response filtering                                        │
│  - Medical advice blocking                                   │
│  - Harmful content detection                                 │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Depression Detection Engine                         │
│  - PHQ-9 Scoring                                            │
│  - Real-time text analysis                                  │
│  - Combined scoring algorithm                               │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Response Generator                                   │
│  - Multi-language templates                                  │
│  - Safe, empathetic responses                               │
│  - Escalation triggers                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 PHQ-9 Questionnaire

The Patient Health Questionnaire-9 (PHQ-9) is a validated depression screening tool with 9 questions:

1. **Little interest or pleasure in doing things**
2. **Feeling down, depressed, or hopeless**
3. **Trouble falling or staying asleep, or sleeping too much**
4. **Feeling tired or having little energy**
5. **Poor appetite or overeating**
6. **Feeling bad about yourself or that you are a failure**
7. **Trouble concentrating on things**
8. **Moving or speaking so slowly/fast that others noticed**
9. **Thoughts of hurting yourself**

**Scoring**: 0-3 for each question (0=Not at all, 1=Several days, 2=More than half, 3=Nearly every day)

**Total Score Interpretation**:
- 0-4: Minimal depression
- 5-9: Mild depression
- 10-14: Moderate depression
- 15-19: Moderately severe depression
- 20-27: Severe depression

---

## 🔒 Safety Guardrails

### 1. **Response Filtering**
- Block medical advice keywords
- Block prescription/diagnosis language
- Block harmful suggestions
- Redirect to safe responses

### 2. **Intent Classification**
- Detect suicide/self-harm mentions → **IMMEDIATE ESCALATION**
- Detect medical questions → Redirect to professional help
- Detect general conversation → Safe empathetic responses

### 3. **Content Validation**
- Check response against whitelist of safe phrases
- Validate response doesn't contain medical advice
- Ensure responses are empathetic and supportive

### 4. **Escalation Triggers**
- PHQ-9 score ≥ 15 (Severe)
- Suicide/self-harm keywords detected
- User explicitly requests human help
- Multiple high-risk indicators

---

## 💬 Chatbot Modes

### Mode 1: PHQ-9 Questionnaire Mode
- **Purpose**: Structured depression screening
- **Flow**: Sequential questions, one at a time
- **Output**: PHQ-9 score (0-27)
- **Language**: User's preferred language (Sinhala/Tamil/English)

### Mode 2: Free Chat Mode
- **Purpose**: Natural conversation with real-time detection
- **Flow**: Open conversation, continuous analysis
- **Output**: Real-time depression score + risk level
- **Language**: User's preferred language

### Mode Switching
- User can start PHQ-9 anytime: "I want to take the questionnaire"
- User can switch to free chat: "I want to chat"
- System can suggest PHQ-9 if high risk detected in chat

---

## 🔄 Conversation Flow

### Starting a Session
1. User initiates chat
2. Bot greets and offers options:
   - "Would you like to take a quick assessment (PHQ-9)?"
   - "Or would you prefer to chat freely?"
3. User selects mode

### PHQ-9 Flow
1. Bot asks Question 1
2. User responds (0-3 or text)
3. Bot interprets response and scores
4. Bot asks Question 2
5. Repeat until all 9 questions answered
6. Calculate total score
7. Provide interpretation and recommendations

### Free Chat Flow
1. User sends message
2. Bot analyzes for depression indicators
3. Bot generates safe, empathetic response
4. Bot updates real-time depression score
5. If high risk detected → Suggest PHQ-9 or escalate

---

## 🧠 Depression Detection Algorithm

### Real-time Text Analysis
```python
depression_score = (
    keyword_analysis * 0.3 +
    sentiment_analysis * 0.3 +
    linguistic_patterns * 0.2 +
    conversation_context * 0.2
)
```

### Combined Scoring (PHQ-9 + Chat)
```python
final_score = (
    phq9_score * 0.6 +      # PHQ-9 is more reliable
    chat_score * 0.4
)
```

### Risk Levels
- **Low**: Score < 0.25
- **Moderate**: Score 0.25 - 0.5
- **High**: Score 0.5 - 0.75
- **Severe**: Score > 0.75

---

## 🌐 Multi-language Support

### Language Detection
- Detect from user's first message
- Store preference in session
- Use appropriate templates

### Response Templates
- Predefined safe responses in all 3 languages
- Culturally appropriate phrasing
- Maintains empathetic tone

### Translation (if needed)
- Use Google Translate API for user input
- Responses always in user's language

---

## 📊 Integration Points

### 1. **Existing Depression Detection Models**
- Integrate with typing pattern model (Component 4)
- Integrate with voice analysis (Component 1)
- Integrate with facial expression model (Component 2)
- Integrate with Twitter analysis (Component 3)

### 2. **Admin Panel**
- Real-time alerts for high-risk users
- Session history and analytics
- Escalation queue for counselors

### 3. **1926 Calling Center**
- Direct escalation for severe cases
- Session data for counselor review
- Integration with call center workflow

---

## 🛡️ Safety Measures

### What the Bot CAN Do
✅ Listen empathetically
✅ Ask PHQ-9 questions
✅ Provide general support phrases
✅ Detect depression indicators
✅ Escalate to human counselors
✅ Provide crisis hotline information

### What the Bot CANNOT Do
❌ Give medical advice
❌ Prescribe medications
❌ Diagnose conditions
❌ Provide therapy techniques
❌ Make treatment recommendations
❌ Give specific health advice

---

## 📝 Response Templates

### Safe Empathetic Responses
- "I understand this is difficult. I'm here to listen."
- "Thank you for sharing. How does that make you feel?"
- "That sounds really challenging. Would you like to talk more about it?"

### Escalation Responses
- "I'm concerned about your wellbeing. Let me connect you with a counselor."
- "For immediate support, please call 1926."
- "I think it would be helpful to speak with a mental health professional."

### PHQ-9 Responses
- "Over the last 2 weeks, how often have you experienced [symptom]?"
- "Thank you. Now, let's move to the next question."

---

## 🔧 Technical Implementation

### Services
1. **ChatbotService**: Main orchestration
2. **PHQ9Service**: PHQ-9 questionnaire logic
3. **ChatbotSafetyService**: Safety guardrails
4. **DepressionDetectionService**: Analysis engine
5. **LanguageService**: Multi-language support

### Data Storage
- Session state in Firestore
- PHQ-9 responses in Firestore
- Chat history in Firestore
- Depression scores in Firestore

### API Endpoints
- `POST /api/chatbot/chat` - Send message
- `POST /api/chatbot/phq9/start` - Start PHQ-9
- `POST /api/chatbot/phq9/answer` - Answer PHQ-9 question
- `GET /api/chatbot/phq9/result` - Get PHQ-9 result
- `GET /api/chatbot/sessions` - Get chat sessions

---

## 🚀 Deployment Considerations

### Performance
- Response time < 2 seconds
- Support concurrent users
- Efficient pattern matching

### Scalability
- Stateless design (session in database)
- Horizontal scaling capability
- Caching for templates

### Monitoring
- Track response times
- Monitor safety filter triggers
- Log escalation events
- Analytics on depression scores

---

## 📚 References

- PHQ-9: Patient Health Questionnaire
- WHO Mental Health Guidelines
- Sri Lanka 1926 Mental Health Helpline
- Best practices for mental health chatbots

---

*This architecture ensures a safe, effective, and controlled chatbot for depression detection while maintaining user safety and compliance with medical guidelines.*
