# Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- Flutter SDK 3.0+
- PostgreSQL or SQLite (for database)
- Firebase account (optional, for additional features)

## Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Run the server**
   ```bash
   python main.py
   # Or use uvicorn directly
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Frontend Setup (Flutter)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Update API base URL**
   - Edit `lib/services/api_service.dart`
   - Change `baseUrl` to match your backend URL

4. **Run the app**
   ```bash
   flutter run
   ```

## Admin Panel Setup

1. **Navigate to admin panel directory**
   ```bash
   cd admin_panel
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Update API base URL**
   - Edit `src/services/api.js`
   - Change `baseURL` to match your backend URL

4. **Run the development server**
   ```bash
   npm run dev
   ```

The admin panel will be available at `http://localhost:3000`

## AI Models Training

1. **Prepare your dataset**
   - Collect voice samples, typing patterns, and text data
   - Label data with depression indicators

2. **Train depression detection model**
   ```bash
   cd ai_models
   python train_depression_model.py
   ```

3. **Train voice analysis model**
   ```bash
   python train_voice_model.py
   ```

4. **Train typing pattern model**
   ```bash
   python train_typing_model.py
   ```

5. **Copy trained models to backend**
   ```bash
   cp models/*.pkl ../backend/models/
   ```

## Rasa Chatbot Setup (Optional)

1. **Install Rasa**
   ```bash
   pip install rasa
   ```

2. **Create Rasa project**
   ```bash
   rasa init
   ```

3. **Configure Sinhala NLP**
   - Update `config.yml` with Sinhala language support
   - Train custom Sinhala NLU model

4. **Start Rasa server**
   ```bash
   rasa run --enable-api --cors "*"
   ```

5. **Update backend configuration**
   - Set `RASA_SERVER_URL` in `.env`

## Firebase Setup (Optional)

1. **Create Firebase project**
   - Go to Firebase Console
   - Create a new project

2. **Download credentials**
   - Download service account JSON
   - Place in backend directory

3. **Update configuration**
   - Set `FIREBASE_CREDENTIALS` in `.env`

## Testing

### Backend API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'
```

### Frontend
- Run Flutter app on emulator or device
- Test chat, voice, and typing features

### Admin Panel
- Login with admin credentials
- View dashboard and user profiles
- Test alert management

## Troubleshooting

### Backend Issues
- **Database errors**: Ensure database is running and accessible
- **Import errors**: Check virtual environment is activated
- **Port conflicts**: Change PORT in `.env`

### Frontend Issues
- **API connection errors**: Verify backend is running and URL is correct
- **Permission errors**: Check app permissions for sensors and microphone
- **Build errors**: Run `flutter clean` and `flutter pub get`

### Admin Panel Issues
- **CORS errors**: Ensure backend CORS settings allow admin panel origin
- **Authentication errors**: Check token is being sent correctly

## Production Deployment

1. **Backend**
   - Use production WSGI server (Gunicorn)
   - Set up proper database (PostgreSQL)
   - Configure environment variables
   - Enable HTTPS

2. **Frontend**
   - Build release APK/IPA
   - Configure production API URLs
   - Enable code obfuscation

3. **Admin Panel**
   - Build production bundle
   - Deploy to web server
   - Configure reverse proxy

## Security Considerations

- Change default SECRET_KEY
- Use strong passwords
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates
- Data encryption at rest
- Secure API endpoints

