import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_provider.dart';

// WebRTC temporarily disabled - using simplified call screen
// import 'package:flutter_webrtc/flutter_webrtc.dart' if (dart.library.html) 'call_screen_web_stub.dart' as webrtc;

class CallScreen extends StatefulWidget {
  final String callId;
  final String callType; // 'counselor', 'ai_practice', 'emergency'
  final String? calleeName;

  const CallScreen({
    super.key,
    required this.callId,
    required this.callType,
    this.calleeName,
  });

  @override
  State<CallScreen> createState() => _CallScreenState();
}

class _CallScreenState extends State<CallScreen> {
  dynamic _peerConnection;
  dynamic _localStream;
  dynamic _remoteStream;
  dynamic _localRenderer;
  dynamic _remoteRenderer;
  bool _isMuted = false;
  bool _isVideoEnabled = true;
  bool _isSpeakerEnabled = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    // WebRTC temporarily disabled
    // if (!kIsWeb) {
    //   _localRenderer = webrtc.RTCVideoRenderer();
    //   _remoteRenderer = webrtc.RTCVideoRenderer();
    // }
    _initializeWebRTC();
  }

  Future<void> _initializeWebRTC() async {
    // WebRTC is not fully supported on web platform
    if (kIsWeb) {
      setState(() {
        _isInitialized = true;
      });
      return;
    }
    
    // WebRTC temporarily disabled - using simplified mode
    // All WebRTC initialization code commented out
    setState(() {
      _isInitialized = true;
    });
    
    // TODO: Re-enable WebRTC after fixing package compatibility
    // try {
    //   await _localRenderer.initialize();
    //   ...
    // } catch (e) { ... }
  }

  Future<dynamic> _createPeerConnection() async {
    // WebRTC temporarily disabled
    return null;
  }

  Future<void> _createOffer() async {
    // WebRTC temporarily disabled
    return;
  }

  String _getCallTypeLabel() {
    switch (widget.callType) {
      case 'counselor':
        return 'Counselor Call';
      case 'ai_practice':
        return 'AI Practice Call';
      case 'emergency':
        return 'Emergency Call';
      default:
        return 'Call';
    }
  }

  String _getCallerName() {
    if (widget.calleeName != null) {
      return widget.calleeName!;
    }
    return widget.callType == 'ai_practice' ? 'AI Assistant' : 'Counselor';
  }

  Widget _buildWebCallView(CallProvider callProvider) {
    // Web fallback - show call UI without WebRTC
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[900],
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.person,
              size: 80,
              color: Colors.grey[600],
            ),
            const SizedBox(height: 16),
            Text(
              _getCallerName(),
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              callProvider.callStatus == CallStatus.ringing
                  ? 'Ringing...'
                  : callProvider.callStatus == CallStatus.connected
                      ? 'Connected (Web - Audio Only)'
                      : 'Connecting...',
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Note: Full WebRTC calling is available on mobile devices.\n'
                'Web platform supports basic call management.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMobileCallView(CallProvider callProvider) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Remote video (if available)
                          // WebRTC video view temporarily disabled
                          // if (_remoteStream != null && !kIsWeb)
                          //   Expanded(child: webrtc.RTCVideoView(...))
        else
          Expanded(
            child: Container(
              decoration: const BoxDecoration(
                color: Colors.grey,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.person,
                      size: 80,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _getCallerName(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      callProvider.callStatus == CallStatus.ringing
                          ? 'Ringing...'
                          : callProvider.callStatus == CallStatus.connected
                              ? 'Connected'
                              : 'Connecting...',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Local video preview temporarily disabled
        // if (_localStream != null && !kIsWeb) ...
      ],
    );
  }

  @override
  void dispose() {
    // WebRTC cleanup temporarily disabled
    // if (!kIsWeb) {
    //   _localRenderer.dispose();
    //   _remoteRenderer.dispose();
    // }
    // _localStream?.dispose();
    // _remoteStream?.dispose();
    // _peerConnection?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final callProvider = Provider.of<CallProvider>(context);

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          children: [
            // Call header
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text(
                          _getCallTypeLabel(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _getCallerName(),
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 48), // Balance for back button
                ],
              ),
            ),

            // Video/Audio area
            Expanded(
              child: Center(
                child: _isInitialized
                    ? kIsWeb
                        ? _buildWebCallView(callProvider)
                        : _buildMobileCallView(callProvider)
                    : const CircularProgressIndicator(color: Colors.white),
              ),
            ),

            // Call controls
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Mute button
                  _buildControlButton(
                    icon: _isMuted ? Icons.mic_off : Icons.mic,
                    color: _isMuted ? Colors.red : Colors.white,
                    onPressed: () {
                      if (kIsWeb) {
                        // Web fallback - just toggle UI state
                        setState(() {
                          _isMuted = !_isMuted;
                        });
                      } else {
                        setState(() {
                          _isMuted = !_isMuted;
                          _localStream?.getAudioTracks().forEach((track) {
                            track.enabled = !_isMuted;
                          });
                        });
                      }
                    },
                  ),

                  // Speaker button
                  _buildControlButton(
                    icon: _isSpeakerEnabled ? Icons.volume_up : Icons.volume_down,
                    color: _isSpeakerEnabled ? Colors.green : Colors.white,
                    onPressed: () {
                      setState(() {
                        _isSpeakerEnabled = !_isSpeakerEnabled;
                        // TODO: Implement speaker toggle
                      });
                    },
                  ),

                  // End call button
                  _buildControlButton(
                    icon: Icons.call_end,
                    color: Colors.red,
                    size: 56,
                    onPressed: () async {
                      await callProvider.endCall();
                      if (mounted) {
                        Navigator.pop(context);
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required Color color,
    required VoidCallback onPressed,
    double size = 48,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        shape: BoxShape.circle,
      ),
      child: IconButton(
        icon: Icon(icon, color: color),
        onPressed: onPressed,
      ),
    );
  }
}

