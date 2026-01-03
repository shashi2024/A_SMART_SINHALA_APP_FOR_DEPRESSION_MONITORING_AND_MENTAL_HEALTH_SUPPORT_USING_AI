"""
Simple test script for Chatbot - Quick test without authentication
Use this for quick testing if you have a test endpoint or want to test locally
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/chatbot"

def test_chatbot_quick():
    """Quick test of chatbot endpoints"""
    
    # You'll need to replace this with a valid token
    # Get it from: POST /api/auth/login
    TOKEN = "YOUR_TOKEN_HERE"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Testing Chatbot Endpoints...\n")
    
    # Test 1: Free Chat
    print("1. Testing Free Chat...")
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            headers=headers,
            json={
                "message": "I've been feeling really sad lately",
                "language": "en"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Response: {data['response'][:80]}...")
            print(f"   Depression Score: {data.get('depression_score', 'N/A')}")
            print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Start PHQ-9
    print("\n2. Testing PHQ-9 Start...")
    try:
        response = requests.post(
            f"{API_BASE}/phq9/start",
            headers=headers,
            json={"language": "en"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Question: {data['question'][:80]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n✅ Quick test completed!")
    print("\nNote: Make sure:")
    print("  1. Backend server is running (python -m uvicorn main:app --reload)")
    print("  2. You have a valid authentication token")
    print("  3. Firebase is configured properly")

if __name__ == "__main__":
    test_chatbot_quick()









