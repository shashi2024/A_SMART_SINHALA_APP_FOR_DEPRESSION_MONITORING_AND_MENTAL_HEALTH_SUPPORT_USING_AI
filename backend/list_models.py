import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found in environment variables.")
else:
    client = genai.Client(api_key=api_key)
    print("Listing all models to models_list_clean.txt...")
    with open('models_list_clean.txt', 'w', encoding='utf-8') as f:
        for m in client.models.list():
            f.write(f"{m.name}\n")
    print("Done.")
