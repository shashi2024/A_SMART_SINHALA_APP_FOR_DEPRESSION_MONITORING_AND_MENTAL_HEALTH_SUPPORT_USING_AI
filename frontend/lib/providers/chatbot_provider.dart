import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final double? depressionScore;
  final String? riskLevel;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.depressionScore,
    this.riskLevel,
    required this.timestamp,
  });
}

class ChatbotProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final List<ChatMessage> _messages = [];
  int? _currentSessionId;

  List<ChatMessage> get messages => _messages;
  int? get currentSessionId => _currentSessionId;

  Future<void> sendMessage(
    String message, {
    Map<String, dynamic>? typingData,
    Map<String, dynamic>? sensorData,
  }) async {
    // Add user message
    _messages.add(ChatMessage(
      text: message,
      isUser: true,
      timestamp: DateTime.now(),
    ));
    notifyListeners();

    try {
      // Send to API
      final response = await _apiService.sendChatMessage(
        message,
        sessionId: _currentSessionId,
        typingData: typingData,
        sensorData: sensorData,
      );

      // Update session ID
      _currentSessionId = response['session_id'];

      // Add bot response
      _messages.add(ChatMessage(
        text: response['response'],
        isUser: false,
        depressionScore: response['depression_score']?.toDouble(),
        riskLevel: response['risk_level'],
        timestamp: DateTime.now(),
      ));
      notifyListeners();
    } catch (e) {
      // Add error message
      _messages.add(ChatMessage(
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: DateTime.now(),
      ));
      notifyListeners();
    }
  }

  void clearMessages() {
    _messages.clear();
    _currentSessionId = null;
    notifyListeners();
  }
}

