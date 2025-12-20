# 🚀 START HERE - Complete Setup in 10 Minutes

## ✅ Quick Checklist

Follow these steps in order:

---

## Step 1: Get Firebase Credentials (5 min)

1. Go to: **https://console.firebase.google.com/**
2. Create/Select project
3. ⚙️ Settings → **Project settings** → **Service accounts**
4. Click **"Generate new private key"**
5. Download JSON file
6. **Rename to**: `firebase-credentials.json`
7. **Move to**: `backend/firebase-credentials.json`

---

## Step 2: Enable Firestore (2 min)

1. Firebase Console → **Firestore Database**
2. Click **"Create database"**
3. Select **"Start in test mode"**
4. Choose location
5. Click **"Enable"**

---

## Step 3: Update .env File (1 min)

Open `backend/.env` and add:

```env
FIREBASE_CREDENTIALS=./firebase-credentials.json
```

---

## Step 4: Run These Commands (2 min)

Open PowerShell in `backend` folder:

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test connection
python test_firestore_connection.py

# Start server
python main.py
```

---

## Step 5: Test It Works

Open browser: **http://localhost:8000/api/health**

Or test register:

```powershell
curl -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{"username":"test","email":"test@test.com","password":"test123456"}'
```

---

## ✅ Done!

If you see:
- ✅ Firebase initialized successfully
- ✅ Server running on http://0.0.0.0:8000
- ✅ Can register users

**You're all set!** 🎉

---

## 📚 Need More Details?

- **Complete Guide**: `COMPLETE_SETUP_GUIDE.md`
- **All Commands**: `SETUP_COMMANDS.md`
- **Migration Info**: `FIRESTORE_MIGRATION_COMPLETE.md`

---

## 🐛 Problems?

1. **"Firebase not initialized"**
   - Check `firebase-credentials.json` exists
   - Check `.env` has correct path

2. **"Module not found"**
   - Run: `pip install -r requirements.txt`

3. **"Permission denied"**
   - Make sure Firestore is in **test mode**

---

## 🎯 Next Steps

1. Test all API endpoints
2. Check Firestore Console for data
3. Share Firebase project with team
4. Start building features!

**Good luck!** 🚀

