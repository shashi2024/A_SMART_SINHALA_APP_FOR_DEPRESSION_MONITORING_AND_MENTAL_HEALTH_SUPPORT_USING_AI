# 🧪 Chatbot Test Scripts Guide

## Available Scripts

### 1. `test_chatbot.py` - Comprehensive Test Suite
**Full test coverage for all chatbot features**

**Usage:**
```bash
python test_chatbot.py
```

**What it tests:**
- ✅ Free chat functionality
- ✅ PHQ-9 questionnaire (all 9 questions)
- ✅ Multi-language support (English, Sinhala, Tamil)
- ✅ Crisis detection
- ✅ Session management
- ✅ Depression scoring

**Before running:**
1. Set `TOKEN` variable in the script (get it from `/api/auth/login`)
2. Or uncomment the login section and provide credentials

**Example:**
```python
# In test_chatbot.py, set:
TOKEN = "your_token_here"

# Or uncomment:
username = "test_user"
password = "test_password"
TOKEN = get_auth_token(username, password)
```

---

### 2. `test_chatbot_simple.py` - Quick Test
**Simple script for quick endpoint testing**

**Usage:**
```bash
python test_chatbot_simple.py
```

**What it does:**
- Quick test of chat endpoint
- Quick test of PHQ-9 start endpoint
- Minimal setup required

**Before running:**
- Set `TOKEN = "your_token_here"` in the script

---

### 3. `demo_chatbot.py` - Interactive Demo
**Interactive chatbot demo - chat with the bot!**

**Usage:**
```bash
python demo_chatbot.py
```

**Features:**
- 🗣️ Interactive chat mode
- 📋 PHQ-9 questionnaire mode
- 🔄 Switch between modes
- 📊 View PHQ-9 results

**How to use:**
1. Run the script
2. Enter your username and password (or set TOKEN in script)
3. Start chatting!
4. Type `phq9` to start questionnaire
5. Type `exit` to quit

**Example session:**
```
You: Hello
Bot: Hello! I'm here to support you...

You: I feel sad
Bot: I'm sorry you're feeling this way...

You: phq9
[Starts PHQ-9 questionnaire]

Question 1/9:
Over the last 2 weeks, how often have you had little interest...
Your answer (0-3): 2

[Continues through all 9 questions]

✅ Questionnaire completed!
PHQ-9 Score: 15/27
Severity: moderately_severe
Risk Level: severe
```

---

### 4. `run_chatbot_tests.bat` - Windows Batch Script
**Easy Windows launcher for tests**

**Usage:**
```bash
run_chatbot_tests.bat
```

**What it does:**
- Checks if Python is installed
- Checks if backend server is running
- Runs `test_chatbot.py`
- Shows results

---

## 🔑 Getting an Authentication Token

### Method 1: Using curl
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

### Method 2: Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={
        "username": "your_username",
        "password": "your_password"
    }
)

token = response.json()["access_token"]
print(f"Token: {token}")
```

### Method 3: Using the test script
The `test_chatbot.py` script has a `get_auth_token()` function you can use.

---

## 🚀 Quick Start

### Step 1: Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload
```

### Step 2: Get Token
```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### Step 3: Run Tests
```bash
# Option 1: Comprehensive tests
python test_chatbot.py

# Option 2: Interactive demo
python demo_chatbot.py

# Option 3: Quick test
python test_chatbot_simple.py
```

---

## 📝 Example Test Output

### Free Chat Test
```
============================================================
TEST 1: Free Chat
============================================================

1. Starting new chat session...
✅ Chat started successfully!
   Session ID: abc123...
   Response: I'm sorry you're feeling this way...
   Depression Score: 0.65
   Risk Level: high
   Needs Escalation: True

2. Continuing chat...
✅ Chat continued!
   Response: Thank you for sharing...
   Depression Score: 0.72
   Risk Level: severe

3. Testing crisis detection...
✅ Crisis detected!
   Is Crisis: True
   Needs Escalation: True
   Response: I'm very concerned about what you've shared...
```

### PHQ-9 Test
```
============================================================
TEST 2: PHQ-9 Questionnaire
============================================================

1. Starting PHQ-9 questionnaire...
✅ PHQ-9 started!
   Session ID: xyz789...
   Question 1: Over the last 2 weeks, how often have you...

2. Answering PHQ-9 questions...
   Answering question 1 with score 2...
   ✅ Question 1 answered. Next: Question 2
   ...
   ✅ All questions completed!

3. Getting PHQ-9 results...
✅ Results retrieved!
   Score: 15/27
   Severity: moderately_severe
   Risk Level: severe
   Needs Escalation: True
   Recommendation: Your responses suggest moderately severe...
```

---

## 🐛 Troubleshooting

### Error: "Please set TOKEN variable"
**Solution:** Get a token from the login endpoint and set it in the script.

### Error: "Connection refused"
**Solution:** Make sure the backend server is running on `http://localhost:8000`

### Error: "401 Unauthorized"
**Solution:** Your token might be expired. Get a new token from the login endpoint.

### Error: "404 Not Found"
**Solution:** Check that the API routes are registered in `main.py`:
```python
from app.routes.chatbot import router as chatbot_router
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])
```

### Error: "Firebase not initialized"
**Solution:** Make sure Firebase credentials are set in `.env` file:
```
FIREBASE_CREDENTIALS=path/to/firebase-credentials.json
```

---

## 📊 What Gets Tested

### ✅ Chat Functionality
- New chat session creation
- Continuing existing sessions
- Language detection
- Intent detection
- Depression scoring
- Crisis detection
- Escalation triggers

### ✅ PHQ-9 Functionality
- Starting questionnaire
- Answering questions (numeric and text)
- Score calculation
- Result interpretation
- Escalation for high scores

### ✅ Multi-language
- English responses
- Sinhala responses
- Tamil responses
- Language auto-detection

### ✅ Safety Features
- Crisis keyword detection
- Medical advice blocking
- Response validation
- Admin alert creation

---

## 🔧 Customizing Tests

### Add Custom Test Cases
Edit `test_chatbot.py` and add your test functions:

```python
def test_custom_feature():
    """Test your custom feature"""
    print("Testing custom feature...")
    # Your test code here
    pass

# Add to main():
test_custom_feature()
```

### Test Different Languages
Modify the language parameter:
```python
response = requests.post(
    f"{API_BASE}/chat",
    headers=get_headers(),
    json={
        "message": "මට දුක්බර හැඟීමක් ඇත",
        "language": "si"  # Sinhala
    }
)
```

### Test Different Depression Levels
Modify test messages to trigger different risk levels:
```python
# Low risk
"I feel okay today"

# Moderate risk
"I've been feeling down lately"

# High risk
"I feel hopeless and worthless"

# Crisis
"I want to kill myself"
```

---

## 📚 Related Files

- `CHATBOT_IMPLEMENTATION_GUIDE.md` - API usage guide
- `CHATBOT_ARCHITECTURE.md` - Architecture documentation
- `app/routes/chatbot.py` - API endpoints
- `app/services/chatbot_service.py` - Chatbot logic
- `app/services/phq9_service.py` - PHQ-9 implementation

---

*Use these scripts to verify your chatbot implementation is working correctly!*









