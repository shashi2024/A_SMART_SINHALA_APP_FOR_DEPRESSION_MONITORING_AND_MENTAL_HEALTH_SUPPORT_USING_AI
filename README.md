# 🧠 Smart Sinhala App for Depression Monitoring

AI-powered mental health support app with Sinhala, Tamil, and English language support.

## 🎯 Features

- **Voice Call Analysis** - Depression detection from voice with call bot detection
- **Fake Call Detector** - Detect the fake calles like spam, AI , joke calles
- **Chat Support** - AI chatbot in Sinhala/Tamil/English
- **Typing Analysis** - Keystroke pattern analysis
- **Multi-language** - Sinhala (සිංහල), Tamil (தமிழ்), English
- **Admin Dashboard** - Monitor users and alerts

## 🚀 Quick Start

See **[QUICK_START.md](QUICK_START.md)** for step-by-step setup.

### TL;DR
1. Start backend: `run_backend.bat`
2. Start frontend: `run_frontend_phone.bat` (connect phone first)
3. Start admin: `run_admin_panel.bat` (optional)

## 📁 Project Structure

```
├── backend/          # FastAPI server
├── frontend/         # Flutter mobile app
├── admin_panel/      # React admin dashboard
└── ai_models/        # ML training scripts
```

## 🔧 Requirements

- Python 3.9+
- Java 21
- Node.js 18+
- Flutter 3.0+
- Android phone with USB debugging / chrome / edge (refer the guidlines)

## 📱 Running on Phone

1. **Enable USB Debugging:**
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Connect phone via USB**

3. **Update API URL:**
   - Edit `frontend/lib/services/api_service.dart`
   - Change `localhost` to your computer's IP address
   - Find IP: Run `ipconfig` (look for IPv4 Address)

4. **Run:**
   ```bash
   cd frontend
   flutter pub get
   flutter run -d <device ID> 
   ```

## 🌐 API Endpoints

- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Admin Panel: `http://localhost:5173`

## 📝 Configuration

### Backend
- Database: SQLite (auto-created)
- Port: 8000 (configurable in `backend/app/config.py`)

### Frontend
- API URL: `frontend/lib/services/api_service.dart`
- Language: Selectable in app (Sinhala/Tamil/English)

## 🤖 AI Models

Depression recognition model location:
- `backend/models/Depression_Recognition/`
- Auto-detected on startup
- Falls back to rule-based detection if model not found

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **API Docs** - Visit `http://localhost:8000/docs` when backend is running

## 👥 Developers

- IT22025494 - Rathnayaka P.S.N
- IT22304810 - Sewwandi M.P.S.S
- IT22349156 - Wijesinghe K.A.A.N
- IT22169808 - Srimali K.H.J

**Group ID:** 25-26J-261  
**Institution:** SLIIT

## 📄 License

This project is for academic/research purposes.
