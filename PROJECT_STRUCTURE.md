# Project Structure

## Overview
This is a comprehensive depression monitoring system with chatbot, voice analysis, typing pattern analysis, fake detection, and admin panel with digital twin integration.

## Directory Structure

```
A_SMART_SINHALA_APP_FOR_DEPRESSION_MONITORING_AND_MENTAL_HEALTH_SUPPORT_USING_AI/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                      # Main application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                 # Environment variables template
│   │
│   └── app/
│       ├── config.py                 # Configuration settings
│       ├── database.py               # Database models and setup
│       │
│       ├── routes/                   # API routes
│       │   ├── auth.py              # Authentication endpoints
│       │   ├── chatbot.py           # Chatbot endpoints
│       │   ├── voice.py             # Voice analysis endpoints
│       │   ├── typing.py            # Typing analysis endpoints
│       │   ├── admin.py             # Admin panel endpoints
│       │   └── digital_twin.py      # Digital twin endpoints
│       │
│       └── services/                 # Business logic services
│           ├── chatbot_service.py   # Chatbot interaction service
│           ├── voice_analysis.py    # Voice feature extraction & analysis
│           ├── typing_analysis.py   # Typing pattern analysis
│           ├── fake_detection.py    # Fake user detection (voice & typing)
│           ├── depression_detection.py  # Depression detection service
│           └── digital_twin_service.py  # Digital twin management
│
├── frontend/                         # Flutter Mobile App
│   ├── lib/
│   │   ├── main.dart                # App entry point
│   │   │
│   │   ├── screens/                 # UI screens
│   │   │   ├── home_screen.dart    # Home dashboard
│   │   │   ├── chat_screen.dart    # Chat interface
│   │   │   ├── voice_call_screen.dart  # Voice call interface
│   │   │   └── profile_screen.dart # User profile & digital twin
│   │   │
│   │   ├── providers/              # State management
│   │   │   ├── auth_provider.dart  # Authentication state
│   │   │   ├── chatbot_provider.dart  # Chatbot state
│   │   │   ├── voice_provider.dart # Voice analysis state
│   │   │   ├── sensor_provider.dart  # Sensor data state
│   │   │   └── digital_twin_provider.dart  # Digital twin state
│   │   │
│   │   └── services/               # API & device services
│   │       ├── api_service.dart    # Backend API client
│   │       ├── sensor_service.dart # Sensor data collection
│   │       ├── audio_recorder.dart # Audio recording
│   │       └── typing_analyzer.dart # Typing pattern tracking
│   │
│   └── pubspec.yaml                # Flutter dependencies
│
├── admin_panel/                      # React Admin Panel
│   ├── src/
│   │   ├── App.jsx                 # Main app component
│   │   │
│   │   ├── pages/                  # Admin pages
│   │   │   ├── Login.jsx          # Admin login
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── UserProfile.jsx    # User detail view
│   │   │   ├── Alerts.jsx         # Alert management
│   │   │   └── DigitalTwinView.jsx # Digital twin visualization
│   │   │
│   │   ├── components/            # Reusable components
│   │   │   ├── Layout.jsx        # Main layout
│   │   │   └── PrivateRoute.jsx  # Protected routes
│   │   │
│   │   ├── services/              # API services
│   │   │   └── api.js            # Backend API client
│   │   │
│   │   └── contexts/             # React contexts
│   │       └── AuthContext.jsx  # Authentication context
│   │
│   └── package.json              # Node.js dependencies
│
├── ai_models/                       # AI/ML Model Training
│   ├── train_depression_model.py   # Depression detection model
│   ├── train_voice_model.py        # Voice analysis model
│   └── train_typing_model.py       # Typing pattern model
│
├── models/                          # Trained model files (generated)
│   ├── depression_model.pkl
│   ├── voice_model.pkl
│   └── typing_model.pkl
│
├── README.md                         # Project documentation
└── PROJECT_STRUCTURE.md            # This file
```

## Key Features

### Backend (FastAPI)
- **Authentication**: JWT-based user authentication
- **Chatbot API**: Text-based conversation endpoints
- **Voice Analysis**: Audio processing and depression detection
- **Typing Analysis**: Keystroke dynamics analysis
- **Fake Detection**: Detects synthetic/fake users
- **Admin Panel**: Hospital management endpoints
- **Digital Twin**: Mental health profile management

### Frontend (Flutter)
- **Chat Interface**: Real-time chatbot interaction
- **Voice Call**: Audio recording and analysis
- **Typing Tracking**: Real-time keystroke analysis
- **Sensor Integration**: Accelerometer, gyroscope, etc.
- **Profile View**: Digital twin visualization

### Admin Panel (React)
- **Dashboard**: Overview of all users
- **User Management**: Detailed user profiles
- **Alert System**: Risk alerts and notifications
- **Digital Twin View**: Visualize user mental health profiles

### AI Models
- **Depression Detection**: Multi-modal analysis
- **Voice Analysis**: Emotion and depression from audio
- **Typing Patterns**: Behavioral analysis from keystrokes

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python main.py
```

### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run
```

### Admin Panel Setup
```bash
cd admin_panel
npm install
npm run dev
```

## Next Steps

1. **Configure Environment Variables**: Set up API keys, database URLs, etc.
2. **Train AI Models**: Use training scripts with your dataset
3. **Set up Rasa Chatbot**: Configure Sinhala NLP pipeline
4. **Configure Firebase**: Set up Firebase for additional features
5. **Deploy**: Deploy backend, frontend, and admin panel

