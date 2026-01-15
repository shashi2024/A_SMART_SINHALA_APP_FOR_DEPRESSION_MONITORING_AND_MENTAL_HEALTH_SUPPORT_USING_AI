// Stub file for web - prevents WebRTC import errors
// This file is used when compiling for web

import 'package:flutter/widgets.dart';

class RTCPeerConnection {
  Future<void> close() async {}
  Future<dynamic> createOffer() async => throw UnimplementedError();
  Future<void> setLocalDescription(dynamic description) async {}
  void onTrack(dynamic Function(dynamic) handler) {}
  void onIceCandidate(dynamic Function(dynamic) handler) {}
  void addTrack(dynamic track, dynamic stream) {}
}

class MediaStream {
  List<dynamic> getTracks() => [];
  void dispose() {}
}

class RTCVideoRenderer {
  Future<void> initialize() async {}
  void dispose() {}
  set srcObject(MediaStream? stream) {}
}

class RTCVideoViewObjectFit {
  static const String RTCVideoViewObjectFitCover = 'cover';
}

class RTCVideoView extends StatelessWidget {
  final RTCVideoRenderer renderer;
  final bool mirror;
  final String objectFit;
  
  const RTCVideoView(
    this.renderer, {
    this.mirror = false,
    this.objectFit = 'cover',
    super.key,
  });
  
  @override
  Widget build(BuildContext context) => const SizedBox();
}

Future<RTCPeerConnection> createPeerConnection(Map<String, dynamic> config) async {
  throw UnimplementedError('WebRTC not supported on web');
}

Future<MediaStream> getUserMedia(Map<String, dynamic> constraints) async {
  throw UnimplementedError('getUserMedia not supported on web');
}

// Extension for navigator.mediaDevices
extension NavigatorExtension on dynamic {
  MediaDevices get mediaDevices => _MediaDevicesStub();
}

class MediaDevices {
  Future<MediaStream> getUserMedia(Map<String, dynamic> constraints) async {
    throw UnimplementedError('getUserMedia not supported on web');
  }
}

class _MediaDevicesStub implements MediaDevices {
  @override
  Future<MediaStream> getUserMedia(Map<String, dynamic> constraints) async {
    throw UnimplementedError('getUserMedia not supported on web');
  }
}

