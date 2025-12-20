# 🚀 Complete Firestore Setup Guide - Step by Step

## 📋 Prerequisites Checklist

- [ ] Python installed
- [ ] Virtual environment activated
- [ ] Firebase account (free tier is fine)
- [ ] Code editor ready

---

## Step 1: Get Firebase Credentials (5 minutes)

### 1.1 Create/Select Firebase Project

1. Go to: **https://console.firebase.google.com/**
2. Click **"Add project"** (or select existing)
3. Enter project name: `depression-monitoring-app`
4. Click **"Continue"**
5. Disable Google Analytics (optional)
6. Click **"Create project"**
7. Wait for setup, then click **"Continue"**

### 1.2 Download Service Account Key

1. Click **⚙️ Settings** (gear icon) → **Project settings**
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Click **"Generate key"** in popup
5. JSON file downloads automatically
6. **Rename it to**: `firebase-credentials.json`
7. **Move it to**: `backend/firebase-credentials.json`

**File location should be:**
```
backend/
  └── firebase-credentials.json  ← This file
```

---

## Step 2: Enable Firestore Database (2 minutes)

### 2.1 Create Firestore Database

1. In Firebase Console, click **"Firestore Database"** (left sidebar)
2. Click **"Create database"**
3. Select **"Start in test mode"** (for development)
4. Click **"Next"**
5. Choose location (pick closest to you, e.g., `asia-south1` for Sri Lanka)
6. Click **"Enable"**
7. Wait for database creation (30 seconds)

### 2.2 Set Up Security Rules (Optional - for production later)

For now, test mode is fine. You'll update rules later.

---

## Step 3: Update Environment File (1 minute)

### 3.1 Check if `.env` exists

```powershell
cd backend
Test-Path .env
```

If it returns `False`, create it:

```powershell
Copy-Item env.template .env
```

### 3.2 Edit `.env` file

Open `backend/.env` in your editor and make sure it has:

```env
# ============================================
# Firebase Settings (REQUIRED)
# ============================================
FIREBASE_CREDENTIALS=./firebase-credentials.json

# ============================================
# JWT Settings
# ============================================
SECRET_KEY=your-secret-key-change-in-production-please-use-a-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Server Settings
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=True

# ============================================
# CORS Settings
# ============================================
ALLOWED_ORIGINS=*

# ============================================
# AI/ML Settings
# ============================================
MODEL_PATH=./models
VOICE_MODEL_PATH=./models/voice_analysis
TYPING_MODEL_PATH=./models/typing_analysis
DEPRESSION_MODEL_PATH=./models/depression_detection

# ============================================
# Google APIs (Optional)
# ============================================
GOOGLE_SPEECH_API_KEY=
GOOGLE_MAPS_API_KEY=

# ============================================
# Rasa Chatbot (Optional)
# ============================================
RASA_SERVER_URL=http://localhost:5005

# ============================================
# File Upload Settings
# ============================================
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads
```

**Important:** Make sure `FIREBASE_CREDENTIALS=./firebase-credentials.json` is set!

---

## Step 4: Install/Update Dependencies (2 minutes)

### 4.1 Activate Virtual Environment

```powershell
cd backend
.\venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### 4.2 Install Updated Requirements

```powershell
pip install -r requirements.txt
```

This will:
- ✅ Remove MySQL packages (if installed)
- ✅ Install Firebase Admin SDK
- ✅ Install all other dependencies

### 4.3 Verify Installation

```powershell
pip list | Select-String "firebase"
```

You should see:
```
firebase-admin    6.2.0
```

---

## Step 5: Test Firebase Connection (1 minute)

### 5.1 Create Test Script

Create file: `backend/test_firestore_connection.py`

```python
"""
Test Firestore connection
"""
import os
from app.services.firebase_service import initialize_firebase, get_firestore_db

