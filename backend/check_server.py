"""
Quick script to check if server is running and test connection
"""
import requests
import sys

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Server is running!")
            print(f"     Response: {response.json()}")
            return True
        else:
            print(f"[ERROR] Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("        Start server with: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if not check_server():
        sys.exit(1)

















