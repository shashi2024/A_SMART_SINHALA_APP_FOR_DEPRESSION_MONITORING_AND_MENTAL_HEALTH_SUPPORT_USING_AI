
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

# Set path to service account key
os.environ["FIREBASE_CREDENTIALS"] = r"d:\Studies\Sliit\Research Documents\Project\A_SMART_SINHALA_APP_FOR_DEPRESSION_MONITORING_AND_MENTAL_HEALTH_SUPPORT_USING_AI\backend\firebase-credentials.json"

def check_user_details():
    cred = credentials.Certificate(os.environ["FIREBASE_CREDENTIALS"])
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    # 1. Check User
    user_id = "1BHQUr0L2hYt5ONqBLPK"
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        print(f"User Data: {json.dumps(user_doc.to_dict(), indent=2, default=str)}")
    else:
        print("User not found")
        return

    # 2. Check Sessions
    sessions_ref = db.collection('sessions').where('user_id', '==', user_id).stream()
    sessions = []
    for s in sessions_ref:
        sessions.append(s.to_dict())
    print(f"Total Sessions: {len(sessions)}")
    if sessions:
        print(f"Sample Session: {json.dumps(sessions[0], indent=2, default=str)}")

if __name__ == "__main__":
    check_user_details()
