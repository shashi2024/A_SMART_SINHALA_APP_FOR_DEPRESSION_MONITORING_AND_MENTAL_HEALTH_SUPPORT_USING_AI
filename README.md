# 🧠 Smart Sinhala App for Depression Monitoring and Mental Health Support

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B.svg?logo=flutter)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-6.2.0-FFCA28.svg?logo=firebase)](https://firebase.google.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?logo=react)](https://reactjs.org/)

An AI-powered mental health support application with multi-language support (Sinhala, Tamil, English) that monitors depression through voice analysis, typing patterns, and chatbot interactions.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## ✨ Features

### Core Features
- **🎤 Voice Call Analysis** - Real-time depression detection from voice with call bot detection
- **💬 AI Chatbot** - Conversational support in Sinhala, Tamil, and English
- **⌨️ Typing Pattern Analysis** - Keystroke dynamics for mental health assessment
- **📱 Biofeedback System** - Depression detection using mobile sensor data (accelerometer, gyroscope, etc.)
- **📱 Social Media Analysis** - Depression detection through social media sentiment and behavior analysis
- **🌐 Multi-language Support** - Sinhala (සිංහල), Tamil (தமிழ்), and English
- **📊 Admin Dashboard** - Comprehensive monitoring and alert system
- **🔐 Secure Authentication** - JWT-based authentication with Firebase
- **📱 Cross-platform Mobile App** - Android, iOS, Web, Windows, macOS, Linux

### AI/ML Capabilities
- **Voice-based Detection** - Depression detection using Random Forest Classifier and voice emotion analysis with SVM
- **Typing Pattern Analysis** - Keystroke dynamics analysis with Gradient Boosting Classifier
- **Biofeedback Analysis** - Physiological data analysis from mobile sensors for depression indicators
- **Social Media Sentiment Analysis** - Text mining and sentiment analysis from social media posts for depression detection
- **PHQ-9 Integration** - Standardized questionnaire for depression screening
- **Safety Guardrails** - Crisis detection and escalation mechanisms

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Firebase/Firestore** - NoSQL database and authentication
- **TensorFlow & PyTorch** - Deep learning frameworks
- **Scikit-learn** - Machine learning algorithms
- **Google Cloud Speech APIs** - Voice processing

### Frontend (Mobile)
- **Flutter** - Cross-platform mobile framework
- **Provider** - State management
- **Firebase SDK** - Authentication and database

### Admin Panel
- **React** - UI library
- **Material-UI (MUI)** - Component library
- **Vite** - Build tool
- **Recharts** - Data visualization

For a complete list of technologies, see [TOOLS_AND_TECHNOLOGIES.md](TOOLS_AND_TECHNOLOGIES.md).

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.9 or higher
- **Node.js** 18 or higher
- **Flutter** 3.0 or higher
- **Java** 21 (for Android development)
- **Git** for version control
- **Firebase Account** (free tier is sufficient)

### Platform-Specific Requirements

#### Windows
- PowerShell 5.1+
- Android Studio (for Android development)
- Visual Studio (for Windows app development)

#### macOS
- Xcode (for iOS development)
- CocoaPods

#### Linux
- CMake
- GCC/G++

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-sinhala-depression-app.git
cd smart-sinhala-depression-app
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Create virtual environment (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable **Firestore Database** (start in test mode)
4. Go to **Project Settings** → **Service Accounts**
5. Click **"Generate new private key"** and download the JSON file
6. Rename the file to `firebase-credentials.json`
7. Place it in the `backend/` directory

### 4. Environment Configuration

```bash
# Copy environment template
cd backend
copy env.template .env  # Windows
# or
cp env.template .env    # Linux/Mac
```

Edit `.env` and ensure `FIREBASE_CREDENTIALS=./firebase-credentials.json` is set.

### 5. Frontend Setup (Flutter)

```bash
# Navigate to frontend directory
cd frontend

# Install Flutter dependencies
flutter pub get

# Generate Firebase configuration (if needed)
flutter pub run flutterfire_cli:configure
```

### 6. Admin Panel Setup

```bash
# Navigate to admin panel directory
cd admin_panel

# Install Node.js dependencies
npm install
```

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Firebase (Required)
FIREBASE_CREDENTIALS=./firebase-credentials.json

# JWT Settings
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=*

# Google APIs (Optional)
GOOGLE_SPEECH_API_KEY=your-api-key-here
```

### Frontend Configuration

Update API URL in `frontend/lib/services/api_service.dart`:

```dart
// For local development
static const String baseUrl = 'http://localhost:8000';

// For mobile device testing (replace with your computer's IP)
static const String baseUrl = 'http://192.168.1.100:8000';
```


### Firebase Mobile Configuration

1. In Firebase Console, go to **Project Settings** → **General**
2. Add your Android/iOS app
3. Download `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
4. Place in appropriate directories:
   - Android: `frontend/android/app/google-services.json`
   - iOS: `frontend/ios/Runner/GoogleService-Info.plist`

---

## 🏃 Running the Application

### Quick Start (Windows)

Use the provided batch scripts:

```bash
# Terminal 1: Start Backend
run_backend.bat

# Terminal 2: Start Frontend (connect phone first)
run_frontend_phone.bat

# Terminal 3: Start Admin Panel (optional)
run_admin_panel.bat
```

### Manual Start

#### Backend Server

```bash
cd backend
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

python main.py
```

Backend will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### Flutter Mobile App

```bash
cd frontend

# List available devices
flutter devices

# Run on connected device
flutter run

# Run on specific device
flutter run -d <device-id>

# Run on Chrome (for web testing)
flutter run -d chrome
```

#### Admin Panel

```bash
cd admin_panel
npm run dev
```

Admin panel will be available at: `http://localhost:5173`

### Running on Physical Device

1. **Enable USB Debugging** (Android):
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Connect device via USB**

3. **Update API URL** in `frontend/lib/services/api_service.dart` to your computer's IP address

4. **Run the app**:
   ```bash
   cd frontend
   flutter run
   ```

---

## 📁 Project Structure

```
smart-sinhala-depression-app/
├── backend/                 # FastAPI backend server
│   ├── app/
│   │   ├── routes/         # API route handlers
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── chatbot.py  # Chatbot endpoints
│   │   │   ├── voice.py    # Voice analysis endpoints
│   │   │   ├── typing.py   # Typing analysis endpoints
│   │   │   ├── digital_twin.py  # Digital twin endpoints
│   │   │   └── admin.py    # Admin panel endpoints
│   │   ├── services/       # Business logic services
│   │   └── config.py       # Configuration settings
│   ├── models/             # ML model files
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
├── frontend/               # Flutter mobile application
│   ├── lib/
│   │   ├── screens/        # UI screens
│   │   ├── services/       # API services
│   │   └── providers/      # State management
│   ├── android/            # Android-specific code
│   ├── ios/                # iOS-specific code
│   └── pubspec.yaml        # Flutter dependencies
│
├── admin_panel/            # React admin dashboard
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   └── services/       # API services
│   └── package.json        # Node.js dependencies
│
└── ai_models/              # ML model training scripts
    ├── train_depression_model.py
    ├── train_voice_model.py
    └── train_typing_model.py
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "phone_number": "string" (optional)
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Chatbot Endpoints

#### Send Chat Message
```http
POST /api/chatbot/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "string"
}
```

#### Start PHQ-9 Questionnaire
```http
POST /api/chatbot/phq9/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "language": "en" | "si" | "ta"
}
```

### Voice Analysis Endpoints

#### Analyze Voice Recording
```http
POST /api/voice/analyze
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio_file>
language: "en" | "si" | "ta"
```

### Typing Analysis Endpoints

#### Analyze Typing Pattern
```http
POST /api/typing/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "keystroke_times": [0.1, 0.2, 0.3, ...],
  "session_id": "string" (optional)
}
```

### Digital Twin Endpoints

#### Get User Profile
```http
GET /api/digital-twin/profile
Authorization: Bearer <token>
```

### Admin Endpoints

#### Get All Alerts
```http
GET /api/admin/alerts
Authorization: Bearer <admin_token>
```

#### Get User Dashboard
```http
GET /api/admin/dashboard
Authorization: Bearer <admin_token>
```

### Interactive API Documentation

When the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔧 Development

### Testing Backend Connection

```bash
cd backend
python test_firestore_connection.py
```

### Creating Test Users

```bash
# Create regular user
cd backend
python create_test_user.py

