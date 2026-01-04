import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chatbot_provider.dart';
import '../providers/auth_provider.dart';
import '../providers/sensor_provider.dart';
import '../services/typing_analyzer.dart';
import 'login_screen.dart'; // For AppColors

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

  @override
  void initState() {
    super.initState();
    _typingAnalyzer.startTracking();
    
    // Sync authentication token to chatbot provider
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final chatbotProvider = Provider.of<ChatbotProvider>(context, listen: false);
      if (authProvider.token != null) {
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
      typingData: typingData,
      sensorData: sensorData,
    );

    _messageController.clear();
    _typingAnalyzer.reset();

    // Scroll to bottom
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
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
              // Header with back button and title
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
                        'Chat with me ........',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[800],
                        ),
                      ),
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
                      return _buildInitialGreeting();
                    } else {
                      // Chat messages
                      return _buildChatMessages(provider);
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
                        decoration: const InputDecoration(
                          hintText: 'Tell me what\'s on your mind.....',
                          hintStyle: TextStyle(color: Colors.grey),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 0,
                            vertical: 16.0,
                          ),
                        ),
                        onSubmitted: (_) => _sendMessage(),
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.mic,
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

  Widget _buildInitialGreeting() {
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
                        text: 'SAHANA',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AppColors.darkGreen,
                        ),
                      ),
                      const TextSpan(
                        text: ' is here to listen to you,\n',
                      ),
                      const TextSpan(
                        text: 'How are you feeling right now?',
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

  Widget _buildChatMessages(ChatbotProvider provider) {
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
                      'Risk: ${message.riskLevel}',
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
