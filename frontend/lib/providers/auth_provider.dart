import 'package:flutter/foundation.dart';
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

  User? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null;

  Future<bool> login(String username, String password) async {
    try {
      final response = await _apiService.login(username, password);
      _token = response['access_token'];
      _apiService.setToken(_token!);
      
      // Get user info
      final userInfo = await _apiService.getCurrentUser();
      _user = User.fromJson(userInfo);
      
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    try {
      final response = await _apiService.register(username, email, password);
      _token = response['access_token'];
      _apiService.setToken(_token!);
      
      // Get user info
      final userInfo = await _apiService.getCurrentUser();
      _user = User.fromJson(userInfo);
      
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  void logout() {
    _token = null;
    _user = null;
    _apiService.setToken(null);
    notifyListeners();
  }
}

