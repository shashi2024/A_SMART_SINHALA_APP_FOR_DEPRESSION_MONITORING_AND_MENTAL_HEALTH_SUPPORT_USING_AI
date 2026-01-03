# 🔧 Troubleshooting Login & Registration Issues

## Quick Checks

### 1. **Verify Backend is Running**
```powershell
# Check if backend is running
curl http://localhost:8000/health
# Or open in browser: http://localhost:8000/docs
```

### 2. **Check Browser Console**
1. Open Chrome DevTools (F12)
2. Go to **Console** tab
3. Look for errors like:
   - `Failed to load resource`
   - `CORS policy`
   - `Network error`
   - `Login API Error`

### 3. **Check Network Tab**
1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Try to login
4. Look for the `/api/auth/login` request
5. Check:
   - **Status Code** (should be 200)
   - **Request URL** (should be `http://localhost:8000/api/auth/login`)
   - **Response** (should contain `access_token`)

## Common Issues & Solutions

### Issue 1: "Cannot connect to server"
**Cause:** Backend not running or wrong URL

**Solution:**
1. Make sure backend is running:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python main.py
   ```
2. Verify it's running: Open `http://localhost:8000/docs` in browser
3. Check API URL in `frontend/lib/services/api_service.dart` is `http://localhost:8000/api`

### Issue 2: "CORS policy" error
**Cause:** CORS not configured correctly

**Solution:**
- Backend should already have CORS enabled
- Check `backend/main.py` has CORS middleware
- If still having issues, check browser console for exact CORS error

### Issue 3: "Login failed" but backend works
**Cause:** Frontend error handling issue

**Solution:**
1. Check browser console for actual error
2. Check Network tab to see the actual API response
3. Verify the error message matches the backend response

### Issue 4: "401 Unauthorized"
**Cause:** Wrong username/password

**Solution:**
- Use test credentials:
  - Username: `test`
  - Password: `test1234`
- Or create new user via registration

### Issue 5: "Username already exists"
**Cause:** User already registered

**Solution:**
- Use different username
- Or login with existing credentials

## Testing Steps

### Step 1: Test Backend Directly
```powershell
cd backend
.\venv\Scripts\python.exe -c "import requests; r = requests.post('http://localhost:8000/api/auth/login', json={'username': 'test', 'password': 'test1234'}); print(f'Status: {r.status_code}'); print(f'Response: {r.text}')"
```

**Expected:** Status 200, Response with `access_token`

### Step 2: Test Frontend
1. Open app in Chrome
2. Open DevTools (F12)
3. Go to Console tab
4. Try to login
5. Check for errors

### Step 3: Check Network Request
1. Open DevTools (F12)
2. Go to Network tab
3. Try to login
4. Click on `/api/auth/login` request
5. Check:
   - **Request URL**: Should be `http://localhost:8000/api/auth/login`
   - **Request Method**: POST
   - **Request Payload**: Should have `username` and `password`
   - **Status Code**: Should be 200
   - **Response**: Should have `access_token`

## Debug Information

### Enable Debug Logging
The app now has debug logging enabled. Check browser console for:
- `Login API Error: ...`
- `Login error: ...`
- `Network error: ...`

### Check API Response
If login fails, check the Network tab to see the actual response from the backend. The response should tell you exactly what went wrong.

## Still Not Working?

1. **Check Backend Logs**
   - Look at the terminal where backend is running
   - Check for any error messages

2. **Verify Test User Exists**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe create_test_user.py
   ```

3. **Try Registration Instead**
   - Use a new username/email
   - If registration works but login doesn't, there might be a password hashing issue

4. **Check Firestore Connection**
   - Make sure Firebase credentials are set in `.env`
   - Check backend logs for Firebase initialization errors

## Test Credentials

- **Username:** `test`
- **Password:** `test1234`
- **Email:** `test@example.com`

These credentials were created by `create_test_user.py` script.

