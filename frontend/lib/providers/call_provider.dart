import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../services/api_service.dart';

enum CallType {
  counselor,
  aiPractice,
  emergency,
}

enum CallStatus {
  initiating,
  ringing,
  connected,
  ended,
  rejected,
  missed,
  cancelled,
}

class CallProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  void setToken(String? token) {
    _apiService.setToken(token);
  }
  
  void setLanguage(String langCode) {
    _language = langCode;
    notifyListeners();
  }
  
  String? _currentCallId;
  CallType? _currentCallType;
  CallStatus _callStatus = CallStatus.ended;
  String _language = 'en';
  WebSocketChannel? _webSocketChannel;
  List<Map<String, dynamic>> _callHistory = [];
  List<Map<String, dynamic>> _availableCounselors = [];
  
  // Voice chat state
  String? _lastBotText;
  String? _lastBotAudio;  // Base64 encoded audio
  String? _lastUserText;
  bool _isProcessing = false;
  List<Map<String, String>> _chatMessages = [];  // Chat history for display
  
  // Getters
  String? get currentCallId => _currentCallId;
  CallType? get currentCallType => _currentCallType;
  CallStatus get callStatus => _callStatus;
  String get language => _language;
  List<Map<String, dynamic>> get callHistory => _callHistory;
  List<Map<String, dynamic>> get availableCounselors => _availableCounselors;
  bool get isInCall => _callStatus == CallStatus.connected || 
                       _callStatus == CallStatus.ringing;
  
  // Voice chat getters
  String? get lastBotText => _lastBotText;
  String? get lastBotAudio => _lastBotAudio;
  String? get lastUserText => _lastUserText;
  bool get isProcessing => _isProcessing;
  List<Map<String, String>> get chatMessages => _chatMessages;
  
  // Create a new call
  Future<String> createCall({
    required CallType callType,
    String? calleeId,
    String language = 'en',
  }) async {
    try {
      _language = language;
      _callStatus = CallStatus.initiating;
      notifyListeners();
      
      final callTypeStr = callType == CallType.counselor 
          ? 'counselor' 
          : callType == CallType.aiPractice 
              ? 'ai_practice' 
              : 'emergency';
      
      final response = await _apiService.createCall(
        callType: callTypeStr,
        calleeId: calleeId,
        language: language,
      );
      
      _currentCallId = response['call_id'];
      _currentCallType = callType;
      
      if (callType == CallType.aiPractice) {
        _callStatus = CallStatus.connected;
      } else {
        _callStatus = CallStatus.ringing;
      }
      
      notifyListeners();
      
      // Connect WebSocket for signaling
      if (_currentCallId != null) {
        _connectWebSocket(_currentCallId!);
      }
      
      return _currentCallId!;
    } catch (e) {
      _callStatus = CallStatus.ended;
      notifyListeners();
      rethrow;
    }
  }
  
  // Connect WebSocket for WebRTC signaling
  void _connectWebSocket(String callId) {
    try {
      // Replace with your WebSocket URL
      //final wsUrl = 'ws://localhost:8000/api/calls/ws/$callId';
      final wsUrl = 'ws://192.168.8.111:8000/api/calls/ws/$callId';
      _webSocketChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _webSocketChannel!.stream.listen(
        (message) {
          final data = Map<String, dynamic>.from(
            jsonDecode(message as String)
          );
          _handleWebSocketMessage(data);
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
        },
        onDone: () {
          debugPrint('WebSocket closed');
        },
      );
    } catch (e) {
      debugPrint('Failed to connect WebSocket: $e');
    }
  }
  
  void _handleWebSocketMessage(Map<String, dynamic> message) {
    final type = message['type'];
    
    switch (type) {
      case 'bot_response':
        // Handle bot response (voice chat)
        _isProcessing = false;
        _lastBotText = message['text'];
        _lastBotAudio = message['audio'];
        _lastUserText = message['user_text'];
        
        // Add to chat history
        if (_lastUserText != null && _lastUserText!.isNotEmpty) {
          _chatMessages.add({'role': 'user', 'text': _lastUserText!});
        }
        if (_lastBotText != null && _lastBotText!.isNotEmpty) {
          _chatMessages.add({'role': 'bot', 'text': _lastBotText!});
        }
        
        debugPrint('Bot response: $_lastBotText');
        notifyListeners();
        break;
      case 'error':
        _isProcessing = false;
        debugPrint('Call error: ${message['message']}');
        notifyListeners();
        break;
      case 'offer':
        // Handle WebRTC offer
        notifyListeners();
        break;
      case 'answer':
        // Handle WebRTC answer
        _callStatus = CallStatus.connected;
        notifyListeners();
        break;
      case 'ice_candidate':
        // Handle ICE candidate
        notifyListeners();
        break;
      case 'call_ended':
        _endCall();
        break;
      case 'call_rejected':
        _callStatus = CallStatus.rejected;
        notifyListeners();
        break;
    }
  }
  
  // Send voice message to bot
  void sendVoiceMessage(String audioBase64) {
    if (_webSocketChannel != null && _currentCallId != null) {
      _isProcessing = true;
      notifyListeners();
      
      _webSocketChannel!.sink.add(jsonEncode({
        'type': 'voice_message',
        'audio': audioBase64,
        'call_id': _currentCallId,
      }));
    }
  }
  
  // Send text message to bot (fallback)
  void sendTextMessage(String text) {
    if (_webSocketChannel != null && _currentCallId != null) {
      _isProcessing = true;
      _chatMessages.add({'role': 'user', 'text': text});
      notifyListeners();
      
      _webSocketChannel!.sink.add(jsonEncode({
        'type': 'text_message',
        'text': text,
        'call_id': _currentCallId,
      }));
    }
  }
  
  // Clear chat messages
  void clearChatMessages() {
    _chatMessages.clear();
    _lastBotText = null;
    _lastBotAudio = null;
    _lastUserText = null;
    notifyListeners();
  }
  
  // Send WebRTC offer
  void sendOffer(String offer) {
    if (_webSocketChannel != null && _currentCallId != null) {
      _webSocketChannel!.sink.add(jsonEncode({
        'type': 'offer',
        'call_id': _currentCallId,
        'offer': offer,
      }));
    }
  }
  
  // Send WebRTC answer
  void sendAnswer(String answer) {
    if (_webSocketChannel != null && _currentCallId != null) {
      _webSocketChannel!.sink.add(jsonEncode({
        'type': 'answer',
        'call_id': _currentCallId,
        'answer': answer,
      }));
      _callStatus = CallStatus.connected;
      notifyListeners();
    }
  }
  
  // Send ICE candidate
  void sendIceCandidate(Map<String, dynamic> candidate) {
    if (_webSocketChannel != null && _currentCallId != null) {
      _webSocketChannel!.sink.add(jsonEncode({
        'type': 'ice_candidate',
        'call_id': _currentCallId,
        'candidate': candidate,
      }));
    }
  }
  
  // End call
  Future<void> endCall() async {
    if (_currentCallId != null) {
      try {
        await _apiService.endCall(_currentCallId!);
      } catch (e) {
        debugPrint('Error ending call: $e');
      }
    }
    _endCall();
  }
  
  void _endCall() {
    _webSocketChannel?.sink.close();
    _webSocketChannel = null;
    _currentCallId = null;
    _currentCallType = null;
    _callStatus = CallStatus.ended;
    notifyListeners();
    loadCallHistory(); // Refresh history
  }
  
  // Reject call
  Future<void> rejectCall(String callId) async {
    try {
      await _apiService.rejectCall(callId);
      _callStatus = CallStatus.rejected;
      notifyListeners();
    } catch (e) {
      debugPrint('Error rejecting call: $e');
    }
  }
  
  // Load call history
  Future<void> loadCallHistory({String? callType}) async {
    try {
      _callHistory = List<Map<String, dynamic>>.from(
        await _apiService.getCallHistory(callType: callType)
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading call history: $e');
    }
  }
  
  // Load available counselors
  Future<void> loadAvailableCounselors({String language = 'en'}) async {
    try {
      _availableCounselors = List<Map<String, dynamic>>.from(
        await _apiService.getAvailableCounselors(language: language)
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading counselors: $e');
    }
  }
  
  @override
  void dispose() {
    _webSocketChannel?.sink.close();
    super.dispose();
  }
}

