import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/language_provider.dart';
import '../providers/chatbot_provider.dart';
import '../providers/sensor_provider.dart';
import '../services/typing_analyzer.dart';
import 'login_screen.dart'; // For AppColors
import 'chat_screen.dart';

class WelcomeChatScreen extends StatefulWidget {
  const WelcomeChatScreen({super.key});

  @override
  State<WelcomeChatScreen> createState() => _WelcomeChatScreenState();
}

class _WelcomeChatScreenState extends State<WelcomeChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final TypingAnalyzer _typingAnalyzer = TypingAnalyzer();
  bool _hasStartedChat = false;
  bool _showLoginPrompt = false;
  int _messageCount = 0;
  bool _hasShownCameraPrompt = false;
  bool _hasShownVoicePrompt = false;

  @override
  void initState() {
    super.initState();
    _typingAnalyzer.startTracking();
    
    // Initialize chatbot provider (without auth token for first-time users)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Don't set token - allow anonymous chat
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

    // Send message (without authentication for first-time users)
    await chatbotProvider.sendMessage(
      _messageController.text,
      typingData: typingData,
      sensorData: sensorData,
    );

    _messageController.clear();
    _typingAnalyzer.reset();

    // Increment message count
    setState(() {
      _messageCount++;
      // Show login prompt after 3-5 messages
      if (_messageCount >= 3 && !_showLoginPrompt) {
        _showLoginPrompt = true;
      }

      // Around 5–6th message: invite user to quick camera-based check-in
      if ((_messageCount == 5 || _messageCount == 6) && !_hasShownCameraPrompt) {
        _hasShownCameraPrompt = true;
        _showCameraPrompt();
      }

      // Around 8–9th message: invite user to quick voice check
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

  Future<void> _handleLogin() async {
    // Mark that user has seen the welcome screen
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('has_seen_welcome', true);
    
    // Navigate to login
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  Future<void> _showCameraPrompt() async {
    if (!mounted) return;
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Quick camera check-in'),
        content: const Text(
          'To better understand your current state, Sahana can take a short, one-time '
          'snapshot using your front camera. This helps the biofeedback system analyse '
          'facial cues together with sensor data.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Maybe later'),
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
        title: const Text('Optional voice check'),
        content: const Text(
          'A short 10–15 second voice sample helps detect stress patterns and fake-caller '
          'behaviour using our audio models. You can skip this if you are not comfortable.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Skip for now'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pushNamed('/voice');
            },
            child: const Text('Record short sample'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();
    final media = MediaQuery.of(context);
    final isNarrow = media.size.width < 380 || media.textScaler.scale(1.0) > 1.15;
    return Scaffold(
      appBar: AppBar(
        // Give the app bar a solid background and avoid drawing it under
        // the system status bar / Flutter debug banner. On some phones
        // the previous transparent + overlay setup caused the login
        // button in the top‑right to be hidden.
        title: Text(
          lp.translate('chat_with_sahana'),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
        backgroundColor: AppColors.creamYellow,
        iconTheme: const IconThemeData(color: AppColors.darkGreen),
        elevation: 0.5,
        actions: [
          if (isNarrow)
            IconButton(
              tooltip: lp.translate('login'),
              onPressed: _handleLogin,
              icon: const Icon(Icons.login, color: AppColors.darkGreen, size: 22),
            )
          else
            TextButton.icon(
              onPressed: _handleLogin,
              icon: const Icon(Icons.login, color: AppColors.darkGreen, size: 20),
              label: Text(
                lp.translate('login'),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: AppColors.darkGreen,
                ),
              ),
            ),
          const SizedBox(width: 8),
        ],
      ),
      // Do not extend the body behind the app bar so that the login
      // button is always fully visible on mobile devices.
      extendBodyBehindAppBar: false,
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
              if (_showLoginPrompt)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: AppColors.darkGreen,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(
                            Icons.info_outline,
                            color: Colors.white,
                            size: 24,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              lp.translate('continue_conversation'),
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        lp.translate('login_save_history'),
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _handleLogin,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: AppColors.darkGreen,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: Text(
                            lp.translate('login_continue'),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pushNamed('/signup');
                        },
                        child: Text(
                          lp.translate('dont_have_account_signup'),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            decoration: TextDecoration.underline,
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
                      return _buildInitialGreeting(lp);
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
                      color: Colors.grey.withValues(alpha: 0.2),
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
                          hintStyle: const TextStyle(color: Colors.grey),
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 0,
                            vertical: 16.0,
                          ),
                        ),
                        onSubmitted: (_) => _sendMessage(),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(
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
                        text: lp.translate('sahana_listen').split(' is here')[0], // Extract SAHANA
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AppColors.darkGreen,
                        ),
                      ),
                      TextSpan(
                        text: lp.translate('sahana_listen').contains('SAHANA') 
                            ? lp.translate('sahana_listen').substring(lp.translate('sahana_listen').indexOf('SAHANA') + 6)
                            : lp.translate('sahana_listen'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  lp.translate('start_chatting_journey'),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
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
            child: Text(
              message.text,
              style: TextStyle(
                color: message.isUser
                    ? Colors.white
                    : Colors.black87,
                fontSize: 16,
              ),
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

