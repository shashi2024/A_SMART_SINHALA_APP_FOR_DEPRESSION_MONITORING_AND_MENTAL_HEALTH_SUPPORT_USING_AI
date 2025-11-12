import 'package:flutter/foundation.dart';
import '../services/sensor_service.dart';

class SensorProvider with ChangeNotifier {
  final SensorService _sensorService = SensorService();
  Map<String, dynamic>? _currentData;

  Map<String, dynamic>? get currentData => _currentData;

  Future<void> initialize() async {
    await _sensorService.initialize();
  }

  Future<Map<String, dynamic>> getCurrentSensorData() async {
    _currentData = await _sensorService.getSensorData();
    notifyListeners();
    return _currentData!;
  }

  void startMonitoring() {
    _sensorService.startMonitoring();
  }

  void stopMonitoring() {
    _sensorService.stopMonitoring();
  }

  void dispose() {
    _sensorService.dispose();
    super.dispose();
  }
}