# Create admin user
python create_admin.py
```

### Running Tests

```bash
# Backend tests
cd backend
python test_chatbot.py

# Flutter tests
cd frontend
flutter test
```

### Code Quality

```bash
# Flutter linting
cd frontend
flutter analyze

# Python formatting (if configured)
cd backend
black .
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Follow Flutter style guide for Dart code
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for new features

---

## 👥 Team

**Group ID:** 25-26J-261  
**Institution:** SLIIT (Sri Lanka Institute of Information Technology)

---

### Team Members & Contributions

#### 👨‍💻 **IT22025494 - Rathnayaka P.S.N**

**Role:** Biofeedback System Developer & UI/UX Designer

**Key Contributions:**
- **Biofeedback System Development**
  - Sensor data integration and processing
  - Real-time sensor data collection from mobile devices
  - Biofeedback analysis algorithms
  - Physiological data monitoring (heart rate, movement, etc.)
  - Sensor-based depression indicators

- **UI/UX Design**
  - Mobile app interface design
  - User experience optimization
  - Visual design and styling
  - Responsive layout design
  - Accessibility features

- **Sensor Integration**
  - Mobile sensor API integration (accelerometer, gyroscope, etc.)
  - Data preprocessing and feature extraction
  - Real-time data visualization
  - Sensor data storage and analysis

