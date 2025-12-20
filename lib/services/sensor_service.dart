import 'dart:async';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:permission_handler/permission_handler.dart';

class SensorService {
  StreamSubscription<AccelerometerEvent>? _accelerometerSubscription;
  StreamSubscription<GyroscopeEvent>? _gyroscopeSubscription;
  Timer? _monitoringTimer;
  
  Map<String, dynamic> _sensorData = {
    'accelerometer': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'gyroscope': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'heart_rate': null,
    'timestamp': DateTime.now().toIso8601String(),
  };

  Future<void> initialize() async {
    // Request permissions
    await Permission.sensors.request();
  }

  void startMonitoring() {
    // Monitor accelerometer
    _accelerometerSubscription = accelerometerEventStream().listen((event) {
      _sensorData['accelerometer'] = {
        'x': event.x,
        'y': event.y,
        'z': event.z,
      };
      _sensorData['timestamp'] = DateTime.now().toIso8601String();
    });

    // Monitor gyroscope
    _gyroscopeSubscription = gyroscopeEventStream().listen((event) {
      _sensorData['gyroscope'] = {
        'x': event.x,
        'y': event.y,
        'z': event.z,
      };
      _sensorData['timestamp'] = DateTime.now().toIso8601String();
    });

    // Periodic monitoring
    _monitoringTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _sensorData['timestamp'] = DateTime.now().toIso8601String();
    });
  }

  void stopMonitoring() {
    _accelerometerSubscription?.cancel();
    _gyroscopeSubscription?.cancel();
    _monitoringTimer?.cancel();
  }

  Future<Map<String, dynamic>> getSensorData() async {
    // Add any additional sensor data collection here
    // For example, camera-based heart rate detection, etc.
    return Map<String, dynamic>.from(_sensorData);
  }

  void dispose() {
    stopMonitoring();
  }
}

