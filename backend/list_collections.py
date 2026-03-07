from app.services.firestore_service import FirestoreService
import os

# Set environment variable if needed (though it should be in .env)
# os.environ["FIREBASE_CREDENTIALS"] = "path/to/credentials.json"

try:
    fs = FirestoreService()
    collections = fs.db.collections()
    print("--- COLLECTIONS ---")
    for col in collections:
        print(f"Collection: {col.id}")
    print("--- END ---")
except Exception as e:
    print(f"Error: {e}")
