import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart';

class PermissionService {
  /// Request all necessary permissions for the app
  Future<void> requestAllPermissions() async {
    if (kIsWeb) {
      debugPrint('Skipping hardware permissions on web');
      return;
    }
    try {
      final statuses = await [
        Permission.camera,
        Permission.microphone,
        Permission.location,
        Permission.sensors,
        // Add notification permission if needed (requires specific handling in some versions)
        Permission.notification,
      ].request();

      _logPermissionStatuses(statuses);
    } catch (e) {
      debugPrint('Error requesting permissions: $e');
    }
  }

  /// Check if a specific permission is granted
  Future<bool> isPermissionGranted(Permission permission) async {
    if (kIsWeb) return true;
    return await permission.isGranted;
  }

  /// Request a specific permission
  Future<PermissionStatus> requestPermission(Permission permission) async {
    if (kIsWeb) return PermissionStatus.granted;
    return await permission.request();
  }

  void _logPermissionStatuses(Map<Permission, PermissionStatus> statuses) {
    statuses.forEach((permission, status) {
      debugPrint('Permission ${permission.toString()} is ${status.toString()}');
    });
  }
}
