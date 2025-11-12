import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class VoiceProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _lastAnalysis;

  Map<String, dynamic>? get lastAnalysis => _lastAnalysis;

  Future<void> analyzeVoice(
    String audioPath,
    Map<String, dynamic>? sensorData,
  ) async {
    try {
      final analysis = await _apiService.analyzeVoice(audioPath, sensorData);
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

