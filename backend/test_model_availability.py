
import os
import sys
from google import genai
from google.genai import types

# Add backend to path
sys.path.append(os.getcwd())

from app.config import settings

def test_models():
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in settings.")
        return

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # List of models to test
    # gemini-2.0-flash failed with 0 quota
    candidates = [
        "gemini-1.5-flash",
        "gemini-2.0-flash-001",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]
    
    print("Testing models for availability...")
    
    with open('test_scan_results.txt', 'w', encoding='utf-8') as f:
        for model in candidates:
            print(f"\nTesting {model}...")
            f.write(f"\n--- Testing {model} ---\n")
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Hello, simply reply with 'OK'."
                )
                print(f"✅ SUCCESS: {model} is working!")
                f.write(f"SUCCESS: {model} is working!\n")
                f.write(f"Response: {response.text}\n")
                
                # We want to find *all* working models, or stop at first? 
                # Let's stop at first working to save time/quota? 
                # No, let's scan all to see best option.
                
            except Exception as e:
                print(f"❌ FAILED: {model}")
                f.write(f"FAILED: {model}\n")
                f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_models()
