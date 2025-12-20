# 🔐 Admin Panel Login Guide

## ✅ Yes! Admin User Can Login to Admin Panel

The admin user created via `create_admin.py` **CAN login to the admin panel**!

---

## 🎯 How It Works

### 1. **Same Authentication System**
- Admin panel uses: `/api/auth/login` (same as mobile app)
- Admin user created via script has `is_admin: True`
- Login returns JWT token
- Token stored in browser localStorage

### 2. **Backend Protection**
- Admin endpoints check: `is_admin: True`
- Non-admin users get `403 Forbidden`
- Only admins can access `/api/admin/*` endpoints

### 3. **Frontend Check** (Added)
- Admin panel now checks admin status after login
- Shows error if non-admin tries to login
- Redirects to login if admin check fails

---

## 🚀 Steps to Login

### Step 1: Create Admin User

```powershell
cd backend
.\venv\Scripts\activate
python create_admin.py
```

**Default credentials:**
- Username: `admin`
- Password: `admin123456`

### Step 2: Start Backend Server

```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

### Step 3: Start Admin Panel

```powershell
cd admin_panel
npm run dev
```

### Step 4: Login

1. Open browser: `http://localhost:3000`
2. You'll see the login page
3. Enter:
   - **Username**: `admin`
   - **Password**: `admin123456`
4. Click "Login"
5. You'll be redirected to Dashboard

---

## ✅ What You'll See

### After Successful Login:
- ✅ Redirected to Dashboard
- ✅ See all users in the system
- ✅ View user statistics
- ✅ Access alerts
- ✅ View user profiles
- ✅ Access digital twin data

### If Non-Admin Tries to Login:
- ❌ Error: "Access denied: Admin privileges required"
- ❌ Cannot access admin features
- ✅ Backend will reject with 403

---

## 🔍 Testing Admin Login

### Test via API First:

```powershell
# Login as admin
$body = @{
    username = "admin"
    password = "admin123456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$TOKEN = $response.access_token

# Check if admin
$headers = @{ Authorization = "Bearer $TOKEN" }
$userInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" `
    -Headers $headers

Write-Host "Is Admin: $($userInfo.is_admin)"
```

**Expected output:**
```
Is Admin: True
```

### Then Test Admin Panel:
1. Open `http://localhost:3000`
2. Login with admin credentials
3. Should see dashboard with all users

---

## 🛡️ Security Features

### Backend Protection:
- ✅ All `/api/admin/*` endpoints check `is_admin: True`
- ✅ Returns `403 Forbidden` if not admin
- ✅ JWT token contains username (not admin status)
- ✅ Admin status checked from Firestore on each request

### Frontend Protection:
- ✅ Checks admin status after login
- ✅ Shows error if not admin
- ✅ Dashboard shows error if access denied
- ✅ Token stored securely in localStorage

---

## 📋 Admin Panel Features

Once logged in as admin, you can:

1. **Dashboard** (`/dashboard`)
   - View all users
   - See user statistics
   - View risk levels
   - See last activity

2. **Alerts** (`/alerts`)
   - View all alerts
   - Filter by resolved/unresolved
   - Resolve alerts

3. **User Profile** (`/users/:id`)
   - View detailed user info
   - See all sessions
   - View digital twin

4. **Digital Twin** (`/digital-twin/:id`)
   - View mental health profile
   - See risk factors
   - View recommendations

---

## 🔧 Troubleshooting

### "Access denied: Admin privileges required"
- **Cause**: User doesn't have `is_admin: True` in Firestore
- **Fix**: Run `python create_admin.py` or manually set `is_admin: true` in Firestore

### "Invalid credentials"
- **Cause**: Wrong username/password
- **Fix**: Check credentials, or create new admin user

### Dashboard shows error
- **Cause**: Backend returned 403 (not admin)
- **Fix**: Verify user has `is_admin: True` in Firestore

### Cannot connect to backend
- **Cause**: Backend server not running
- **Fix**: Start backend with `python main.py`

---

## ✅ Summary

| Feature | Status |
|---------|--------|
| Admin user creation | ✅ Working |
| Admin login | ✅ Working |
| Admin panel access | ✅ Working |
| Backend protection | ✅ Working |
| Frontend check | ✅ Added |

**Your admin panel is ready to use!** 🎉

---

## 🎯 Quick Test

1. Create admin: `python create_admin.py`
2. Start backend: `python main.py`
3. Start admin panel: `npm run dev` (in admin_panel folder)
4. Login: `admin` / `admin123456`
5. See dashboard! ✅


