# PowerShell script to test API endpoints

# Test Register User
Write-Host "Testing Register User..." -ForegroundColor Cyan
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "test123456"
    phone_number = "+1234567890"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✅ Registration successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token)" -ForegroundColor Yellow
    $global:TOKEN = $response.access_token
} catch {
    Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit
}

Write-Host "`n" -NoNewline

# Test Login
Write-Host "Testing Login..." -ForegroundColor Cyan
$loginBody = @{
    username = "testuser"
    password = "test123456"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($loginResponse.access_token)" -ForegroundColor Yellow
    $global:TOKEN = $loginResponse.access_token
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" -NoNewline

# Test Get Current User (requires token)
if ($global:TOKEN) {
    Write-Host "Testing Get Current User..." -ForegroundColor Cyan
    try {
        $headers = @{
            "Authorization" = "Bearer $global:TOKEN"
        }
        
        $userResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" `
            -Method Get `
            -Headers $headers
        
        Write-Host "✅ Get user successful!" -ForegroundColor Green
        Write-Host "User Info:" -ForegroundColor Yellow
        $userResponse | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "❌ Get user failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline

# Test Health Check
Write-Host "Testing Health Check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Health check successful!" -ForegroundColor Green
    Write-Host "Status: $($health.status)" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ All tests completed!" -ForegroundColor Green













































