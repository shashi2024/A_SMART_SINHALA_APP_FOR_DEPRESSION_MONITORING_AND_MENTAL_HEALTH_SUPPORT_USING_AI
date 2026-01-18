@echo off
echo Building APK for Android...
echo.

cd frontend

echo Step 1: Getting Flutter dependencies...
call flutter pub get

echo.
echo Step 2: Building APK (Debug mode for testing)...
call flutter build apk --debug

echo.
echo Build complete!
echo.
echo APK location: frontend\build\app\outputs\flutter-apk\app-debug.apk
echo.
echo To build a release APK (smaller size, optimized), run:
echo   flutter build apk --release
echo.
pause















