@echo off
echo ========================================
echo Starting Flutter Frontend (Physical Device)
echo ========================================
echo.
echo This will run the app on your Android phone connected via USB
echo.
echo IMPORTANT: Before running this script:
echo   1. Enable Developer Options on your phone
echo   2. Enable USB Debugging
echo   3. Connect your phone via USB
echo   4. Accept the USB debugging prompt on your phone
echo.
pause

REM Change to script directory (project root)
cd /d "%~dp0"

REM Verify we're in the right place
if not exist "frontend\pubspec.yaml" (
    echo.
    echo ERROR: pubspec.yaml not found in frontend directory!
    echo.
    echo Current directory: %CD%
    echo.
    echo Please make sure you run this script from the project root directory.
    echo.
    pause
    exit /b 1
)

cd frontend

echo.
echo Step 1: Installing Flutter dependencies...
flutter pub get
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Checking for connected devices...
flutter devices
echo.

REM Check if any Android device is connected
flutter devices | findstr /i "android" >nul
if errorlevel 1 (
    echo.
    echo ERROR: No Android device detected!
    echo.
    echo Please ensure:
    echo   1. Your phone is connected via USB
    echo   2. USB Debugging is enabled
    echo   3. You accepted the USB debugging prompt on your phone
    echo   4. USB drivers are installed (if needed)
    echo.
    echo To enable USB Debugging:
    echo   1. Go to Settings ^> About Phone
    echo   2. Tap "Build Number" 7 times to enable Developer Options
    echo   3. Go to Settings ^> Developer Options
    echo   4. Enable "USB Debugging"
    echo.
    echo Checking ADB connection...
    adb devices
    echo.
    pause
    exit /b 1
)

echo.
echo Step 3: Device detected! Starting Flutter app...
echo.
echo Note: Make sure your backend is running at http://localhost:8000
echo       For physical device, you may need to use your computer's IP address
echo       instead of localhost in the app configuration.
echo.
pause

echo.
echo Starting Flutter app on your phone...
echo.
flutter run
pause

