@echo off
REM Batch script to run chatbot tests on Windows

echo ========================================
echo Chatbot Test Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if backend server is running
echo Checking if backend server is running...
curl -s http://localhost:8000/docs >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend server might not be running on http://localhost:8000
    echo Please start the backend server first:
    echo   cd backend
    echo   python -m uvicorn main:app --reload
    echo.
    pause
)

echo.
echo Running chatbot tests...
echo.

REM Run the test script
python test_chatbot.py

echo.
echo ========================================
echo Tests completed!
echo ========================================
pause









