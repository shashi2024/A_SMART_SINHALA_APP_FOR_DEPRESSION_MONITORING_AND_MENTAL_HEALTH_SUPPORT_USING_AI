"""
Test script for Chatbot and PHQ-9 functionality
Run this script to test the chatbot endpoints
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/chatbot"

# You'll need to get a token from login endpoint first
# For testing, you can use the auth endpoint to get a token
TOKEN = None  # Set this after getting token from login

def get_headers() -> dict:
    """Get headers with authentication"""
    if not TOKEN:
        raise Exception("Please set TOKEN variable. Get it from /api/auth/login endpoint first.")
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def test_free_chat():
    """Test free chat functionality"""
    print("\n" + "="*60)
    print("TEST 1: Free Chat")
    print("="*60)
    
    # Test 1: Start a new chat
    print("\n1. Starting new chat session...")
    response = requests.post(
        f"{API_BASE}/chat",
        headers=get_headers(),
        json={
            "message": "Hello, I've been feeling really down lately",
            "language": "en"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat started successfully!")
        print(f"   Session ID: {data['session_id']}")
        print(f"   Response: {data['response'][:100]}...")
        print(f"   Depression Score: {data['depression_score']}")
        print(f"   Risk Level: {data['risk_level']}")
        print(f"   Needs Escalation: {data['needs_escalation']}")
        session_id = data['session_id']
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None
    
    # Test 2: Continue chat
    print("\n2. Continuing chat...")
    response = requests.post(
        f"{API_BASE}/chat",
        headers=get_headers(),
        json={
            "message": "I feel hopeless and tired all the time",
            "session_id": session_id,
            "language": "en"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat continued!")
        print(f"   Response: {data['response'][:100]}...")
        print(f"   Depression Score: {data['depression_score']}")
        print(f"   Risk Level: {data['risk_level']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 3: Test crisis detection
    print("\n3. Testing crisis detection...")
    response = requests.post(
        f"{API_BASE}/chat",
        headers=get_headers(),
        json={
            "message": "I want to kill myself",
            "session_id": session_id,
            "language": "en"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Crisis detected!")
        print(f"   Is Crisis: {data['is_crisis']}")
        print(f"   Needs Escalation: {data['needs_escalation']}")
        print(f"   Response: {data['response'][:150]}...")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return session_id

def test_phq9_questionnaire():
    """Test PHQ-9 questionnaire"""
    print("\n" + "="*60)
    print("TEST 2: PHQ-9 Questionnaire")
    print("="*60)
    
    # Test 1: Start PHQ-9
    print("\n1. Starting PHQ-9 questionnaire...")
    response = requests.post(
        f"{API_BASE}/phq9/start",
        headers=get_headers(),
        json={"language": "en"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ PHQ-9 started!")
        print(f"   Session ID: {data['session_id']}")
        print(f"   Question {data['question_num']}: {data['question'][:80]}...")
        session_id = data['session_id']
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None
    
    # Test 2: Answer all 9 questions
    print("\n2. Answering PHQ-9 questions...")
    answers = [2, 2, 1, 2, 1, 2, 1, 0, 1]  # Example answers
    
    for i, answer in enumerate(answers, 1):
        print(f"   Answering question {i} with score {answer}...")
        response = requests.post(
            f"{API_BASE}/phq9/answer",
            headers=get_headers(),
            json={
                "session_id": session_id,
                "answer": str(answer),
                "language": "en"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['is_complete']:
                print(f"   ✅ All questions completed!")
                break
            else:
                print(f"   ✅ Question {i} answered. Next: Question {data['question_num']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(response.text)
            return None
    
    # Test 3: Get results
    print("\n3. Getting PHQ-9 results...")
    response = requests.get(
        f"{API_BASE}/phq9/result/{session_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Results retrieved!")
        print(f"   Score: {data['score']}/27")
        print(f"   Severity: {data['severity']}")
        print(f"   Risk Level: {data['risk_level']}")
        print(f"   Needs Escalation: {data['needs_escalation']}")
        print(f"   Recommendation: {data['recommendation'][:150]}...")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return session_id

def test_multi_language():
    """Test multi-language support"""
    print("\n" + "="*60)
    print("TEST 3: Multi-language Support")
    print("="*60)
    
    languages = [
        ("en", "I feel sad"),
        ("si", "මට දුක්බර හැඟීමක් ඇත"),
        ("ta", "நான் வருத்தமாக உணர்கிறேன்")
    ]
    
    for lang_code, message in languages:
        print(f"\nTesting {lang_code.upper()} language...")
        response = requests.post(
            f"{API_BASE}/chat",
            headers=get_headers(),
            json={
                "message": message,
                "language": lang_code
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {lang_code.upper()} chat successful!")
            print(f"   Response language: {data['language']}")
            print(f"   Response: {data['response'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

def test_sessions():
    """Test session retrieval"""
    print("\n" + "="*60)
    print("TEST 4: Session Management")
    print("="*60)
    
    # Get chat sessions
    print("\n1. Getting chat sessions...")
    response = requests.get(
        f"{API_BASE}/sessions",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"✅ Found {len(sessions)} chat sessions")
        for session in sessions[:3]:  # Show first 3
            print(f"   - Session {session['id'][:8]}... | Score: {session.get('depression_score', 0):.2f} | Risk: {session.get('risk_level', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    # Get PHQ-9 sessions
    print("\n2. Getting PHQ-9 sessions...")
    response = requests.get(
        f"{API_BASE}/phq9/sessions",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"✅ Found {len(sessions)} PHQ-9 sessions")
        for session in sessions[:3]:  # Show first 3
            print(f"   - Session {session['id'][:8]}... | Score: {session.get('phq9_score', 'N/A')} | Severity: {session.get('phq9_severity', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def get_auth_token(username: str, password: str) -> Optional[str]:
    """Get authentication token"""
    print("\n" + "="*60)
    print("Getting Authentication Token")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Token obtained successfully!")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("CHATBOT TEST SCRIPT")
    print("="*60)
    print("\n⚠️  Make sure the backend server is running on http://localhost:8000")
    print("⚠️  You need to set TOKEN variable or provide credentials\n")
    
    # Option 1: Use existing token
    global TOKEN
    if not TOKEN:
        # Option 2: Get token from login
        print("To get a token, you can:")
        print("1. Use an existing token (set TOKEN variable)")
        print("2. Login with credentials (uncomment below)")
        print("\nExample login:")
        print("  username = 'your_username'")
        print("  password = 'your_password'")
        print("  TOKEN = get_auth_token(username, password)")
        
        # Uncomment and fill in to auto-login:
        # username = "test_user"
        # password = "test_password"
        # TOKEN = get_auth_token(username, password)
        # if not TOKEN:
        #     print("\n❌ Cannot proceed without authentication token")
        #     return
        
        # For now, prompt user
        print("\nPlease set TOKEN variable in the script or uncomment the login section.")
        print("You can get a token by:")
        print("  curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"your_user\",\"password\":\"your_pass\"}'")
        return
    
    try:
        # Run tests
        test_free_chat()
        test_phq9_questionnaire()
        test_multi_language()
        test_sessions()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()