**Technologies:** Flutter, Dart, Sensors Plus, UI/UX Design Tools, Data Visualization

---

#### 👩‍💻 **IT22304810 - Sewwandi M.P.S.S**

**Role:** Full-Stack Developer & AI/ML Engineer

**Key Contributions:**
- **AI Chatbot Development**
  - Multi-language chatbot implementation (Sinhala, Tamil, English)
  - Intent detection and pattern matching
  - Conversational flow design
  - PHQ-9 questionnaire integration
  - Safety guardrails and crisis detection
  - Chatbot service architecture and backend

- **Voice-Based Depression Detection**
  - Voice analysis service with emotion recognition
  - Audio processing and feature extraction
  - Depression detection from voice patterns
  - Integration with Google Cloud Speech APIs
  - Voice emotion analysis models

- **Fake Call Detector**
  - Call bot detection algorithms
  - Fake call identification system
  - Audio authenticity verification
  - Pattern recognition for synthetic calls
  - Integration with voice analysis pipeline

- **Mobile App Development**
  - Cross-platform Flutter application
  - Screen development (Login, Signup, Home, Profile, Chat, Voice Call)
  - State management with Provider pattern
  - Firebase mobile SDK integration
  - API service layer implementation

**Technologies:** Python, FastAPI, Flutter, Dart, TensorFlow, Librosa, NLP, Pattern Matching, Firebase

---

#### 👨‍💻 **IT22349156 - Wijesinghe K.A.A.N**

**Role:** ML Engineer & Typing Analysis Specialist

**Key Contributions:**
- **Typing-Based Depression Detection Model**
  - Keystroke dynamics analysis
  - Typing pattern feature extraction
  - Machine learning model development for typing analysis
  - Model training and optimization
  - Typing behavior classification algorithms

- **ML Model Development**
  - Gradient Boosting Classifier implementation
  - Feature engineering for typing patterns
  - Model training scripts and pipelines
  - Typing analysis service development
  - Model evaluation and validation

- **Typing Analysis System**
  - Keystroke timing analysis
  - Typing speed and consistency metrics
  - Error rate and pause duration analysis
  - Depression score calculation from typing patterns
  - Integration with backend API

**Technologies:** Python, Scikit-learn, NumPy, Pandas, Machine Learning, FastAPI

---

#### 👩‍💻 **IT22169808 - Srimali K.H.J**

**Role:** Social Media Analysis Developer & Admin Panel Designer

**Key Contributions:**
- **Social Media-Based Depression Detection**
  - Social media data analysis algorithms
  - Text mining and sentiment analysis from social posts
  - Depression indicators extraction from social media content
  - Pattern recognition in social media behavior
  - Integration with depression detection pipeline

- **Admin Panel Design & Development**
  - Complete React admin dashboard design
  - Material-UI component integration and customization
  - Responsive dashboard layout and UX design
  - Visual design system implementation
  - User interface optimization

- **Admin Panel Features**
  - User management and monitoring interface
  - Alert system and notifications UI
  - Patient risk level visualization
  - Digital Twin profile viewer design
  - Real-time data updates and dashboards

- **Data Visualization & Analytics**
  - Charts and graphs using Recharts
  - Risk level dashboards design
  - User analytics and insights visualization
  - Trend analysis and reporting interfaces

- **Frontend Integration**
  - API integration with backend
  - State management with React Context
  - Routing with React Router
  - Error handling and loading states

**Technologies:** React, Material-UI, Recharts, Axios, Vite, JavaScript, NLP, Text Mining, Sentiment Analysis

---

### 🎯 Project Areas & Responsibilities

#### **Chatbot & Voice Analysis** (IT22304810 - Sewwandi M.P.S.S)
- AI chatbot development with multi-language support
- Voice-based depression detection
- Fake call detection system
- PHQ-9 questionnaire integration
- Safety guardrails and crisis detection
- Mobile app development and integration

