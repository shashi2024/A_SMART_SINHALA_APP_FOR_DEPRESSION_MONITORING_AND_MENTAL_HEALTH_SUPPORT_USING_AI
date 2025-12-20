# Firebase Setup Guide

## 🤔 Is Firebase Good? When to Use It?

### ✅ Firebase is Great For:
- **Push Notifications** - Alert users about high-risk situations
- **Cloud Storage** - Store audio files, images securely
- **Real-time Database** - Live updates without polling
- **Cloud Functions** - Serverless backend operations
- **Analytics** - Track app usage and user behavior
- **Authentication** - User login (though you already have JWT)

### ⚠️ You Might NOT Need Firebase If:
- ✅ You already have MySQL for database (you do!)
- ✅ You already have JWT authentication (you do!)
- ✅ You're storing files locally (you can)
- ✅ You don't need real-time features

### 💡 Recommendation for Your Project:
**Firebase is OPTIONAL** but could be useful for:
1. **Push Notifications** - Send alerts to users' phones
2. **Cloud Storage** - Store voice recordings in the cloud
3. **Real-time Alerts** - Notify admins immediately

---

## 🚀 Step-by-Step Setup

### Step 1: Create Firebase Project

1. **Go to Firebase Console:**
   - Visit: https://console.firebase.google.com/
   - Sign in with Google account

2. **Create New Project:**
   - Click "Add project" or "Create a project"
   - Project name: `depression-monitoring-app`
   - Click "Continue"
   - Disable Google Analytics (optional, for free tier)
   - Click "Create project"
   - Wait for project creation (30 seconds)

3. **Project Created!** ✅

---

### Step 2: Enable Required Services

#### A. **Firebase Admin SDK** (For Backend)

1. In Firebase Console, click the **gear icon** ⚙️ (Project Settings)
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Click **"Generate key"** in the popup
5. A JSON file will download - **SAVE THIS FILE!**
   - File name: `depression-monitoring-firebase-adminsdk-xxxxx.json`
   - **IMPORTANT**: Keep this file secure, never commit to Git!

#### B. **Cloud Storage** (Optional - for audio files)

1. In Firebase Console, click **"Storage"** in left menu
2. Click **"Get started"**
3. Start in **test mode** (for development)
4. Choose location (closest to your users)
5. Click **"Done"**

#### C. **Cloud Messaging** (Optional - for push notifications)

1. In Firebase Console, click **"Cloud Messaging"** in left menu
2. It's automatically enabled - no setup needed!

---

### Step 3: Install Firebase Admin SDK

The package is already in your `requirements.txt`, but make sure it's installed:

```bash
cd backend
.\venv\Scripts\activate
pip install firebase-admin
```

---

### Step 4: Configure Firebase in Your Project

#### A. **Place Credentials File**

1. Move the downloaded JSON file to `backend/` directory
2. Rename it to: `firebase-credentials.json`
3. **Verify it's in `.gitignore`** (it should be already)

#### B. **Update `.env` File**

Open `backend/.env` and add:

```env
# Firebase Settings
FIREBASE_CREDENTIALS=./firebase-credentials.json
```

Or use the full path:
```env
FIREBASE_CREDENTIALS=D:\Studies\Sliit\Research Documents\Project\A_SMART_SINHALA_APP_FOR_DEPRESSION_MONITORING_AND_MENTAL_HEALTH_SUPPORT_USING_AI\backend\firebase-credentials.json
```

---

### Step 5: Initialize Firebase in Your Code

Create a new file: `backend/app/services/firebase_service.py`

```python
"""
Firebase service for cloud storage, notifications, etc.
"""

import os
import firebase_admin
from firebase_admin import credentials, storage, messaging
from app.config import settings

# Initialize Firebase (only once)
_firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    cred_path = settings.FIREBASE_CREDENTIALS
    
    if not cred_path or not os.path.exists(cred_path):
        print("⚠️  Firebase credentials not found. Firebase features disabled.")
        return
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-project-id.appspot.com'  # Replace with your bucket name
        })
        _firebase_initialized = True
        print("✅ Firebase initialized successfully!")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")

def upload_file_to_storage(local_file_path: str, cloud_file_path: str) -> str:
    """Upload file to Firebase Cloud Storage"""
    if not _firebase_initialized:
        raise Exception("Firebase not initialized")
    
    bucket = storage.bucket()
    blob = bucket.blob(cloud_file_path)
    blob.upload_from_filename(local_file_path)
    blob.make_public()
    
    return blob.public_url

def send_push_notification(fcm_token: str, title: str, body: str, data: dict = None):
    """Send push notification to user's device"""
    if not _firebase_initialized:
        raise Exception("Firebase not initialized")
    
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
```

