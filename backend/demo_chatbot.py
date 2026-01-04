"""
Interactive Chatbot Demo Script
Run this to have an interactive conversation with the chatbot
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/chatbot"

class ChatbotDemo:
    def __init__(self, token: str):
        self.token = token
        self.session_id = None
        self.language = "en"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def chat(self, message: str) -> Optional[dict]:
        """Send a chat message"""
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                headers=self.headers,
                json={
                    "message": message,
                    "session_id": self.session_id,
                    "language": self.language
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                return data
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def start_phq9(self) -> Optional[dict]:
        """Start PHQ-9 questionnaire"""
        try:
            response = requests.post(
                f"{API_BASE}/phq9/start",
                headers=self.headers,
                json={"language": self.language},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def answer_phq9(self, session_id: str, answer: str) -> Optional[dict]:
        """Answer PHQ-9 question"""
        try:
            response = requests.post(
                f"{API_BASE}/phq9/answer",
                headers=self.headers,
                json={
                    "session_id": session_id,
                    "answer": answer,
                    "language": self.language
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def run_chat_mode(self):
        """Run interactive chat mode"""
        print("\n" + "="*60)
        print("CHAT MODE - Type 'exit' to quit, 'phq9' to start questionnaire")
        print("="*60 + "\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\nGoodbye! 👋")
                break
            
            if user_input.lower() == 'phq9':
                self.run_phq9_mode()
                continue
            
            # Send message
            result = self.chat(user_input)
            
            if result:
                print(f"\nBot: {result['response']}")
                if result.get('depression_score'):
                    print(f"   [Depression Score: {result['depression_score']:.2f}, Risk: {result['risk_level']}]")
                if result.get('needs_escalation'):
                    print(f"   ⚠️  High risk detected - Admin has been notified")
                print()
            else:
                print("Error communicating with chatbot\n")
    
    def run_phq9_mode(self):
        """Run PHQ-9 questionnaire mode"""
        print("\n" + "="*60)
        print("PHQ-9 QUESTIONNAIRE")
        print("="*60)
        print("Answer each question with 0-3 or text:")
        print("  0 = Not at all")
        print("  1 = Several days")
        print("  2 = More than half the days")
        print("  3 = Nearly every day")
        print("Type 'back' to return to chat mode\n")
        
        # Start PHQ-9
        result = self.start_phq9()
        if not result:
            print("Error starting PHQ-9")
            return
        
        session_id = result['session_id']
        current_question = result['question_num']
        
        print(f"Question {current_question}/9:")
        print(f"{result['question']}\n")
        
        while True:
            answer = input("Your answer (0-3): ").strip()
            
            if answer.lower() == 'back':
                print("Returning to chat mode...\n")
                break
            
            if not answer:
                continue
            
            # Submit answer
            result = self.answer_phq9(session_id, answer)
            
            if not result:
                print("Error submitting answer")
                continue
            
            if result['is_complete']:
                print("\n✅ Questionnaire completed!")
                print("Getting results...\n")
                
                # Get results
                try:
                    response = requests.get(
                        f"{API_BASE}/phq9/result/{session_id}",
                        headers=self.headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        results = response.json()
                        print(f"PHQ-9 Score: {results['score']}/27")
                        print(f"Severity: {results['severity']}")
                        print(f"Risk Level: {results['risk_level']}")
                        print(f"\nRecommendation:")
                        print(f"{results['recommendation']}\n")
                    else:
                        print("Error getting results")
                except Exception as e:
                    print(f"Error: {e}")
                
                print("Returning to chat mode...\n")
                break
            else:
                current_question = result['question_num']
                print(f"\nQuestion {current_question}/9:")
                print(f"{result['question']}\n")

def get_token() -> Optional[str]:
    """Get authentication token"""
    print("="*60)
    print("AUTHENTICATION")
    print("="*60)
    print("\nYou need to provide credentials to get a token.")
    print("Or set TOKEN directly in the script.\n")
    
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function"""
    print("\n" + "="*60)
    print("CHATBOT INTERACTIVE DEMO")
    print("="*60)
    print("\n⚠️  Make sure the backend server is running on http://localhost:8000\n")
    
    # Get token
    token = get_token()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print("\nAlternative: Set TOKEN directly in the script:")
        print("  token = 'your_token_here'")
        return
    
    # Create demo instance
    demo = ChatbotDemo(token)
    
    # Run chat mode
    demo.run_chat_mode()

if __name__ == "__main__":
    main()












