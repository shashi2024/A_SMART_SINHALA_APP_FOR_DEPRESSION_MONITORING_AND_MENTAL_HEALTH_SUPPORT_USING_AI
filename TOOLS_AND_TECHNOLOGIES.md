# 🛠️ Tools and Technologies Used in the System

This document provides a comprehensive list of all tools, frameworks, libraries, and services used to build the Smart Sinhala App for Depression Monitoring and Mental Health Support.

---

## 📱 **Frontend Technologies**

### Mobile App (Flutter)
- **Flutter SDK** (v3.0+) - Cross-platform mobile framework
- **Dart** (v3.0+) - Programming language
- **Provider** (^6.1.1) - State management
- **HTTP** (^1.1.0) - HTTP client for API calls
- **Record** (^5.0.4) - Audio recording
- **Sensors Plus** (^4.0.2) - Device sensors access
- **Permission Handler** (^11.1.0) - Runtime permissions
- **Path Provider** (^2.1.1) - File system paths
- **Shared Preferences** (^2.2.2) - Local storage

### Firebase (Mobile)
- **Firebase Core** (^3.6.0) - Firebase initialization
- **Firebase Auth** (^5.3.1) - Authentication
- **Cloud Firestore** (^5.4.3) - NoSQL database
- **Firebase Storage** (^12.3.2) - File storage
- **Firebase Messaging** (^15.1.3) - Push notifications

### Platforms Supported
- Android
- iOS
- Web
- Windows
- macOS
- Linux

---

## 🖥️ **Admin Panel Technologies**

### Frontend Framework
- **React** (^18.2.0) - UI library
- **React DOM** (^18.2.0) - React rendering
- **React Router DOM** (^6.20.0) - Routing

### UI Framework
- **Material-UI (MUI)** (^5.14.20) - Component library
- **MUI Icons** (^5.14.19) - Icon set
- **Emotion React** (^11.14.0) - CSS-in-JS
- **Emotion Styled** (^11.14.1) - Styled components

### Build Tools
- **Vite** (^7.2.4) - Build tool and dev server
- **Vite React Plugin** (^5.1.1) - React support for Vite

### Data Visualization
- **Recharts** (^2.10.3) - Chart library

### HTTP Client
- **Axios** (^1.6.2) - HTTP client

---

## ⚙️ **Backend Technologies**

### Web Framework
- **FastAPI** (0.104.1) - Modern Python web framework
- **Uvicorn** (0.24.0) - ASGI server
- **Pydantic** (2.5.0) - Data validation
- **Pydantic Settings** (2.1.0) - Settings management

### Authentication & Security
- **Python-JOSE** (3.3.0) - JWT handling
- **Passlib** (1.7.4) - Password hashing (bcrypt)
- **Python-Multipart** (0.0.6) - File upload support

### Database & Cloud Services
- **Firebase Admin SDK** (6.2.0) - Firebase backend integration
- **Cloud Firestore** - Primary database (via Firebase Admin)

### Google Cloud Services
- **Google Cloud Speech** (2.21.0) - Speech-to-text API
- **Google Cloud Text-to-Speech** (2.14.2) - Text-to-speech API

### HTTP Client
- **Requests** (2.31.0) - HTTP library

---

## 🤖 **AI/ML Technologies**

### Machine Learning Frameworks
- **TensorFlow** (2.15.0) - Deep learning framework
- **PyTorch** (2.1.0) - Deep learning framework
- **Scikit-learn** (1.3.2) - Machine learning library

### Audio Processing
- **Librosa** (0.10.1) - Audio analysis
- **Soundfile** (0.12.1) - Audio I/O

### Data Science
- **NumPy** (1.24.3) - Numerical computing
- **Pandas** (2.1.3) - Data manipulation
- **SciPy** (1.11.4) - Scientific computing

### Model Training Tools
- **Joblib** - Model serialization (via scikit-learn)

### ML Algorithms Used
- **Random Forest Classifier** - Depression detection
- **SVM (Support Vector Machine)** - Voice analysis
- **Gradient Boosting Classifier** - Typing pattern analysis

---

## 💬 **Chatbot Technologies**

### Chatbot Framework
- **Rasa** - Conversational AI framework (optional, runs on port 5005)

---

## 🔧 **Development Tools**

### Version Control
- **Git** - Version control system

### Package Managers
- **npm** / **Node.js** (18+) - JavaScript package management
- **pip** - Python package management
- **pub** (Flutter) - Dart package management

### Build Systems
- **Gradle** (Android) - Build automation
- **CMake** (Linux/Windows) - Build system
- **Xcode** (iOS/macOS) - Apple development tools

### Development Servers
- **Vite Dev Server** - Admin panel development
- **Uvicorn** - Backend API server
- **Flutter Dev Server** - Mobile app hot reload

