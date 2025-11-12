# 🧠 A SMART SINHALA APP FOR DEPRESSION MONITORING AND MENTAL HEALTH SUPPORT USING AI

### Group ID: 25-26J-261  
**Specialization:** Information Technology  
**Institution:** SLIIT  
**Developed by:**  
- IT22025494 - Rathnayaka P.S.N 
- IT22304810 - Sewwandi M.P.S.S  
- IT22349156 - Wijesinghe K.A.A.N   
- IT22169808 - Srimali K.H.J  

---

## 📘 Project Overview

This project introduces **an AI-driven Sinhala mobile application** designed to support **depression monitoring and mental health assistance**.  
The system integrates **chat-based and call-based** interactions in Sinhala and detects emotional states using **AI models** and **mobile phone sensors**.

The solution bridges the **gap in culturally relevant mental health support** for Sinhala-speaking communities by providing **real-time, adaptive, and privacy-conscious** assistance.

---

## 🎯 Key Features

### 1. **AI-Driven Sinhala Chatbot**
- Real-time conversational agent (text + voice)
- Emotion detection and fake call detection from call data
- Empathetic and culturally aligned responses

### 2. **Voice Analysis**
- Real-time voice call recording and analysis
- Emotion detection from audio features
- Depression score calculation
- Fake voice detection to prevent synthetic users

### 3. **Typing Behavior Analysis**
- Tracks Sinhala typing speed, pauses, and errors
- Detects stress or emotional imbalance using keystroke dynamics
- Privacy-preserving – does not store typed content
- Fake typing pattern detection

### 4. **Sensor-Based Monitoring**
- Uses **smartphone sensors** (camera, mic, accelerometer, gyroscope)
- Detects stress or depression levels (mild, moderate, severe)
- Adaptive UI that adjusts based on detected emotional state

### 5. **Digital Twin Framework**
- Builds a virtual model of user's mental health profile
- Enables **real-time doctor connection** and **location tracking** during crises
- Provides **personalized, data-driven insights** for long-term wellness

### 6. **Admin Panel**
- Hospital/medical professional dashboard
- User management and monitoring
- Alert system for high-risk cases
- Digital twin visualization
- Real-time analytics

---

## ⚙️ System Architecture

- **Frontend:** Flutter (cross-platform mobile app)  
- **Backend:** FastAPI + RESTful APIs  
- **AI Model Training:** Python, TensorFlow, PyTorch, librosa  
- **Chatbot Engine:** Rasa (Custom Sinhala NLP pipeline)  
- **Database:** SQLite/PostgreSQL  
- **Admin Panel:** React + Material-UI  
- **Additional Tools:** Visual Studio, Android Studio, Ollama, Google Maps API  

---

## 📁 Project Structure

```
├── backend/              # FastAPI backend server
├── frontend/             # Flutter mobile application
├── admin_panel/          # React admin dashboard
├── ai_models/            # ML model training scripts
└── models/               # Trained model files
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Flutter SDK 3.0+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Chatbot
- `POST /api/chatbot/chat` - Send chat message
- `GET /api/chatbot/sessions` - Get chat sessions

### Voice Analysis
- `POST /api/voice/analyze` - Analyze voice audio
- `GET /api/voice/history` - Get voice analysis history

### Typing Analysis
- `POST /api/typing/analyze` - Analyze typing patterns
- `GET /api/typing/history` - Get typing analysis history

### Admin Panel
- `GET /api/admin/dashboard` - Get dashboard data
- `GET /api/admin/alerts` - Get alerts
- `GET /api/admin/users/{user_id}/profile` - Get user profile

### Digital Twin
- `GET /api/digital-twin/profile` - Get digital twin profile
- `POST /api/digital-twin/update` - Update digital twin

---

## 🧪 Technologies Used

| Category | Technologies |
|-----------|--------------|
| **Frontend** | Flutter, Dart |
| **Backend** | FastAPI, Python, SQLAlchemy |
| **AI/ML** | TensorFlow, PyTorch, librosa, scikit-learn |
| **Chatbot** | Rasa (custom Sinhala NLP pipeline) |
| **Admin Panel** | React, Material-UI, Vite |
| **APIs** | Google Speech-to-Text, Text-to-Speech, Maps API |
| **Database** | SQLite/PostgreSQL |
| **Tools** | Visual Studio, Android Studio, Ollama |

---

## 🛡️ Ethical & Privacy Considerations

- Approval from **SLIIT Ethical Review Committee** and **NIMH**.
- No raw audio, video, or typed text is stored — only processed features.
- Data anonymized and securely stored.
- Strict compliance with local and international mental health data handling regulations.
- Fake user detection to prevent system abuse.

---

## 📚 Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed project structure
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- API documentation available at `http://localhost:8000/docs` when backend is running

---

## 🚀 Future Enhancements

- Expand to **multilingual mental health support** (Tamil & English).
- Integrate **wearable device data** for advanced biofeedback.
- Enable **offline chatbot conversations**.
- Introduce **AI-generated therapy content** and mindfulness sessions.
- Advanced fake detection using deep learning models.

---

## 🤝 Acknowledgements

Special thanks to:  
- **NIMH (National Institute of Mental Health)** – for dataset access and expert feedback.  
- **SLIIT Ethical Review Committee** – for research clearance and ethical guidance.  
- **Supervisors & Mentors** – for continuous technical and academic support.

---

## 🧩 License

This project is for **academic and research purposes** under the SLIIT final year research project framework.  
Unauthorized commercial use or redistribution is prohibited.

---

> "Empowering Sinhala-speaking communities with AI-driven mental health care — confidential, compassionate, and culturally relevant."