---

### Step 6: Initialize Firebase on App Startup

Update `backend/main.py`:

```python
from app.services.firebase_service import initialize_firebase

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await init_db()
    initialize_firebase()  # Add this line
```

---

## 📱 Frontend Setup (Flutter - Optional)

If you want push notifications in your Flutter app:

### Step 1: Add Firebase to Flutter

1. Install FlutterFire CLI:
   ```bash
   dart pub global activate flutterfire_cli
   ```

2. Configure Firebase:
   ```bash
   cd frontend
   flutterfire configure
   ```
   - Select your Firebase project
   - Select platforms (Android, iOS)

3. Add dependencies to `pubspec.yaml`:
   ```yaml
   dependencies:
     firebase_core: ^2.24.0
     firebase_messaging: ^14.7.0
     firebase_storage: ^11.5.0
   ```

4. Run:
   ```bash
   flutter pub get
   ```

---

## 🧪 Test Firebase Connection

Create a test script: `backend/test_firebase.py`

```python
"""Test Firebase connection"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import initialize_firebase

print("Testing Firebase connection...")
try:
    initialize_firebase()
    print("✅ Firebase connection successful!")
except Exception as e:
    print(f"❌ Firebase connection failed: {e}")
```

Run it:
```bash
python test_firebase.py
```

---

## 🔐 Security Best Practices

1. ✅ **Never commit** `firebase-credentials.json` to Git
2. ✅ **Use environment variables** for sensitive data
3. ✅ **Restrict Storage rules** in production
4. ✅ **Use service account** with minimal permissions
5. ✅ **Rotate keys** regularly

---

## 💰 Firebase Pricing

### Free Tier (Spark Plan):
- ✅ **Storage**: 5 GB
- ✅ **Bandwidth**: 1 GB/day
- ✅ **Cloud Messaging**: Unlimited
- ✅ **Cloud Functions**: 2 million invocations/month

**For your project, free tier should be enough!**

---

## 📚 Common Use Cases

### 1. Upload Audio Files to Cloud Storage

```python
from app.services.firebase_service import upload_file_to_storage

# After saving audio file locally
cloud_url = upload_file_to_storage(
    local_file_path="uploads/audio.wav",
    cloud_file_path="voice_recordings/user123_session456.wav"
)
```

### 2. Send Push Notification

```python
from app.services.firebase_service import send_push_notification

send_push_notification(
    fcm_token="user_device_token",
    title="High Risk Alert",
    body="Your depression score indicates high risk. Please contact support.",
    data={"alert_type": "high_risk", "user_id": "123"}
)
```

### 3. Store User FCM Tokens

Add to your `users` table:
```sql
ALTER TABLE users ADD COLUMN fcm_token VARCHAR(255);
```

---

## ❓ Troubleshooting

### Error: "Firebase credentials not found"
- Check if `firebase-credentials.json` exists
- Verify path in `.env` file
- Check file permissions

### Error: "Permission denied"
- Check Storage rules in Firebase Console
- Verify service account has proper permissions

### Error: "Module not found"
```bash
pip install firebase-admin
```

---

## 🎯 Summary

1. ✅ Create Firebase project at https://console.firebase.google.com/
2. ✅ Download service account JSON
3. ✅ Place file as `firebase-credentials.json` in `backend/`
4. ✅ Update `.env` with file path
5. ✅ Initialize Firebase in your code
6. ✅ Use Firebase services (Storage, Messaging, etc.)

**Firebase is optional but adds powerful features!** 🚀

---

## 🔗 Useful Links

- **Firebase Console**: https://console.firebase.google.com/
- **Firebase Admin SDK Docs**: https://firebase.google.com/docs/admin/setup
- **Firebase Storage**: https://firebase.google.com/docs/storage
- **Cloud Messaging**: https://firebase.google.com/docs/cloud-messaging


