import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.firestore_service import FirestoreService
    db_service = FirestoreService()
    
    analyses_ref = db_service.db.collection('biofeedback_analyses')
    query = analyses_ref.where('user_id', '==', 'VYhYDBJ9T7Oqpe29aCUk')
    
    print("All Biofeedback Analyses for User VYhYDBJ9T7Oqpe29aCUk:")
    for doc in query.stream():
        data = doc.to_dict()
        user_id = data.get('user_id')
        timestamp = data.get('timestamp')
        created_at = data.get('created_at')
        print(f"Doc ID: {doc.id} | Timestamp: {timestamp} | Created At: {created_at}")
except Exception as e:
    print(f"Error: {e}")
