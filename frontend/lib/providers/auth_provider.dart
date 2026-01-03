import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class User {
  final int id;
  final String username;
  final String email;
  final bool isAdmin;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.isAdmin,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      isAdmin: json['is_admin'] ?? false,
    );
  }
}

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  User? _user;
  String? _token;

  AuthProvider() {
    _loadToken();
  }

  User? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null;

  Future<void> _loadToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedToken = prefs.getString('auth_token');
      if (savedToken != null) {
        _token = savedToken;
        _apiService.setToken(_token!);
        
        // Try to get user info
        try {
          final userInfo = await _apiService.getCurrentUser();
          _user = User.fromJson(userInfo);
          notifyListeners();
        } catch (e) {
          // Token might be expired, clear it
          debugPrint('Token validation failed: $e');
          await _clearToken();
        }
      }
    } catch (e) {
      debugPrint('Error loading token: $e');
    }
  }

  Future<void> _saveToken(String token) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', token);
    } catch (e) {
      debugPrint('Error saving token: $e');
    }
  }

  Future<void> _clearToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
      _token = null;
      _user = null;
      _apiService.setToken(null);
      notifyListeners();
    } catch (e) {
      debugPrint('Error clearing token: $e');
    }
  }

  Future<bool> login(String username, String password) async {
    try {
      final response = await _apiService.login(username, password);
      _token = response['access_token'];
      _apiService.setToken(_token!);
      
      // Save token to persistent storage
      await _saveToken(_token!);
      
      // Get user info
      try {
        final userInfo = await _apiService.getCurrentUser();
        _user = User.fromJson(userInfo);
      } catch (e) {
        debugPrint('Warning: Could not fetch user info: $e');
        // User info fetch failed, but login was successful
        // Create a minimal user object
        _user = User(
          id: 0,
          username: username,
          email: '',
          isAdmin: false,
        );
      }
      
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('Login error: $e');
      // Don't throw, just return false and let UI handle the error
      return false;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    try {
      final response = await _apiService.register(username, email, password);
      _token = response['access_token'];
      _apiService.setToken(_token!);
      
      // Save token to persistent storage
      await _saveToken(_token!);
      
      // Get user info
      try {
        final userInfo = await _apiService.getCurrentUser();
        _user = User.fromJson(userInfo);
      } catch (e) {
        debugPrint('Warning: Could not fetch user info: $e');
        // User info fetch failed, but registration was successful
        // Create a minimal user object
        _user = User(
          id: 0,
          username: username,
          email: email,
          isAdmin: false,
        );
      }
      
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('Registration error: $e');
      // Don't throw, just return false and let UI handle the error
      return false;
    }
  }

  Future<void> logout() async {
    await _clearToken();
  }
  
  // Method to sync token to other providers (like ChatbotProvider)
  String? getToken() => _token;
}

