# 🚀 Quick Start Guide

Get the project running in 5 minutes!

## 📋 Prerequisites

- **Python 3.9+** (for backend)
- **Java 21** (for Android builds)
- **Node.js 18+** (for admin panel)
- **Flutter 3.0+** (for mobile app)
- **Android phone** with USB debugging enabled

## ⚡ Quick Run (3 Steps)

### Step 1: Start Backend
```bash
# Double-click: run_backend.bat
# OR run manually:
cd backend
venv\Scripts\activate
python main.py
```
✅ Backend runs at: `http://localhost:8000`

### Step 2: Start Frontend (Phone)
```bash
# Connect your Android phone via USB
# Double-click: run_frontend_phone.bat
# OR run manually:
cd frontend
flutter pub get
flutter run -d <your_device_id>
```

**Important:** Update API URL in `frontend/lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://YOUR_COMPUTER_IP:8000/api';
// Find your IP: Run 'ipconfig' in terminal
```

### Step 3: Start Admin Panel (Optional)
```bash
# Double-click: run_admin_panel.bat
# OR run manually:
cd admin_panel
npm install
npm run dev
```
✅ Admin panel runs at: `http://localhost:5173`

## 📱 First Time Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
flutter pub get
```

### Admin Panel Setup
```bash
cd admin_panel
npm install
```

## 🔧 Common Issues

### Backend won't start?
- Check Python is installed: `python --version`
- Activate virtual environment: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't build?
- Check Java 21: `java -version`
- Check Flutter: `flutter doctor`
- Clean build: `flutter clean && flutter pub get`

### Phone not detected?
- Enable USB Debugging in phone settings
- Check connection: `flutter devices`
- Accept USB debugging prompt on phone

## 📞 Need Help?

Check `README.md` for detailed information about the project.

