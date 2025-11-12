import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class DigitalTwinProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _profile;
  List<String>? _riskFactors;

  Map<String, dynamic>? get profile => _profile;
  List<String>? get riskFactors => _riskFactors;

  Future<void> loadProfile() async {
    try {
      final data = await _apiService.getDigitalTwinProfile();
      _profile = data['profile'];
      _riskFactors = List<String>.from(data['risk_factors'] ?? []);
      notifyListeners();
    } catch (e) {
      _profile = null;
      _riskFactors = null;
      notifyListeners();
    }
  }

  Future<void> updateProfile() async {
    try {
      await _apiService.updateDigitalTwin();
      await loadProfile();
    } catch (e) {
      rethrow;
    }
  }
}