#### **Typing Analysis & ML Models** (IT22349156 - Wijesinghe K.A.A.N)
- Typing-based depression detection model
- Keystroke dynamics analysis
- ML model training and optimization
- Feature engineering for typing patterns
- Model integration with backend

#### **Biofeedback & UI Design** (IT22025494 - Rathnayaka P.S.N)
- Biofeedback system using sensor data
- Mobile sensor integration
- UI/UX design for mobile application
- Visual design and styling
- Real-time sensor data processing

#### **Social Media Analysis & Admin Panel** (IT22169808 - Srimali K.H.J)
- Social media-based depression detection
- Text mining and sentiment analysis
- Admin panel design and development
- Data visualization and dashboards
- User management interface

#### **Backend & Infrastructure** (IT22304810, IT22349156)
- FastAPI server setup and configuration
- API endpoint development
- Database design and Firestore integration
- Authentication and authorization
- Service integration

#### **Testing & Documentation** (All Members)
- API testing and validation
- Mobile app testing
- Documentation writing
- Setup guides and tutorials
- Code review and quality assurance

---

### 📊 Project Statistics

- **Total Lines of Code:** ~15,000+
- **Backend Services:** 11 major services
- **API Endpoints:** 20+ endpoints
- **Mobile Screens:** 6 main screens
- **Admin Pages:** 6 pages
- **AI/ML Models:** 
  - Voice-based depression detection model
  - Typing pattern analysis model
  - Social media sentiment analysis model
- **Detection Methods:** 4 (Voice, Typing, Social Media, Biofeedback)
- **Languages Supported:** 3 (Sinhala, Tamil, English)

---

### 🤝 Collaboration

The team worked collaboratively using:
- **Version Control:** Git/GitHub
- **Communication:** Regular team meetings and code reviews
- **Project Management:** Agile methodology
- **Code Standards:** PEP 8 (Python), Flutter style guide, ESLint (JavaScript)
- **Documentation:** Comprehensive documentation for all modules

---

### 🏆 Achievements

- ✅ Successfully implemented multi-language support (Sinhala, Tamil, English)
- ✅ Developed 4 different depression detection methods:
  - Voice-based depression detection
  - Typing pattern analysis
  - Social media sentiment analysis
  - Biofeedback using sensor data
- ✅ Built cross-platform mobile application (Android, iOS, Web)
- ✅ Developed comprehensive admin dashboard with data visualization
- ✅ Implemented AI chatbot with safety guardrails and crisis detection
- ✅ Created fake call detection system
- ✅ Integrated PHQ-9 questionnaire in multiple languages
- ✅ Implemented real-time monitoring and alerting system
- ✅ Created secure authentication system with Firebase
- ✅ Migrated from SQLite to Firebase/Firestore

---

## 📄 License

This project is for academic and research purposes.

---

## 📖 Additional Documentation

- [Quick Start Guide](QUICK_START.md)
- [Complete Setup Guide](backend/COMPLETE_SETUP_GUIDE.md)
- [Tools and Technologies](TOOLS_AND_TECHNOLOGIES.md)
- [Backend Start Here](backend/START_HERE.md)
- [Chatbot Architecture](backend/CHATBOT_ARCHITECTURE.md)
- [Firebase Setup Guide](backend/FIREBASE_SETUP_GUIDE.md)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Firebase not initialized
- **Solution:** Check that `firebase-credentials.json` exists in `backend/` directory
- Verify `.env` has correct path: `FIREBASE_CREDENTIALS=./firebase-credentials.json`

**Problem:** Module not found
- **Solution:** Activate virtual environment and run `pip install -r requirements.txt`

**Problem:** Permission denied (Firestore)
- **Solution:** Ensure Firestore is in test mode or update security rules in Firebase Console

### Frontend Issues

**Problem:** Cannot connect to backend
- **Solution:** Update API URL in `api_service.dart` to your computer's IP address (not localhost)

**Problem:** Firebase not configured
- **Solution:** Run `flutterfire configure` or manually add Firebase config files

**Problem:** Build errors
- **Solution:** Run `flutter clean` and `flutter pub get`

### Admin Panel Issues

**Problem:** Cannot connect to backend
- **Solution:** Check that backend is running on `http://localhost:8000`
- Verify CORS settings in backend `.env`

---

## 🎯 Next Steps

1. Set up Firebase project and download credentials
2. Configure environment variables
3. Install all dependencies
4. Test backend connection
5. Run the application
6. Explore API documentation at `/docs`

For detailed setup instructions, see [backend/START_HERE.md](backend/START_HERE.md).

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the documentation files

---

**Made with ❤️ for mental health support**
