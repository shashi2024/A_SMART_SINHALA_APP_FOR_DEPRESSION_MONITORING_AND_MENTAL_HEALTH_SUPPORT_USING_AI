
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Set path to service account key
os.environ["FIREBASE_CREDENTIALS"] = r"d:\Studies\Sliit\Research Documents\Project\A_SMART_SINHALA_APP_FOR_DEPRESSION_MONITORING_AND_MENTAL_HEALTH_SUPPORT_USING_AI\backend\firebase-credentials.json"

def check_user():
    cred = credentials.Certificate(os.environ["FIREBASE_CREDENTIALS"])
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    users_ref = db.collection('users')
    # Try username sashinitest or sashini_test
    docs = users_ref.where('username', '==', 'sashinitest').stream()
    found = False
    for doc in docs:
        print(f"User found: {json.dumps(doc.to_dict(), indent=2, default=str)}")
        found = True
    
    if not found:
        docs = users_ref.where('username', '==', 'sashini_test').stream()
        for doc in docs:
            print(f"User found (sashini_test): {json.dumps(doc.to_dict(), indent=2, default=str)}")
            found = True
            
    if not found:
        print("User not found by username")

if __name__ == "__main__":
    check_user()