---

## 🌐 **External Services & APIs**

### Firebase Services
- **Firebase Authentication** - User authentication
- **Cloud Firestore** - Real-time database
- **Firebase Storage** - File storage
- **Firebase Cloud Messaging (FCM)** - Push notifications
- **Firebase Hosting** - Web hosting (optional)

### Google Cloud Platform
- **Google Cloud Speech-to-Text API** - Voice transcription
- **Google Cloud Text-to-Speech API** - Voice synthesis

---

## 📦 **Runtime Requirements**

### Programming Languages
- **Python** (3.9+) - Backend
- **JavaScript/TypeScript** - Admin panel
- **Dart** (3.0+) - Mobile app
- **Kotlin** - Android native code
- **Swift** - iOS native code

### System Requirements
- **Java** (21) - Android development
- **Node.js** (18+) - Admin panel
- **Flutter** (3.0+) - Mobile development

---

## 🗄️ **Data Storage**

### Primary Database
- **Cloud Firestore** (Firebase) - NoSQL document database

### Local Storage
- **Shared Preferences** (Flutter) - Mobile app local storage
- **File System** - Audio recordings, temporary files

---

## 🔐 **Security & Authentication**

### Authentication Methods
- **JWT (JSON Web Tokens)** - Token-based authentication
- **Firebase Authentication** - User authentication
- **Bcrypt** - Password hashing

### Security Libraries
- **Python-JOSE** - JWT encoding/decoding
- **Passlib** - Password hashing

---

## 📊 **Data Analysis & Processing**

### Audio Processing
- **Librosa** - Audio feature extraction (MFCC, pitch, energy)
- **Soundfile** - Audio file I/O
- **NumPy** - Audio signal processing

### Feature Extraction
- **MFCC (Mel-frequency cepstral coefficients)** - Voice features
- **Pitch tracking** - Voice pitch analysis
- **Energy/RMS** - Voice energy analysis
- **Keystroke timing** - Typing pattern analysis

---

## 🚀 **Deployment & Infrastructure**

### Development Environment
- **Windows** - Development OS
- **PowerShell** - Command shell
- **Batch Scripts** (.bat) - Automation scripts

### Server
- **Uvicorn** - ASGI server for production
- **FastAPI** - API framework with auto-documentation

### API Documentation
- **Swagger UI** - Auto-generated API docs (via FastAPI)
- **ReDoc** - Alternative API docs (via FastAPI)

---

## 📝 **Configuration & Environment**

### Configuration Files
- **.env** - Environment variables
- **firebase-credentials.json** - Firebase service account
- **google-services.json** - Android Firebase config
- **firebase_options.dart** - Flutter Firebase config
- **vite.config.js** - Vite build configuration
- **pubspec.yaml** - Flutter dependencies
- **requirements.txt** - Python dependencies
- **package.json** - Node.js dependencies

---

## 🧪 **Testing & Quality**

### Testing Tools
- **Flutter Test** - Unit/widget testing
- **Flutter Lints** (^3.0.0) - Code linting

---

## 📱 **Mobile Development Tools**

### Android
- **Android SDK** - Android development
- **Gradle** - Build system
- **Kotlin** - Native Android code

### iOS
- **Xcode** - iOS development
- **Swift** - Native iOS code
- **CocoaPods** - Dependency management

---

## 🔄 **State Management**

- **Provider** (Flutter) - State management for mobile app
- **React Context** (Admin Panel) - State management for admin panel

---

## 📡 **Communication Protocols**

- **HTTP/HTTPS** - REST API communication
- **WebSocket** (via Firebase) - Real-time updates
- **REST API** - Backend API endpoints

---

## 📚 **Documentation Tools**

- **Markdown** - Documentation format
- **FastAPI Auto-docs** - API documentation
- **Swagger/OpenAPI** - API specification

---

## 🎯 **Summary by Category**

### **Frontend Stack**
- Flutter (Mobile) + React (Admin Panel)

### **Backend Stack**
- FastAPI (Python) + Firebase

### **AI/ML Stack**
- TensorFlow + PyTorch + Scikit-learn

### **Database**
- Cloud Firestore (Firebase)

### **Cloud Services**
- Firebase (Auth, Database, Storage, Messaging)
- Google Cloud (Speech APIs)

### **Development Tools**
- Vite, Uvicorn, Flutter CLI, Git

---

## 📌 **Key Integrations**

1. **Firebase** - Complete backend infrastructure
2. **Google Cloud Speech APIs** - Voice processing
3. **Rasa** - Chatbot framework (optional)
4. **TensorFlow/PyTorch** - ML model inference
5. **FastAPI** - RESTful API server

---

*Last Updated: Based on current project structure and dependencies*
