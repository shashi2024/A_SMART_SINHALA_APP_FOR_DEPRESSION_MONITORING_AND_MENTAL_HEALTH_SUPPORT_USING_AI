# 📞 Calling Feature - Duolingo-Style Integration

This document describes the calling facility integrated into the app, similar to Duolingo's voice calling feature.

## 🎯 Features

### 1. **AI Practice Calls**
- Practice speaking with an AI assistant
- Real-time voice conversation
- Supports Sinhala, Tamil, and English
- Similar to Duolingo's speaking practice exercises

### 2. **Counselor Calls**
- Connect with professional counselors
- Voice/video calling support
- Counselor availability management
- Language-based counselor matching

### 3. **Emergency Calls**
- Immediate support in crisis situations
- Quick access to help
- Priority routing for emergency calls

## 🏗️ Architecture

### Backend Components

#### 1. Call Service (`backend/app/services/call_service.py`)
- Manages call lifecycle (create, update, end)
- Handles call status transitions
- WebRTC signaling support
- Firestore integration for call history

#### 2. Call Routes (`backend/app/routes/calls.py`)
- REST API endpoints for call management
- WebSocket endpoint for real-time signaling
- Call history retrieval
- Counselor availability queries

#### 3. Firestore Service Updates
- Added call collection operations
- Call history queries
- Counselor management

### Frontend Components

#### 1. Call Provider (`frontend/lib/providers/call_provider.dart`)
- State management for calls
- WebSocket connection handling
- WebRTC signaling coordination
- Call history management

#### 2. Call Screen (`frontend/lib/screens/call_screen.dart`)
- Real-time call interface
- WebRTC video/audio rendering
- Call controls (mute, speaker, end)
- Connection status display

#### 3. Calls Home Screen (`frontend/lib/screens/calls_home_screen.dart`)
- Call initiation interface
- Call history view
- Counselor selection
- Emergency call access

## 📦 Dependencies

### Backend
- FastAPI (already included)
- WebSocket support (FastAPI native)
- Firestore (already configured)

### Frontend
- `flutter_webrtc: ^0.9.48` - WebRTC implementation
- `web_socket_channel: ^2.4.0` - WebSocket client

## 🚀 Setup Instructions

### 1. Install Frontend Dependencies

```bash
cd frontend
flutter pub get
```

### 2. Backend Configuration

The calling routes are automatically included in `main.py`. No additional configuration needed.

### 3. WebRTC Configuration

For production, you'll need to configure STUN/TURN servers:

```python
# In backend/app/routes/calls.py or call_service.py
'iceServers': [
    {'urls': 'stun:stun.l.google.com:19302'},  # Free STUN
    # Add TURN servers for production (e.g., Twilio, Agora)
]
```

## 📱 Usage

### Starting an AI Practice Call

```dart
final callProvider = Provider.of<CallProvider>(context, listen: false);
final callId = await callProvider.createCall(
  callType: CallType.aiPractice,
  language: 'en',
);

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => CallScreen(
      callId: callId,
      callType: 'ai_practice',
    ),
  ),
);
```

### Starting a Counselor Call

```dart
final callId = await callProvider.createCall(
  callType: CallType.counselor,
  calleeId: counselorId,
  language: 'sinhala',
);
```

### Ending a Call

```dart
await callProvider.endCall();
```

## 🔌 API Endpoints

### REST Endpoints

- `POST /api/calls/create` - Create a new call
- `GET /api/calls/{call_id}` - Get call details
- `POST /api/calls/{call_id}/end` - End a call
- `POST /api/calls/{call_id}/reject` - Reject an incoming call
- `GET /api/calls/history` - Get call history
- `GET /api/calls/counselors/available` - Get available counselors

### WebSocket Endpoint

- `WS /api/calls/ws/{call_id}` - WebRTC signaling

## 🔐 Security Considerations

1. **Authentication**: All endpoints require JWT authentication
2. **Authorization**: Users can only access their own calls
3. **WebSocket**: WebSocket connections are authenticated via query params or headers
4. **Call Privacy**: Call data is stored securely in Firestore

## 🎨 UI/UX Features

1. **Call Status Indicators**
   - Ringing, Connected, Ended states
   - Visual feedback for call status

2. **Call Controls**
   - Mute/unmute microphone
   - Speaker toggle
   - End call button

3. **Call History**
   - List of past calls
   - Call duration and status
   - Date/time information

4. **Language Support**
   - Multi-language call interface
   - Language-specific counselor matching

## 🔄 Integration with Existing Features

### Chatbot Integration
- AI practice calls use the same chatbot service
- Voice-to-text conversion for chatbot responses
- Real-time conversation flow

### Voice Analysis
- Calls can trigger voice analysis
- Depression detection during calls
- Risk level assessment

### Admin Dashboard
- Call statistics and monitoring
- Counselor availability management
- Call quality metrics

## 🚧 Future Enhancements

1. **Video Calling**
   - Enable video for counselor calls
   - Screen sharing for therapy sessions

2. **Call Recording**
   - Optional call recording (with consent)
   - Playback for review

3. **Group Calls**
   - Support group therapy sessions
   - Multiple participants

4. **Call Scheduling**
   - Schedule calls with counselors
   - Calendar integration

5. **Push Notifications**
   - Incoming call notifications
   - Call reminders

## 📝 Notes

- WebRTC requires HTTPS in production (except localhost)
- STUN/TURN servers are needed for NAT traversal
- Consider using services like Twilio, Agora, or Daily.co for production
- Test on real devices for best WebRTC performance

## 🐛 Troubleshooting

### WebRTC Connection Issues
- Check STUN/TURN server configuration
- Verify network connectivity
- Check firewall settings

### WebSocket Connection Failures
- Verify WebSocket URL format
- Check CORS settings
- Ensure authentication token is valid

### Audio/Video Not Working
- Check device permissions
- Verify microphone/camera access
- Test on different devices

## 📚 References

- [WebRTC Documentation](https://webrtc.org/)
- [Flutter WebRTC Package](https://pub.dev/packages/flutter_webrtc)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)






