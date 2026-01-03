import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
  final ApiService _apiService;
  final List<ChatMessage> _messages = [];
  String? _currentSessionId;
  String _selectedLanguage = 'en'; // 'en', 'si', 'ta'

  ChatbotProvider({ApiService? apiService}) 
      : _apiService = apiService ?? ApiService() {
    _loadLanguagePreference();
  }

  List<ChatMessage> get messages => _messages;
  String? get currentSessionId => _currentSessionId;
  String get selectedLanguage => _selectedLanguage;
  
  // Method to update token from AuthProvider
  void setToken(String? token) {
    _apiService.setToken(token);
  }

  Future<void> _loadLanguagePreference() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedLanguage = prefs.getString('chatbot_language');
      if (savedLanguage != null) {
        _selectedLanguage = savedLanguage;
        notifyListeners();
      }
    } catch (e) {
      // Use default language
    }
  }

  Future<void> setLanguage(String language) async {
    _selectedLanguage = language;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('chatbot_language', language);
    } catch (e) {
      // Ignore storage errors
    }
  }

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
        language: _selectedLanguage,
        typingData: typingData,
        sensorData: sensorData,
      );

      // Update session ID (convert to string if needed)
      _currentSessionId = response['session_id']?.toString();

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
      // Add error message with details for debugging
      String errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      // Log error for debugging
      debugPrint('Chatbot error: $e');
      
      // Check if it's an authentication error
      if (e.toString().contains('401') || e.toString().contains('Unauthorized')) {
        errorMessage = 'Please log in to use the chatbot.';
      } else if (e.toString().contains('Failed to send message')) {
        errorMessage = 'Failed to connect to server. Please check your connection.';
      }
      
      _messages.add(ChatMessage(
        text: errorMessage,
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

