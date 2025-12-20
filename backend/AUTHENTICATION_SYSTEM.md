# 🔐 Authentication System Overview

## ✅ Firebase Connection Confirmed!

Your successful registration means:
- ✅ Firebase/Firestore is connected
- ✅ Users are being stored in Firestore
- ✅ Authentication is working

---

## 👥 Two Types of Users

### 1. **Patient Users** (Mobile App Users)
- **Register**: `/api/auth/register`
- **Login**: `/api/auth/login`
- **Default Role**: `is_admin: False`
- **Access**: Patient features only
  - Chatbot sessions
  - Voice analysis
  - Typing analysis
  - Digital twin profile
  - Their own data only

### 2. **Admin Users** (Admin Panel Users)
- **Login**: `/api/auth/login` (same endpoint!)
- **Required**: `is_admin: True` in Firestore
- **Access**: Admin features
  - View all users
  - View all sessions
  - View alerts
  - Access dashboard
  - View user profiles

---

## 🔑 How It Works

### Same Authentication System

Both patient and admin users:
1. **Login** using the same endpoint: `/api/auth/login`
2. **Get JWT token** in response
3. **Use token** in `Authorization: Bearer <token>` header
4. **Access** different endpoints based on their role

### Role-Based Access Control

```python
# Patient endpoint (no admin check)
@router.post("/chat")
async def chat(current_user: dict = Depends(get_current_user)):
    # Any logged-in user can access
    ...

# Admin endpoint (checks is_admin)
@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    if not current_user.get('is_admin', False):
        raise HTTPException(403, "Admin access required")
    # Only admins can access
    ...
```

---

## 📋 User Registration Flow

### Patient Registration
```json
POST /api/auth/register
{
  "username": "patient123",
  "email": "patient@example.com",
  "password": "password123",
  "phone_number": "+1234567890"
}
```

**Result:**
- User created in Firestore
- `is_admin: False` (default)
- JWT token returned
- Can use mobile app

### Admin Creation
Admins are **NOT created via registration**. They must be:
1. Created manually in Firestore, OR
2. Created via a script (see below)

---

## 🛠️ Creating an Admin User

### Option 1: Manual in Firestore Console

1. Go to Firebase Console → Firestore Database
2. Find the user in `users` collection
3. Edit the document
4. Set `is_admin: true`
5. Save

### Option 2: Use Script (Recommended)

Create file: `backend/create_admin.py`

```python
from app.services.firestore_service import FirestoreService
from app.routes.auth import get_password_hash

# Create admin user
firestore_service = FirestoreService()

admin_data = {
    'username': 'admin',
    'email': 'admin@hospital.com',
    'hashed_password': get_password_hash('admin123456'),
    'is_active': True,
    'is_admin': True  # ← This makes them admin!
}

user_id = firestore_service.create_user(admin_data)
print(f"Admin user created! ID: {user_id}")
print("Login with: username='admin', password='admin123456'")
```

Run:
```powershell
python create_admin.py
```

---

## 🔍 Checking User Role

### In Backend Code
```python
current_user = Depends(get_current_user)

# Check if admin
if current_user.get('is_admin', False):
    # Admin access
else:
    # Patient access
```

### In Frontend (Mobile App)
```dart
// After login, check user role
final userInfo = await apiService.getCurrentUser();
if (userInfo['is_admin'] == true) {
  // Show admin features
} else {
  // Show patient features
}
```

---

## 📊 Current Setup

### Patient Endpoints (No Admin Check)
- ✅ `/api/auth/register` - Register new patient
- ✅ `/api/auth/login` - Login (patient or admin)
- ✅ `/api/auth/me` - Get current user info
- ✅ `/api/chatbot/chat` - Chat with bot
- ✅ `/api/voice/analyze` - Analyze voice
- ✅ `/api/typing/analyze` - Analyze typing
- ✅ `/api/digital-twin/profile` - Get digital twin

### Admin Endpoints (Requires `is_admin: True`)
- ✅ `/api/admin/dashboard` - View all users
- ✅ `/api/admin/alerts` - View alerts
- ✅ `/api/admin/alerts/{id}/resolve` - Resolve alert
- ✅ `/api/admin/users/{id}/profile` - View user profile

---

## 🎯 Summary

| Feature | Patient Users | Admin Users |
|---------|--------------|-------------|
| **Register** | ✅ Yes | ❌ No (manual creation) |
| **Login** | ✅ Yes | ✅ Yes |
| **JWT Token** | ✅ Yes | ✅ Yes |
| **Access Own Data** | ✅ Yes | ✅ Yes |
| **Access All Users** | ❌ No | ✅ Yes |
| **Admin Dashboard** | ❌ No | ✅ Yes |
| **Create Alerts** | ✅ Yes (via analysis) | ✅ Yes (manual) |

---

## ✅ Next Steps

1. **Test Patient Login**:
   ```powershell
   # Use the user you just registered
   $body = @{username="testuser2"; password="test123456"} | ConvertTo-Json
   Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -ContentType "application/json" -Body $body
   ```

2. **Create Admin User**:
   - Use the script above, OR
   - Manually set `is_admin: true` in Firestore

3. **Test Admin Access**:
   - Login as admin
   - Access `/api/admin/dashboard`
   - Should see all users

---

## 🔒 Security Notes

- ✅ Passwords are hashed with bcrypt
- ✅ JWT tokens expire after 30 minutes (configurable)
- ✅ Admin endpoints check `is_admin` flag
- ✅ Users can only access their own data (patient endpoints)
- ✅ Firestore security rules should be updated for production

---

**Your authentication system is ready for both patients and admins!** 🎉

