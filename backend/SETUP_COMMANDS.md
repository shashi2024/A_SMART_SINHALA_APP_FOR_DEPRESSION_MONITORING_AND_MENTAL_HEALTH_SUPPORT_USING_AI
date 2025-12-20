# 📝 All Commands to Run - Copy & Paste

## Step-by-Step Commands

### 1. Navigate to Backend

```powershell
cd backend
```

### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\activate
```

### 3. Check if .env exists

```powershell
Test-Path .env
```

If `False`, create it:

```powershell
Copy-Item env.template .env
```

### 4. Install/Update Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Test Firebase Connection

```powershell
python test_firestore_connection.py
```

### 6. Start Application

```powershell
python main.py
```

---

## 🧪 Test API Commands

### Register User

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

### Login

```powershell
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

### Create Chat Session (Replace TOKEN)

```powershell
$TOKEN = "your-token-here"

curl -X POST "http://localhost:8000/api/chatbot/chat" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d '{
    "message": "Hello, I feel sad today"
  }'
```

---

## 🔍 Verification Commands

### Check Firebase Package

```powershell
pip list | Select-String "firebase"
```

### Check if credentials file exists

```powershell
Test-Path firebase-credentials.json
```

### Check .env file

```powershell
Get-Content .env | Select-String "FIREBASE"
```

---

## 📋 Complete Setup Script (Run All at Once)

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\activate

# Create .env if not exists
if (-not (Test-Path .env)) {
    Copy-Item env.template .env
    Write-Host "✅ Created .env file - Please edit it!"
}

# Install dependencies
pip install -r requirements.txt

# Test connection
python test_firestore_connection.py

# Start server
Write-Host "🚀 Starting server..."
python main.py
```

---

## 🎯 Quick Start (After Initial Setup)

```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

That's it! 🎉

