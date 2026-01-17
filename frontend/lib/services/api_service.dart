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
  //static const String baseUrl = 'http://localhost:8000/api';
  static const String baseUrl = 'http://192.168.8.111:8000/api';
  
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

  Future<Map<String, dynamic>> login(String usernameOrEmail, String password) async {
    try {
      // Determine if input is email or username by checking for @ symbol
      final Map<String, dynamic> loginData;
      if (usernameOrEmail.contains('@')) {
        // It's an email
        loginData = {
          'email': usernameOrEmail,
          'password': password,
        };
      } else {
        // It's a username
        loginData = {
          'username': usernameOrEmail,
          'password': password,
        };
      }
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: _headers,
        body: jsonEncode(loginData),
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
    String password, [
    String? phoneNumber,
  ]) async {
    try {
      final body = {
        'username': username,
        'email': email,
        'password': password,
      };
      if (phoneNumber != null && phoneNumber.isNotEmpty) {
        body['phone_number'] = phoneNumber;
      }
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: _headers,
        body: jsonEncode(body),
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

  // ========== CALL METHODS ==========

  Future<Map<String, dynamic>> createCall({
    required String callType, // 'counselor', 'ai_practice', 'emergency'
    String? calleeId,
    String language = 'en',
  }) async {
    final body = {
      'call_type': callType,
      'language': language,
      if (calleeId != null) 'callee_id': calleeId,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/calls/create'),
      headers: _headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final errorBody = response.body;
      debugPrint('Create Call API Error: ${response.statusCode} - $errorBody');
      throw Exception('Failed to create call: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> getCall(String callId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/calls/$callId'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get call');
    }
  }

  Future<void> endCall(String callId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/calls/$callId/end'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to end call');
    }
  }

  Future<void> rejectCall(String callId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/calls/$callId/reject'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to reject call');
    }
  }

  Future<List<dynamic>> getCallHistory({
    String? callType,
    int limit = 50,
  }) async {
    final queryParams = <String, String>{
      'limit': limit.toString(),
      if (callType != null) 'call_type': callType,
    };

    final uri = Uri.parse('$baseUrl/calls/history').replace(
      queryParameters: queryParams,
    );

    final response = await http.get(
      uri,
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['calls'] as List;
    } else {
      throw Exception('Failed to get call history');
    }
  }

  Future<List<dynamic>> getAvailableCounselors({String language = 'en'}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/calls/counselors/available?language=$language'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['counselors'] as List;
    } else {
      throw Exception('Failed to get available counselors');
    }
  }

  // ========== MOOD CHECK-IN METHODS ==========

  Future<Map<String, dynamic>> createMoodCheckIn(String mood, {String? notes}) async {
    try {
      final body = {
        'mood': mood,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/mood/checkin'),
        headers: _headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorBody = response.body;
        debugPrint('Mood Check-in API Error: ${response.statusCode} - $errorBody');
        try {
          final errorJson = jsonDecode(errorBody);
          throw Exception(errorJson['detail'] ?? 'Failed to save mood check-in: ${response.statusCode}');
        } catch (_) {
          throw Exception('Failed to save mood check-in: ${response.statusCode} - $errorBody');
        }
      }
    } catch (e) {
      if (e.toString().contains('Exception')) {
        rethrow;
      }
      debugPrint('Mood Check-in network error: $e');
      throw Exception('Network error: ${e.toString()}');
    }
  }

  Future<List<dynamic>> getMoodHistory({
    int limit = 50,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
        if (startDate != null) 'start_date': startDate,
        if (endDate != null) 'end_date': endDate,
      };

      final uri = Uri.parse('$baseUrl/mood/history').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as List;
      } else {
        throw Exception('Failed to get mood history: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Mood history error: $e');
      rethrow;
    }
  }

  // ========== LOCATION METHODS ==========

  Future<Map<String, dynamic>> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        final errorBody = response.body;
        debugPrint('POST API Error: ${response.statusCode} - $errorBody');
        try {
          final errorJson = jsonDecode(errorBody);
          throw Exception(errorJson['detail'] ?? 'Request failed: ${response.statusCode}');
        } catch (_) {
          throw Exception('Request failed: ${response.statusCode} - $errorBody');
        }
      }
    } catch (e) {
      if (e.toString().contains('Exception')) {
        rethrow;
      }
      debugPrint('POST network error: $e');
      throw Exception('Network error: ${e.toString()}');
    }
  }
}

