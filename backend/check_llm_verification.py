import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

try:
    from app.services.llm_service import LLMService
except ImportError as e:
    print(f"Error importing LLMService: {e}")
    sys.exit(1)

async def test_gemini():
    print("Testing Gemini API connection...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        return

    # Configure genai explicitly here to check available models
    from google import genai
    client = genai.Client(api_key=api_key)

    print("Listing available models:")
    try:
        for m in client.models.list():
            print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    # Direct test of the model
    models_to_test = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
    
    for model_name in models_to_test:
        print(f"\nDirectly testing '{model_name}' model...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hello"
            )
            print(f"Direct response from {model_name}: {response.text}")
            break # Stop if one works
        except Exception as e:
            print(f"Direct test for {model_name} failed: {e}")

    service = LLMService()
    
    try:
        print("\nAttempting to generate content with default model...")
        response = await service.generate_response("Hello, can you hear me? Reply with 'Yes, I am working'.")
        if response:
            print(f"\nSUCCESS: Gemini responded: {response}")
        else:
            print("\nFAILURE: Gemini returned no response (None).")
            
    except Exception as e:
        print(f"\nFAILURE: An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
