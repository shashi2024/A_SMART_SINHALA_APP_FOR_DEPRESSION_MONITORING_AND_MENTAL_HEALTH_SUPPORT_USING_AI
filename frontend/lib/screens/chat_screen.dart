import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chatbot_provider.dart';
import '../providers/auth_provider.dart';
import '../providers/sensor_provider.dart';
import '../providers/call_provider.dart';
import '../services/typing_analyzer.dart';
import '../providers/language_provider.dart';
import 'login_screen.dart'; // For AppColors
import 'call_screen_simple.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final TypingAnalyzer _typingAnalyzer = TypingAnalyzer();
  bool _hasStartedChat = false;
  String _lastText = "";
  int _messageCount = 0;
  bool _hasShownCameraPrompt = false;
  bool _hasShownVoicePrompt = false;

  @override
  void initState() {
    super.initState();
    _typingAnalyzer.startTracking();
    
    // Sync authentication token to chatbot provider
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      if (authProvider.token != null) {
        final chatbotProvider = Provider.of<ChatbotProvider>(context, listen: false);
        chatbotProvider.setToken(authProvider.token);
      }
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _typingAnalyzer.stopTracking();
    super.dispose();
  }

  void _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    if (!_hasStartedChat) {
      setState(() {
        _hasStartedChat = true;
      });
    }

    final chatbotProvider = Provider.of<ChatbotProvider>(context, listen: false);
    final sensorProvider = Provider.of<SensorProvider>(context, listen: false);

    // Get typing analysis
    final typingData = await _typingAnalyzer.getAnalysis();
    
    // Get sensor data
    final sensorData = await sensorProvider.getCurrentSensorData();

    // Send message with typing and sensor data
    await chatbotProvider.sendMessage(
      _messageController.text,
      keystrokeEvents: (typingData['keystroke_events'] as List?)?.cast<Map<String, dynamic>>(),
      typingData: typingData,
      sensorData: sensorData,
    );
    
    _lastText = ""; // Reset last text after sending

    _messageController.clear();
    _typingAnalyzer.reset();

    setState(() {
      _messageCount++;

      if ((_messageCount == 5 || _messageCount == 6) && !_hasShownCameraPrompt) {
        _hasShownCameraPrompt = true;
        _showCameraPrompt();
      }

      if ((_messageCount == 8 || _messageCount == 9) && !_hasShownVoicePrompt) {
        _hasShownVoicePrompt = true;
        _showVoicePrompt();
      }
    });

    // Scroll to bottom
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  Future<void> _showCameraPrompt() async {
    if (!mounted) return;
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Quick camera check-in'),
        content: const Text(
          'After a few messages, Sahana can use a short front-camera snapshot together with '
          'sensor data to better understand your stress level. This is optional and used '
          'only for your mental health analysis.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Not now'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pushNamed('/bio-feedback');
            },
            child: const Text('Open camera'),
          ),
        ],
      ),
    );
  }

  Future<void> _showVoicePrompt() async {
    if (!mounted) return;
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Short voice sample'),
        content: const Text(
          'Sahana can record a brief voice sample (10–15 seconds) to analyse stress and '
          'detect fake or synthetic callers. You stay in full control and can decline.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Skip'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pushNamed('/voice');
            },
            child: const Text('Record sample'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.paleSageGreen.withValues(alpha: 0.3),
              AppColors.creamYellow,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header with back button, title, and call button
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: Icon(Icons.arrow_back, color: Colors.grey[800]),
                      onPressed: () {
                        // Navigate to home screen
                        Navigator.of(context).pushReplacementNamed('/home');
                      },
                    ),
                    Expanded(
                      child: Text(
                        lp.translate('chat_with_me'),
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.phone,
                        color: AppColors.darkGreen,
                        size: 28,
                      ),
                      onPressed: () async {
                        // Start AI practice call via API
                        final callProvider = Provider.of<CallProvider>(context, listen: false);
                        try {
                          final callId = await callProvider.createCall(
                            callType: CallType.aiPractice,
                            language: callProvider.language,
                          );
                          if (mounted) {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => CallScreenSimple(
                              callId: callId,
                                  callType: 'ai_practice',
                              calleeName: 'Sahana',
                            ),
                          ),
                        );
                          }
                        } catch (e) {
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('${lp.translate('failed_start_call')}: $e')),
                            );
                          }
                        }
                      },
                      tooltip: lp.translate('start_call'),
                    ),
                  ],
                ),
              ),
              
              // Main content area
              Expanded(
                child: Consumer<ChatbotProvider>(
                  builder: (context, provider, child) {
                    if (!_hasStartedChat && provider.messages.isEmpty) {
                      // Initial greeting screen
                      return _buildInitialGreeting(lp);
                    } else {
                      // Chat messages
                      return _buildChatMessages(provider, lp);
                    }
                  },
                ),
              ),
              
              // Input area
              Container(
                margin: const EdgeInsets.all(16.0),
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.2),
                      spreadRadius: 1,
                      blurRadius: 5,
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _messageController,
                        decoration: InputDecoration(
                          hintText: lp.translate('mind_hint'),
                          hintStyle: TextStyle(color: Colors.grey),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 0,
                            vertical: 16.0,
                          ),
                        ),
                        onChanged: (text) {
                          bool isBackspace = text.length < _lastText.length;
                          _typingAnalyzer.recordKeystrokeWithDetails(
                            isBackspace ? 'Backspace' : (text.isNotEmpty ? text[text.length - 1] : 'key'),
                            isBackspace: isBackspace,
                          );
                          _lastText = text;
                        },
                        onSubmitted: (_) => _sendMessage(),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.send,
                        color: AppColors.darkGreen,
                        size: 28,
                      ),
                      onPressed: _sendMessage,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInitialGreeting(LanguageProvider lp) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Floating orb graphic
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppColors.lightPeach.withValues(alpha: 0.6),
                  AppColors.veryLightBlue.withValues(alpha: 0.3),
                  Colors.white.withValues(alpha: 0.1),
                ],
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.lightPeach.withValues(alpha: 0.3),
                  blurRadius: 30,
                  spreadRadius: 10,
                ),
              ],
            ),
            child: CustomPaint(
              size: const Size(200, 200),
              painter: FloatingOrbPainter(),
            ),
          ),
          
          const SizedBox(height: 40),
          
          // Greeting text
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32.0),
            child: Column(
              children: [
                RichText(
                  textAlign: TextAlign.center,
                  text: TextSpan(
                    style: const TextStyle(
                      fontSize: 18,
                      color: Colors.black87,
                      height: 1.5,
                    ),
                    children: [
                      TextSpan(
                        text: lp.translate('sahana_listen'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatMessages(ChatbotProvider provider, LanguageProvider lp) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16.0),
      itemCount: provider.messages.length,
      itemBuilder: (context, index) {
        final message = provider.messages[index];
        return Align(
          alignment: message.isUser
              ? Alignment.centerRight
              : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.only(bottom: 12.0),
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 12.0,
            ),
            decoration: BoxDecoration(
              color: message.isUser
                  ? AppColors.darkGreen
                  : Colors.white,
              borderRadius: BorderRadius.circular(20.0),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  blurRadius: 5,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  message.text,
                  style: TextStyle(
                    color: message.isUser
                        ? Colors.white
                        : Colors.black87,
                    fontSize: 16,
                  ),
                ),
                if (message.depressionScore != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      '${lp.translate('risk')}: ${message.riskLevel}',
                      style: TextStyle(
                        fontSize: 12,
                        color: message.isUser
                            ? Colors.white70
                            : Colors.grey[600],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}

// Custom painter for floating orb
class FloatingOrbPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Create swirling gradient effect
    final paint = Paint()
      ..shader = RadialGradient(
        colors: [
          AppColors.lightPeach.withValues(alpha: 0.8),
          AppColors.veryLightBlue.withValues(alpha: 0.4),
          Colors.white.withValues(alpha: 0.2),
        ],
      ).createShader(
        Rect.fromCircle(center: center, radius: radius),
      );

    // Draw main circle
    canvas.drawCircle(center, radius, paint);

    // Add some swirling patterns
    final swirlPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (int i = 0; i < 3; i++) {
      final path = Path();
      final angle = (i * 2 * math.pi / 3) - math.pi / 2;
      final startX = center.dx + (radius * 0.3) * math.cos(angle);
      final startY = center.dy + (radius * 0.3) * math.sin(angle);
      
      path.moveTo(startX, startY);
      for (double t = 0; t <= 1; t += 0.1) {
        final currentAngle = angle + (t * 2 * math.pi);
        final currentRadius = radius * (0.3 + t * 0.4);
        final x = center.dx + currentRadius * math.cos(currentAngle);
        final y = center.dy + currentRadius * math.sin(currentAngle);
        path.lineTo(x, y);
      }
      canvas.drawPath(path, swirlPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
