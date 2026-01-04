# 🤖 Chatbot Implementation Guide

## Overview

This guide explains how to use the enhanced chatbot system with PHQ-9 questionnaire support, safety guardrails, and multi-language capabilities.

---

## 🎯 Key Features

✅ **Dual Detection Methods**
- PHQ-9 structured questionnaire (validated depression screening)
- Real-time depression detection from free chat conversations

✅ **Safety First**
- No medical advice or prescriptions
- Crisis detection with immediate escalation
- Controlled, safe responses only

✅ **Multi-language Support**
- English
- Sinhala (සිංහල)
- Tamil (தமிழ்)

✅ **Controlled AI**
- Rule-based responses (NO full LLM access)
- Pattern matching for intent detection
- Predefined safe response templates

---

## 📡 API Endpoints

### 1. Free Chat

**POST** `/api/chatbot/chat`

Start or continue a free chat conversation with depression detection.

**Request:**
```json
{
  "message": "I've been feeling really down lately",
  "session_id": "optional-session-id",
  "language": "en"  // optional: 'en', 'si', 'ta'
}
```

**Response:**
```json
{
  "response": "I'm sorry you're feeling this way...",
  "session_id": "session-id",
  "depression_score": 0.65,
  "risk_level": "high",
  "is_crisis": false,
  "needs_escalation": true,
  "language": "en",
  "intent": "feeling_sad"
}
```

### 2. Start PHQ-9 Questionnaire

**POST** `/api/chatbot/phq9/start`

Begin a PHQ-9 depression screening.

**Request:**
```json
{
  "language": "en"  // 'en', 'si', or 'ta'
}
```

**Response:**
```json
{
  "question": "Over the last 2 weeks, how often have you had little interest or pleasure in doing things?",
  "question_num": 1,
  "session_id": "phq9-session-id",
  "is_complete": false,
  "language": "en"
}
```

### 3. Answer PHQ-9 Question

**POST** `/api/chatbot/phq9/answer`

Answer a PHQ-9 question. Can provide numeric (0-3) or text response.

**Request:**
```json
{
  "session_id": "phq9-session-id",
  "answer": "2",  // or "More than half the days"
  "language": "en"
}
```

**Response:**
```json
{
  "question": "Next question text...",
  "question_num": 2,
  "session_id": "phq9-session-id",
  "is_complete": false,
  "language": "en"
}
```

**When Complete:**
```json
{
  "question": "",
  "question_num": 9,
  "session_id": "phq9-session-id",
  "is_complete": true,
  "language": "en"
}
```

### 4. Get PHQ-9 Results

**GET** `/api/chatbot/phq9/result/{session_id}`

Get completed PHQ-9 questionnaire results.

**Response:**
```json
{
  "session_id": "phq9-session-id",
  "score": 18,
  "severity": "moderately_severe",
  "risk_level": "severe",
  "recommendation": "Your responses suggest moderately severe depression...",
  "needs_escalation": true,
  "language": "en"
}
```

### 5. Get Chat Sessions

**GET** `/api/chatbot/sessions`

Get all chat sessions for the current user.

### 6. Get PHQ-9 Sessions

**GET** `/api/chatbot/phq9/sessions`

Get all PHQ-9 sessions for the current user.

---

## 🔄 Usage Flow

### Flow 1: Free Chat

1. User sends message → `POST /api/chatbot/chat`
2. System detects language, intent, and depression indicators
3. System generates safe, empathetic response
4. System calculates depression score
5. If high risk → Creates admin alert and suggests escalation

### Flow 2: PHQ-9 Questionnaire

1. User starts PHQ-9 → `POST /api/chatbot/phq9/start`
2. System returns first question
3. User answers → `POST /api/chatbot/phq9/answer`
4. System returns next question (or completion)
5. Repeat until all 9 questions answered
6. User gets results → `GET /api/chatbot/phq9/result/{session_id}`
7. If score ≥ 15 → Creates admin alert

---

## 🛡️ Safety Features

### Crisis Detection

If user message contains suicide/self-harm keywords:
- **Immediate escalation** → Admin alert created
- **Crisis response** sent to user
- **1926 hotline** information provided

### Medical Advice Blocking

Bot will **NEVER**:
- Prescribe medications
- Give medical advice
- Diagnose conditions
- Suggest treatments

### Response Validation

All responses are validated against:
- Medical advice keywords
- Harmful suggestions
- Safe response whitelist

---

## 📊 Depression Scoring

