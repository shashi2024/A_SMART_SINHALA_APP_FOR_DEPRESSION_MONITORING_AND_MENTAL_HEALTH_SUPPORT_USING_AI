# 🤖 Chatbot Update Summary

## Overview

This document summarizes the chatbot implementation, language translation approach, and how to use it in the app UI.

---

## 🔍 Key Findings

### **Language Translation Approach**

**The chatbot does NOT use a language translator API (like Google Translate).** Instead, it uses:

1. **Predefined Response Templates**: The chatbot has hardcoded response templates in all three languages:
   - English (`en`)
   - Sinhala (`si`) 
   - Tamil (`ta`)

2. **Automatic Language Detection**: The system detects language from Unicode character ranges:
   - Sinhala: Unicode range `\u0D80-\u0DFF`
   - Tamil: Unicode range `\u0B80-\u0BFF`
   - Default: English

3. **Pattern Matching**: Intent detection uses pattern matching with keywords in all three languages.

### **How It Works**

```
User Message → Language Detection → Intent Detection → Response Template Selection → Safety Check → Response
```

1. User sends a message (in any language)
2. System detects language from Unicode or uses selected language
3. System matches patterns to detect intent (greeting, feeling_sad, etc.)
4. System selects appropriate response template in detected language
5. Safety checks validate the response
6. Response is returned in the user's language

---

## 📱 UI Implementation

### **Language Selection Feature**

I've added language selection to the chat screen:

1. **Language Selector in AppBar**: 
   - Click the language icon in the top-right corner
   - Select from: English, සිංහල (Sinhala), or தமிழ் (Tamil)
   - Selection is saved and persists across app sessions

2. **How to Use**:
   - Open the chat screen
   - Tap the language icon (🌐) in the app bar
   - Select your preferred language
   - All bot responses will be in the selected language

### **Files Updated**

1. **`frontend/lib/services/api_service.dart`**
   - Added `language` parameter to `sendChatMessage()` method
   - Language is now sent to the backend API

2. **`frontend/lib/providers/chatbot_provider.dart`**
   - Added language selection state management
   - Added `setLanguage()` method
   - Language preference is saved using SharedPreferences
   - Language is automatically included in chat requests

3. **`frontend/lib/screens/chat_screen.dart`**
   - Added language selector dropdown in AppBar
   - Shows current language selection
   - Easy language switching during chat

---

## 🎯 Chatbot Features

### **1. Free Chat Mode**
- Natural conversation with the chatbot
- Real-time depression detection
- Automatic language detection or manual selection
- Safety guardrails and crisis detection

### **2. PHQ-9 Questionnaire Mode**
- Structured depression screening (9 questions)
- Available in all three languages
- Automatic scoring and risk assessment
- Escalation for high-risk cases

### **3. Safety Features**
- ❌ **No medical advice** - Bot never prescribes or diagnoses
- ✅ **Crisis detection** - Immediate escalation for suicide/self-harm mentions
- ✅ **Safe responses only** - All responses validated against safety rules
- ✅ **Admin alerts** - High-risk cases automatically create alerts

### **4. Multi-language Support**
- **English**: Full support with predefined templates
- **Sinhala (සිංහල)**: Full support with culturally appropriate responses
- **Tamil (தமிழ்)**: Full support with culturally appropriate responses

---

## 🔧 Backend Implementation

### **Main Components**

1. **`backend/app/services/chatbot_service.py`**
   - Main chatbot logic
   - Intent detection using pattern matching
   - Response template selection
   - Language detection

2. **`backend/app/services/phq9_service.py`**
   - PHQ-9 questionnaire logic
   - Question management
   - Scoring and interpretation

3. **`backend/app/services/chatbot_safety.py`**
   - Safety guardrails
   - Crisis detection
   - Response validation

4. **`backend/app/services/depression_detection.py`**
   - Real-time depression scoring
   - Risk level assessment

5. **`backend/app/routes/chatbot.py`**
   - API endpoints for chat and PHQ-9
   - Session management
   - Integration with Firestore

### **API Endpoints**

#### **Free Chat**
```
POST /api/chatbot/chat
Body: {
  "message": "User message",
  "session_id": "optional",
  "language": "en" | "si" | "ta"
}
```

