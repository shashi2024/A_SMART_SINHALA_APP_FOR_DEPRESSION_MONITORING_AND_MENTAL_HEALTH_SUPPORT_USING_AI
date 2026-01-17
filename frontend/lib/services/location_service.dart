import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'api_service.dart';

class LocationService {
  final ApiService _apiService;
  bool _isTracking = false;
  Position? _lastPosition;

  LocationService({ApiService? apiService}) 
      : _apiService = apiService ?? ApiService();

  /// Request location permissions
  Future<bool> requestPermission() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('Location services are disabled.');
        return false;
      }

      // Check location permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          print('Location permissions are denied');
          return false;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        print('Location permissions are permanently denied');
        return false;
      }

      return true;
    } catch (e) {
      print('Error requesting location permission: $e');
      return false;
    }
  }

  /// Get current location
  Future<Position?> getCurrentLocation() async {
    try {
      bool hasPermission = await requestPermission();
      if (!hasPermission) {
        return null;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      _lastPosition = position;
      return position;
    } catch (e) {
      print('Error getting current location: $e');
      return null;
    }
  }

  /// Update location to backend
  Future<bool> updateLocation({
    required String phoneNumber,
    Position? position,
  }) async {
    try {
      Position? currentPosition = position ?? await getCurrentLocation();
      if (currentPosition == null) {
        print('Could not get current location');
        return false;
      }

      final response = await _apiService.post(
        '/location/update',
        {
          'phone_number': phoneNumber,
          'latitude': currentPosition.latitude,
          'longitude': currentPosition.longitude,
          'accuracy': currentPosition.accuracy,
          'altitude': currentPosition.altitude,
          'speed': currentPosition.speed,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response['message'] == 'Location updated successfully') {
        _lastPosition = currentPosition;
        return true;
      }

      return false;
    } catch (e) {
      print('Error updating location: $e');
      return false;
    }
  }

  /// Start continuous location tracking
  Future<void> startTracking({
    required String phoneNumber,
    Duration interval = const Duration(minutes: 5),
  }) async {
    if (_isTracking) {
      print('Location tracking is already active');
      return;
    }

    bool hasPermission = await requestPermission();
    if (!hasPermission) {
      print('Location permission not granted');
      return;
    }

    _isTracking = true;

    // Update location immediately
    await updateLocation(phoneNumber: phoneNumber);

    // Set up periodic updates
    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 100, // Update every 100 meters
      ),
    ).listen((Position position) async {
      if (_isTracking) {
        await updateLocation(phoneNumber: phoneNumber, position: position);
      }
    });
  }

  /// Stop location tracking
  void stopTracking() {
    _isTracking = false;
  }

  /// Check if tracking is active
  bool get isTracking => _isTracking;

  /// Get last known position
  Position? get lastPosition => _lastPosition;
}

