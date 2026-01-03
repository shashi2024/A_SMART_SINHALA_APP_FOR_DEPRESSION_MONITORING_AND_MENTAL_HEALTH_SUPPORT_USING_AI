import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:io';

class ApiService {
  // API Base URL Configuration
  // For Android Emulator: Use 'http://10.0.2.2:8000/api' (10.0.2.2 maps to host's localhost)
  // For Physical Device: Use 'http://YOUR_COMPUTER_IP:8000/api' (e.g., 'http://192.168.1.100:8000/api')
  // For Web/Windows: Use 'http://localhost:8000/api'
  // 
  // To find your computer's IP address:
  //   Windows: Run 'ipconfig' and look for IPv4 Address
  //   Linux/Mac: Run 'ifconfig' or 'ip addr show'
  
  // For Web/Chrome - use localhost
  static const String baseUrl = 'http://localhost:8000/api';
  
  // Uncomment and set your IP address for physical device or if localhost doesn't work:
  // static const String baseUrl = 'http://192.168.122.173:8000/api';
  
  String? _token;

  void setToken(String? token) {
    _token = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: _headers,
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorBody = response.body;
        debugPrint('Login API Error: ${response.statusCode} - $errorBody');
        try {
          final errorJson = jsonDecode(errorBody);
          throw Exception(errorJson['detail'] ?? 'Login failed: ${response.statusCode}');
        } catch (_) {
          throw Exception('Login failed: ${response.statusCode} - $errorBody');
        }
      }
    } catch (e) {
      if (e.toString().contains('Exception')) {
        rethrow;
      }
      debugPrint('Login network error: $e');
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: _headers,
        body: jsonEncode({
          'username': username,
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorBody = response.body;
        debugPrint('Register API Error: ${response.statusCode} - $errorBody');
        try {
          final errorJson = jsonDecode(errorBody);
          throw Exception(errorJson['detail'] ?? 'Registration failed: ${response.statusCode}');
        } catch (_) {
          throw Exception('Registration failed: ${response.statusCode} - $errorBody');
        }
      }
    } catch (e) {
      if (e.toString().contains('Exception')) {
        rethrow;
      }
      debugPrint('Register network error: $e');
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user info');
    }
  }

  Future<Map<String, dynamic>> sendChatMessage(
    String message, {
    String? sessionId,
    String? language,
    Map<String, dynamic>? typingData,
    Map<String, dynamic>? sensorData,
  }) async {
    final body = {
      'message': message,
      if (sessionId != null) 'session_id': sessionId,
      if (language != null) 'language': language,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/chatbot/chat'),
      headers: _headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      // Provide more detailed error information
      final errorBody = response.body;
      debugPrint('Chat API Error: ${response.statusCode} - $errorBody');
      throw Exception('Failed to send message: ${response.statusCode} - $errorBody');
    }
  }

  Future<Map<String, dynamic>> analyzeVoice(
    String audioPath,
    Map<String, dynamic>? sensorData, {
    String language = 'sinhala',
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/voice/analyze'),
    );

    request.headers.addAll(_headers);
    request.files.add(
      await http.MultipartFile.fromPath('audio_file', audioPath),
    );
    
    // Add language parameter
    request.fields['language'] = language;

    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return jsonDecode(responseBody);
    } else {
      throw Exception('Voice analysis failed');
    }
  }

  Future<List<dynamic>> getSupportedLanguages() async {
    final response = await http.get(
      Uri.parse('$baseUrl/voice/languages'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['languages'] as List;
    } else {
      throw Exception('Failed to get supported languages');
    }
  }

  Future<Map<String, dynamic>> analyzeTyping(
    Map<String, dynamic> typingData,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/typing/analyze'),
      headers: _headers,
      body: jsonEncode(typingData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Typing analysis failed');
    }
  }

  Future<Map<String, dynamic>> getDigitalTwinProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/digital-twin/profile'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get digital twin profile');
    }
  }

  Future<void> updateDigitalTwin() async {
    final response = await http.post(
      Uri.parse('$baseUrl/digital-twin/update'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update digital twin');
    }
  }
}

