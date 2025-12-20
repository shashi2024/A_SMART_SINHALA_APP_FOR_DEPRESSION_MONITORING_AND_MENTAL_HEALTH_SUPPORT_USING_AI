"""
Firebase service for cloud storage, notifications, etc.
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, storage, messaging, firestore
from app.config import settings
from typing import Optional, Dict, List

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        import codecs
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # If encoding fix fails, continue anyway

# Initialize Firebase (only once)
_firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    cred_path = settings.FIREBASE_CREDENTIALS
    
    if not cred_path or not os.path.exists(cred_path):
        print("[WARNING] Firebase credentials not found. Firebase features disabled.")
        print(f"          Expected path: {cred_path}")
        print("          To enable Firebase, download credentials from Firebase Console")
        print("          and set FIREBASE_CREDENTIALS in .env file")
        return False
    
    try:
        cred = credentials.Certificate(cred_path)
        
        # Get project ID from credentials
        with open(cred_path, 'r') as f:
            import json
            cred_data = json.load(f)
            project_id = cred_data.get('project_id', '')
            storage_bucket = f"{project_id}.appspot.com"
        
        firebase_admin.initialize_app(cred, {
            'storageBucket': storage_bucket
        })
        _firebase_initialized = True
        print(f"[OK] Firebase initialized successfully! (Project: {project_id})")
        return True
    except Exception as e:
        print(f"[ERROR] Firebase initialization failed: {e}")
        return False

def is_firebase_initialized() -> bool:
    """Check if Firebase is initialized"""
    return _firebase_initialized

def upload_file_to_storage(local_file_path: str, cloud_file_path: str) -> Optional[str]:
    """
    Upload file to Firebase Cloud Storage
    
    Args:
        local_file_path: Path to local file
        cloud_file_path: Path in cloud storage (e.g., 'voice_recordings/user123.wav')
    
    Returns:
        Public URL of uploaded file, or None if failed
    """
    if not _firebase_initialized:
        raise Exception("Firebase not initialized. Check FIREBASE_CREDENTIALS in .env")
    
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local file not found: {local_file_path}")
    
    try:
        bucket = storage.bucket()
        blob = bucket.blob(cloud_file_path)
        blob.upload_from_filename(local_file_path)
        blob.make_public()
        
        return blob.public_url
    except Exception as e:
        print(f"❌ Failed to upload file to Firebase Storage: {e}")
        return None

def delete_file_from_storage(cloud_file_path: str) -> bool:
    """
    Delete file from Firebase Cloud Storage
    
    Args:
        cloud_file_path: Path in cloud storage
    
    Returns:
        True if deleted, False otherwise
    """
    if not _firebase_initialized:
        return False
    
    try:
        bucket = storage.bucket()
        blob = bucket.blob(cloud_file_path)
        blob.delete()
        return True
    except Exception as e:
        print(f"❌ Failed to delete file from Firebase Storage: {e}")
        return False

def send_push_notification(
    fcm_token: str, 
    title: str, 
    body: str, 
    data: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Send push notification to user's device
    
    Args:
        fcm_token: Firebase Cloud Messaging token from user's device
        title: Notification title
        body: Notification body
        data: Optional data payload (key-value pairs)
    
    Returns:
        Message ID if successful, None otherwise
    """
    if not _firebase_initialized:
        raise Exception("Firebase not initialized. Check FIREBASE_CREDENTIALS in .env")
    
    if not fcm_token:
        raise ValueError("FCM token is required")
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )
        
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"❌ Failed to send push notification: {e}")
        return None

def send_multicast_notification(
    fcm_tokens: list,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Send push notification to multiple devices
    
    Args:
        fcm_tokens: List of FCM tokens
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        Dictionary with success_count and failure_count
    """
    if not _firebase_initialized:
        raise Exception("Firebase not initialized")
    
    if not fcm_tokens:
        return {"success_count": 0, "failure_count": 0}
    
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=fcm_tokens,
        )
        
        response = messaging.send_multicast(message)
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count
        }
    except Exception as e:
        print(f"❌ Failed to send multicast notification: {e}")
        return {"success_count": 0, "failure_count": len(fcm_tokens)}

# ============================================
# Firestore (Real-time Database) Functions
# ============================================

def get_firestore_db():
    """
    Get Firestore database instance
    
    Returns:
        Firestore client
    """
    if not _firebase_initialized:
        raise Exception("Firebase not initialized")
    return firestore.client()

def update_user_realtime_data(user_id: int, data: Dict):
    """
    Update user's real-time data in Firestore
    This enables real-time updates across devices
    
    Args:
        user_id: User ID
        data: Data to update (e.g., {'depression_score': 0.75, 'risk_level': 'high'})
    """
    if not _firebase_initialized:
        return
    
    try:
        db = get_firestore_db()
        db.collection('users').document(str(user_id)).set({
            **data,
            'last_updated': firestore.SERVER_TIMESTAMP
        }, merge=True)
    except Exception as e:
        print(f"❌ Failed to update Firestore: {e}")

def get_user_realtime_data(user_id: int) -> Optional[Dict]:
    """
    Get user's real-time data from Firestore
    
    Args:
        user_id: User ID
    
    Returns:
        User data dictionary or None
    """
    if not _firebase_initialized:
        return None
    
    try:
        db = get_firestore_db()
        doc = db.collection('users').document(str(user_id)).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Failed to get Firestore data: {e}")
        return None

def listen_to_user_updates(user_id: int, callback):
    """
    Listen to real-time updates for a user
    (This is typically used on the client side, but can be used here too)
    
    Args:
        user_id: User ID
        callback: Function to call when data changes
    """
    if not _firebase_initialized:
        return
    
    try:
        db = get_firestore_db()
        doc_ref = db.collection('users').document(str(user_id))
        
        def on_snapshot(doc_snapshot, changes, read_time):
            if doc_snapshot.exists:
                callback(doc_snapshot.to_dict())
        
        doc_ref.on_snapshot(on_snapshot)
    except Exception as e:
        print(f"❌ Failed to set up Firestore listener: {e}")

def create_alert_realtime(alert_data: Dict) -> Optional[str]:
    """
    Create a real-time alert in Firestore
    This enables instant notifications across all devices
    
    Args:
        alert_data: Alert information (user_id, type, severity, message, etc.)
    
    Returns:
        Alert document ID
    """
    if not _firebase_initialized:
        return None
    
    try:
        db = get_firestore_db()
        doc_ref = db.collection('alerts').add({
            **alert_data,
            'created_at': firestore.SERVER_TIMESTAMP,
            'is_resolved': False
        })
        return doc_ref[1].id
    except Exception as e:
        print(f"❌ Failed to create real-time alert: {e}")
        return None

def send_notification_with_realtime_update(
    user_id: int,
    fcm_token: str,
    title: str,
    body: str,
    alert_data: Optional[Dict] = None
):
    """
    Send push notification AND update Firestore for real-time sync
    
    Args:
        user_id: User ID
        fcm_token: FCM token
        title: Notification title
        body: Notification body
        alert_data: Additional data to store in Firestore
    """
    # Send push notification
    send_push_notification(fcm_token, title, body, alert_data)
    
    # Update Firestore for real-time sync
    if alert_data:
        update_user_realtime_data(user_id, {
            'latest_alert': {
                'title': title,
                'body': body,
                **alert_data
            }
        })
        
        # Also create alert document
        create_alert_realtime({
            'user_id': user_id,
            'title': title,
            'body': body,
            **alert_data
        })

