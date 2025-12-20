# 🧪 Quick API Test Commands

## PowerShell Commands (Copy & Paste)

### 1. Register User

```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "test123456"
    phone_number = "+1234567890"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### 2. Login

```powershell
$body = @{
    username = "testuser"
    password = "test123456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Save token
$TOKEN = $response.access_token
```

### 3. Get Current User (requires token)

```powershell
$headers = @{
    "Authorization" = "Bearer $TOKEN"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" `
    -Method Get `
    -Headers $headers
```

### 4. Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### 5. Create Chat Session (requires token)

```powershell
$body = @{
    message = "Hello, I feel sad today"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $TOKEN"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/chatbot/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $body
```

---

## 🚀 Run All Tests at Once

```powershell
cd backend
.\TEST_API.ps1
```

---

## 📝 Notes

- **PowerShell `curl`** is an alias for `Invoke-WebRequest` (different syntax)
- Use **`Invoke-RestMethod`** for JSON APIs (easier)
- Use **`ConvertTo-Json`** for request bodies
- Use **`-Headers`** parameter for authentication

---

## 🔍 Alternative: Use curl.exe (if installed)

If you have `curl.exe` installed, you can use:

```powershell
curl.exe -X POST "http://localhost:8000/api/auth/register" `
    -H "Content-Type: application/json" `
    -d '{\"username\":\"test\",\"email\":\"test@test.com\",\"password\":\"test123456\"}'
```

Note: Use `curl.exe` (not `curl`) to bypass PowerShell alias.