def test_connection():
    """Test Firebase/Firestore connection"""
    print("🔍 Testing Firebase connection...")
    
    # Initialize Firebase
    result = initialize_firebase()
    if not result:
        print("❌ Failed to initialize Firebase")
        print("   Check FIREBASE_CREDENTIALS in .env file")
        return False
    
    print("✅ Firebase initialized successfully!")
    
    # Test Firestore
    try:
        db = get_firestore_db()
        print("✅ Firestore connection successful!")
        
        # Test write
        test_ref = db.collection('_test').document('connection')
        test_ref.set({'status': 'connected', 'timestamp': 'test'})
        print("✅ Firestore write test successful!")
        
        # Test read
        doc = test_ref.get()
        if doc.exists:
            print("✅ Firestore read test successful!")
        
        # Cleanup
        test_ref.delete()
        print("✅ Test cleanup complete!")
        
        print("\n🎉 All tests passed! Firestore is ready to use!")
        return True
        
    except Exception as e:
        print(f"❌ Firestore test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

### 5.2 Run Test

```powershell
python test_firestore_connection.py
```

**Expected output:**
```
🔍 Testing Firebase connection...
✅ Firebase initialized successfully!
✅ Firestore connection successful!
✅ Firestore write test successful!
✅ Firestore read test successful!
✅ Test cleanup complete!

🎉 All tests passed! Firestore is ready to use!
```

If you see errors, check:
- ✅ `firebase-credentials.json` exists in `backend/` folder
- ✅ `.env` has `FIREBASE_CREDENTIALS=./firebase-credentials.json`
- ✅ Firestore database is created in Firebase Console

---

## Step 6: Start the Application (1 minute)

### 6.1 Start Backend Server

```powershell
python main.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✅ Firebase initialized successfully! (Project: your-project-id)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 6.2 Test API Endpoint

Open new terminal (keep server running) and test:

```powershell
# Test health endpoint
curl http://localhost:8000/api/health
```

Or open in browser: **http://localhost:8000/api/health**

---

## Step 7: Test Complete Flow (5 minutes)

### 7.1 Register a User

```powershell
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123456",
    "phone_number": "+1234567890"
  }'
```

**Expected response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 7.2 Check Firestore

1. Go to Firebase Console
2. Click **Firestore Database**
3. You should see:
   - Collection: `users`
   - Document with user data

### 7.3 Login

```powershell
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

### 7.4 Create Chat Session

```powershell
# First, get token from login response
$TOKEN = "your-access-token-here"

curl -X POST "http://localhost:8000/api/chatbot/chat" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d '{
    "message": "Hello, I feel sad today"
  }'
```

### 7.5 Check Firestore Again

You should now see:
- `users` collection (with user)
- `sessions` collection (with chat session)

---

## Step 8: Share with Team (2 minutes)

### 8.1 Add Team Members to Firebase Project

1. Firebase Console → **⚙️ Project Settings**
2. Go to **"Users and permissions"** tab
3. Click **"Add user"**
4. Enter team member's email
5. Select role: **"Editor"** (or **"Viewer"** for read-only)
6. Click **"Add user"**

### 8.2 Team Member Setup

Each team member needs to:

1. **Get Firebase credentials:**
   - Same steps as Step 1.2
   - Download `firebase-credentials.json`
   - Place in `backend/` folder

2. **Update `.env`:**
   ```env
   FIREBASE_CREDENTIALS=./firebase-credentials.json
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run app:**
   ```powershell
   python main.py
   ```

**That's it!** Everyone uses the same Firestore database automatically.

---

## 🎯 Quick Command Reference

### Daily Development

```powershell
# 1. Activate virtual environment
cd backend
.\venv\Scripts\activate

# 2. Start server
python main.py

# 3. Test connection (if needed)
python test_firestore_connection.py
```

### Check Firestore Data

1. Go to: **https://console.firebase.google.com/**
2. Select your project
3. Click **Firestore Database**
4. Browse collections and documents

---

## ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] `firebase-credentials.json` exists in `backend/` folder
- [ ] `.env` has `FIREBASE_CREDENTIALS=./firebase-credentials.json`
- [ ] Firestore database created in Firebase Console
- [ ] `pip install -r requirements.txt` completed successfully
- [ ] `python test_firestore_connection.py` passes all tests
- [ ] `python main.py` starts without errors
- [ ] Can register user via API
- [ ] User appears in Firestore Console
- [ ] Can create chat session
- [ ] Session appears in Firestore Console

---

## 🐛 Troubleshooting

### Error: "Firebase not initialized"

**Solution:**
1. Check `firebase-credentials.json` exists
2. Check `.env` has correct path
3. Verify JSON file is valid (not corrupted)

### Error: "Permission denied"

**Solution:**
1. Check Firestore is in **test mode**
2. Or update security rules in Firebase Console

### Error: "Module not found: firebase_admin"

**Solution:**
```powershell
pip install firebase-admin==6.2.0
```

### Error: "Collection not found"

**Solution:**
- This is normal! Collections are created automatically when you write data
- Just use the API and collections will appear

---

## 🎉 Success!

If all steps completed successfully, your app is now:
- ✅ Using Firestore (no MySQL needed)
- ✅ Ready for team sharing
- ✅ Real-time updates enabled
- ✅ Offline support ready
- ✅ Push notifications ready

**Start building!** 🚀

