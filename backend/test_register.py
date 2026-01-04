"""
Test registration endpoint directly
"""
import requests
import json

def test_register():
    """Test user registration"""
    url = "http://localhost:8000/api/auth/register"
    
    data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "test123456",
        "phone_number": "+1234567890"
    }
    
    try:
        print(f"[TEST] Registering user: {data['username']}")
        response = requests.post(url, json=data, timeout=10)
        
        print(f"[INFO] Status Code: {response.status_code}")
        print(f"[INFO] Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("[OK] Registration successful!")
            print(f"     Response: {response.json()}")
            return True
        else:
            print(f"[ERROR] Registration failed!")
            print(f"     Status: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"     Error: {error_detail}")
            except:
                print(f"     Response Text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("        Start server with: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_register()


















