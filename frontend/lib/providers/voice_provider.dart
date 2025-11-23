import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class VoiceProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _lastAnalysis;
  String _selectedLanguage = 'sinhala';
  List<Map<String, dynamic>>? _supportedLanguages;

  Map<String, dynamic>? get lastAnalysis => _lastAnalysis;
  String get selectedLanguage => _selectedLanguage;
  List<Map<String, dynamic>>? get supportedLanguages => _supportedLanguages;

  VoiceProvider() {
    _loadLanguagePreference();
    _loadSupportedLanguages();
  }

  Future<void> _loadLanguagePreference() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedLanguage = prefs.getString('selected_language');
      if (savedLanguage != null) {
        _selectedLanguage = savedLanguage;
        notifyListeners();
      }
    } catch (e) {
      // Use default language
    }
  }

  Future<void> loadSupportedLanguages() async {
    try {
      final languages = await _apiService.getSupportedLanguages();
      _supportedLanguages = languages.map((lang) => Map<String, dynamic>.from(lang)).toList();
      notifyListeners();
    } catch (e) {
      // Set default languages if API fails
      _supportedLanguages = [
        {'code': 'sinhala', 'name': 'Sinhala', 'native_name': 'සිංහල'},
        {'code': 'tamil', 'name': 'Tamil', 'native_name': 'தமிழ்'},
        {'code': 'english', 'name': 'English', 'native_name': 'English'},
      ];
      notifyListeners();
    }
  }

  Future<void> _loadSupportedLanguages() async {
    await loadSupportedLanguages();
  }

  Future<void> setLanguage(String language) async {
    _selectedLanguage = language;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('selected_language', language);
    } catch (e) {
      // Ignore storage errors
    }
    notifyListeners();
  }

  Future<void> analyzeVoice(
    String audioPath,
    Map<String, dynamic>? sensorData, {
    String? language,
  }) async {
    try {
      final lang = language ?? _selectedLanguage;
      final analysis = await _apiService.analyzeVoice(audioPath, sensorData, language: lang);
      _lastAnalysis = analysis;
      notifyListeners();
    } catch (e) {
      _lastAnalysis = null;
      notifyListeners();
      rethrow;
    }
  }

  void clearAnalysis() {
    _lastAnalysis = null;
    notifyListeners();
  }
}