### PHQ-9 Scoring
- **0-4**: Minimal depression
- **5-9**: Mild depression
- **10-14**: Moderate depression
- **15-19**: Moderately severe depression
- **20-27**: Severe depression

### Real-time Chat Scoring
- **0-0.25**: Low risk
- **0.25-0.5**: Moderate risk
- **0.5-0.75**: High risk
- **>0.75**: Severe risk

### Combined Scoring
When both PHQ-9 and chat analysis available:
```
final_score = (phq9_score * 0.6) + (chat_score * 0.4)
```

---

## 🌐 Language Support

### Automatic Detection
Language is auto-detected from user's first message:
- Sinhala characters (Unicode range) → 'si'
- Tamil characters (Unicode range) → 'ta'
- Default → 'en'

### Manual Specification
User can specify language in request:
```json
{
  "message": "Hello",
  "language": "si"  // Force Sinhala
}
```

### Response Language
All responses match user's language preference.

---

## 🚨 Escalation Triggers

Admin alerts are created when:

1. **Crisis detected**: Suicide/self-harm keywords
2. **PHQ-9 score ≥ 15**: Moderately severe or severe
3. **Chat risk level = "severe"**: High depression score from chat
4. **User requests help**: Explicit request for human counselor

---

## 🔧 Integration with Other Components

### Component 1: Voice Analysis
- Chat depression score can be combined with voice analysis
- Use `DepressionDetectionService.combine_analyses()`

### Component 2: Facial Expression
- Can integrate facial expression data with chat analysis
- Store in session for combined scoring

### Component 3: Twitter Analysis
- Twitter depression indicators can inform chat responses
- Use historical data for context

### Component 4: Typing Patterns
- Typing pattern analysis can complement chat analysis
- Combined scoring provides more accurate assessment

---

## 📝 Example Usage

### Python Example

```python
import requests

# Start chat
response = requests.post(
    "http://localhost:8000/api/chatbot/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "message": "I've been feeling really sad",
        "language": "en"
    }
)
print(response.json())

# Start PHQ-9
phq9 = requests.post(
    "http://localhost:8000/api/chatbot/phq9/start",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"language": "en"}
)
session_id = phq9.json()["session_id"]

# Answer questions
for i in range(9):
    answer = requests.post(
        "http://localhost:8000/api/chatbot/phq9/answer",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "session_id": session_id,
            "answer": "2"  # 0-3
        }
    )
    result = answer.json()
    if result["is_complete"]:
        break

# Get results
results = requests.get(
    f"http://localhost:8000/api/chatbot/phq9/result/{session_id}",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
print(results.json())
```

### JavaScript/TypeScript Example

```typescript
// Start chat
const chatResponse = await fetch('http://localhost:8000/api/chatbot/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'I feel hopeless',
    language: 'en'
  })
});

const chatData = await chatResponse.json();
console.log(chatData);

// Start PHQ-9
const phq9Start = await fetch('http://localhost:8000/api/chatbot/phq9/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ language: 'en' })
});

const { session_id } = await phq9Start.json();

// Answer questions
for (let i = 0; i < 9; i++) {
  const answer = await fetch('http://localhost:8000/api/chatbot/phq9/answer', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id,
      answer: '2'
    })
  });
  
  const result = await answer.json();
  if (result.is_complete) break;
}

// Get results
const results = await fetch(
  `http://localhost:8000/api/chatbot/phq9/result/${session_id}`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
console.log(await results.json());
```

---

## 🧪 Testing

### Test Free Chat
```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I feel sad",
    "language": "en"
  }'
```

### Test PHQ-9
```bash
# Start
curl -X POST http://localhost:8000/api/chatbot/phq9/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Answer (repeat 9 times)
curl -X POST http://localhost:8000/api/chatbot/phq9/answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "answer": "2"
  }'
```

---

## ⚠️ Important Notes

1. **No Medical Advice**: Bot never provides medical advice, prescriptions, or diagnoses
2. **Crisis Handling**: Suicide/self-harm mentions trigger immediate escalation
3. **Language Support**: All responses available in Sinhala, Tamil, and English
4. **Session Management**: Sessions stored in Firestore with full history
5. **Admin Alerts**: High-risk cases automatically create alerts for counselors

---

## 🔗 Related Documentation

- `CHATBOT_ARCHITECTURE.md` - Detailed architecture
- `phq9_service.py` - PHQ-9 implementation
- `chatbot_safety.py` - Safety guardrails
- `chatbot_service.py` - Main chatbot logic

---

*This chatbot is designed for the 1926 Mental Health Calling Center system and follows strict safety guidelines to protect users while providing empathetic support.*
