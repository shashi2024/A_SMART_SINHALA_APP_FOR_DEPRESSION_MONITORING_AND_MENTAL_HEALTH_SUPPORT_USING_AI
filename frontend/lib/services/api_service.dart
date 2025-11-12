import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  String? _token;

  void setToken(String? token) {
    _token = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<Map<String, dynamic>> login(String username, String password) async {
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
      throw Exception('Login failed');
    }
  }

  Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
  ) async {
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
      throw Exception('Registration failed');
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
    int? sessionId,
    Map<String, dynamic>? typingData,
    Map<String, dynamic>? sensorData,
  }) async {
    final body = {
      'message': message,
      if (sessionId != null) 'session_id': sessionId,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/chatbot/chat'),
      headers: _headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to send message');
    }
  }

  Future<Map<String, dynamic>> analyzeVoice(
    String audioPath,
    Map<String, dynamic>? sensorData,
  ) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/voice/analyze'),
    );

    request.headers.addAll(_headers);
    request.files.add(
      await http.MultipartFile.fromPath('audio_file', audioPath),
    );

    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return jsonDecode(responseBody);
    } else {
      throw Exception('Voice analysis failed');
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