#### **Start PHQ-9**
```
POST /api/chatbot/phq9/start
Body: {
  "language": "en" | "si" | "ta"
}
```

#### **Answer PHQ-9 Question**
```
POST /api/chatbot/phq9/answer
Body: {
  "session_id": "session-id",
  "answer": "0-3 or text",
  "language": "en" | "si" | "ta"
}
```

#### **Get PHQ-9 Results**
```
GET /api/chatbot/phq9/result/{session_id}
```

---

## 🚀 How to Test in App UI

### **Step 1: Start the Backend**
```bash
cd backend
python -m uvicorn main:app --reload
```

### **Step 2: Run the Flutter App**
```bash
cd frontend
flutter run
```

### **Step 3: Test Language Selection**

1. **Navigate to Chat Screen**
   - Open the app
   - Go to the Chat screen

2. **Select Language**
   - Tap the language icon (🌐) in the top-right
   - Choose: English, සිංහල, or தமிழ்

3. **Test Chat in Different Languages**

   **English:**
   - Send: "Hello, I'm feeling sad"
   - Bot responds in English

   **Sinhala:**
   - Select සිංහල
   - Send: "හෙලෝ, මම දුක්බරව හැඟෙනවා"
   - Bot responds in Sinhala

   **Tamil:**
   - Select தமிழ்
   - Send: "வணக்கம், நான் வருத்தமாக உணர்கிறேன்"
   - Bot responds in Tamil

4. **Test PHQ-9 Questionnaire**
   - Send: "I want to take the questionnaire" (or equivalent in other languages)
   - Bot will start PHQ-9 in your selected language

---

## 📊 Response Templates

The chatbot uses predefined response templates for each intent and language:

### **Example Templates**

**Greeting (English):**
- "Hello! I'm here to support you. Would you like to take a quick mental health assessment (PHQ-9), or would you prefer to chat freely?"

**Greeting (Sinhala):**
- "ආයුබෝවන්! මම ඔබට සහාය වීමට මෙහි සිටිමි. ඔබට මානසික සෞඛ්‍ය ඇගයීමක් (PHQ-9) කිරීමට අවශ්‍යද, නැතහොත් නිදහසේ කතා කිරීමට අවශ්‍යද?"

**Greeting (Tamil):**
- "வணக்கம்! நான் உங்களுக்கு ஆதரவளிக்க இங்கே இருக்கிறேன். நீங்கள் விரைவான மனநல மதிப்பீட்டை (PHQ-9) எடுக்க விரும்புகிறீர்களா, அல்லது சுதந்திரமாக பேச விரும்புகிறீர்களா?"

---

## ⚠️ Important Notes

1. **No Real-time Translation**: The chatbot does NOT translate user input. It uses:
   - Predefined templates in each language
   - Pattern matching for intent detection in each language
   - Language detection from Unicode characters

2. **Language Selection Priority**:
   - If user manually selects a language → Uses selected language
   - If no selection → Auto-detects from message Unicode
   - Default → English

3. **Response Quality**: All responses are:
   - Pre-written and safe
   - Culturally appropriate
   - Validated for medical safety
   - Empathetic and supportive

4. **Crisis Handling**: If crisis keywords detected:
   - Immediate escalation to admin
   - Crisis response in user's language
   - 1926 hotline information provided

---

## 🔗 Related Documentation

- `backend/CHATBOT_IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- `backend/CHATBOT_ARCHITECTURE.md` - Architecture overview
- `backend/app/services/chatbot_service.py` - Main chatbot service
- `backend/app/routes/chatbot.py` - API routes

---

## ✅ Summary

- ✅ **Language Translation**: Uses predefined templates (NOT Google Translate)
- ✅ **Language Selection**: Added to chat UI with dropdown menu
- ✅ **Multi-language Support**: English, Sinhala, Tamil fully supported
- ✅ **Safety Features**: Crisis detection, no medical advice, escalation
- ✅ **PHQ-9 Support**: Structured questionnaire in all languages
- ✅ **Real-time Detection**: Depression scoring from conversations

The chatbot is now ready to use in the app UI with full language selection support!

