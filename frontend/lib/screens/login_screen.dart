import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/auth_provider.dart';
import '../providers/chatbot_provider.dart';
import '../providers/call_provider.dart';

// Color Palette Constants
class AppColors {
  static const Color darkGreen = Color(0xFF185846);
  static const Color paleSageGreen = Color(0xFFD2DEBF);
  static const Color lightPeach = Color(0xFFECD0B6);
  static const Color creamYellow = Color(0xFFF2E8C9);
  static const Color veryLightBlue = Color(0xFFE5F1F5);
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSignIn() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatbotProvider = Provider.of<ChatbotProvider>(context, listen: false);

    bool success = false;
    String? errorMessage;

    try {
      // Login with email - backend now supports email login
      success = await authProvider.login(
        _emailController.text.trim(),
        _passwordController.text,
      );
    } catch (e) {
      success = false;
      errorMessage = e.toString();
      debugPrint('Auth error: $e');
    }

    setState(() {
      _isLoading = false;
    });

    if (success) {
      // Mark that user has seen welcome screen
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('has_seen_welcome', true);
      } catch (e) {
        debugPrint('Error saving welcome flag: $e');
      }
      
      // Sync token to chatbot provider and call provider
      if (authProvider.token != null) {
        chatbotProvider.setToken(authProvider.token);
        final callProvider = Provider.of<CallProvider>(context, listen: false);
        callProvider.setToken(authProvider.token);
      }
      
      // Navigate to home screen
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } else {
      if (mounted) {
        String displayMessage = 'Login failed. Please check your credentials and ensure the backend server is running.';
        
        // Check for specific error types
        if (errorMessage != null) {
          final errorStr = errorMessage.toLowerCase();
          if (errorStr.contains('connection') || errorStr.contains('failed host lookup') || errorStr.contains('network')) {
            displayMessage = 'Cannot connect to server. Please ensure the backend is running at http://localhost:8000';
          } else if (errorStr.contains('401') || errorStr.contains('unauthorized')) {
            displayMessage = 'Invalid email or password. Please try again.';
          } else if (errorStr.contains('400')) {
            displayMessage = 'Invalid input. Please check your information.';
          }
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(displayMessage),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 60),
                
                // Logo
                _buildLogo(),
                
                const SizedBox(height: 40),
                
                // Welcome Message
                Text(
                  'Welcome Back!',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                    letterSpacing: -0.5,
                  ),
                ),
                
                const SizedBox(height: 8),
                
                // Subtitle
                Text(
                  'Let\'s continue your educational journey!',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w400,
                  ),
                ),
                
                const SizedBox(height: 48),
                
                // Email Field
                Text(
                  'Email',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: InputDecoration(
                    hintText: 'Enter your student email',
                    hintStyle: TextStyle(color: Colors.grey[400]),
                    filled: true,
                    fillColor: Colors.grey[100],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Please enter your email';
                    }
                    if (!value.contains('@')) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                ),
                
                const SizedBox(height: 24),
                
                // Password Field
                Text(
                  'Password',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    hintText: 'Enter your password',
                    hintStyle: TextStyle(color: Colors.grey[400]),
                    filled: true,
                    fillColor: Colors.grey[100],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_off
                            : Icons.visibility,
                        color: Colors.grey[600],
                      ),
                      onPressed: () {
                        setState(() {
                          _obscurePassword = !_obscurePassword;
                        });
                      },
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter your password';
                    }
                    return null;
                  },
                ),
                
                const SizedBox(height: 12),
                
                // Forgot Password Link
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {
                      // TODO: Implement forgot password functionality
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Forgot password functionality coming soon'),
                        ),
                      );
                    },
                    style: TextButton.styleFrom(
                      padding: EdgeInsets.zero,
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    child: Text(
                      'Forgot Password?',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Sign In Button
                ElevatedButton(
                  onPressed: _isLoading ? null : _handleSignIn,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.darkGreen,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 0,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Sign In',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                ),
                
                const SizedBox(height: 24),
                
                // Sign Up Link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Don\'t have an account? ',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    TextButton(
                      onPressed: _isLoading
                          ? null
                          : () {
                              Navigator.of(context).pushNamed('/signup');
                            },
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        'Sign Up',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppColors.darkGreen,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLogo() {
    return Center(
      child: SizedBox(
        width: 120,
        height: 120,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Background circle with gradient
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.veryLightBlue,
                    AppColors.paleSageGreen.withValues(alpha: 0.3),
                  ],
                ),
              ),
            ),
            // Heart shape with medical cross
            CustomPaint(
              size: const Size(100, 100),
              painter: LogoPainter(),
            ),
          ],
        ),
      ),
    );
  }
}

// Custom painter for logo (heart, cross, stars)
class LogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final centerX = width / 2;
    final centerY = height / 2;

    // Draw heart shape (pink/purple)
    final heartPaint = Paint()
      ..color = const Color(0xFFE91E63) // Pink color
      ..style = PaintingStyle.fill;

    final heartPath = Path();
    heartPath.moveTo(centerX, centerY + height * 0.15);
    heartPath.cubicTo(
      centerX, centerY,
      centerX - width * 0.15, centerY - height * 0.1,
      centerX - width * 0.15, centerY + height * 0.05,
    );
    heartPath.cubicTo(
      centerX - width * 0.15, centerY + height * 0.15,
      centerX - width * 0.05, centerY + height * 0.2,
      centerX, centerY + height * 0.25,
    );
    heartPath.cubicTo(
      centerX + width * 0.05, centerY + height * 0.2,
      centerX + width * 0.15, centerY + height * 0.15,
      centerX + width * 0.15, centerY + height * 0.05,
    );
    heartPath.cubicTo(
      centerX + width * 0.15, centerY - height * 0.1,
      centerX, centerY,
      centerX, centerY + height * 0.15,
    );
    canvas.drawPath(heartPath, heartPaint);

    // Draw medical cross (blue)
    final crossPaint = Paint()
      ..color = AppColors.darkGreen
      ..style = PaintingStyle.fill
      ..strokeWidth = 4;

    final crossSize = width * 0.25;
    final crossThickness = width * 0.08;
    
    // Vertical line
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(
          center: Offset(centerX, centerY),
          width: crossThickness,
          height: crossSize,
        ),
        const Radius.circular(2),
      ),
      crossPaint,
    );
    
    // Horizontal line
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(
          center: Offset(centerX, centerY),
          width: crossSize,
          height: crossThickness,
        ),
        const Radius.circular(2),
      ),
      crossPaint,
    );

    // Draw small stars (white/cream)
    final starPaint = Paint()
      ..color = AppColors.creamYellow
      ..style = PaintingStyle.fill;

    const starSize = 4.0;
    _drawStar(canvas, Offset(centerX - width * 0.2, centerY - height * 0.15), starSize, starPaint);
    _drawStar(canvas, Offset(centerX + width * 0.2, centerY - height * 0.1), starSize * 0.8, starPaint);
    _drawStar(canvas, Offset(centerX - width * 0.15, centerY + height * 0.25), starSize * 0.8, starPaint);
  }

  void _drawStar(Canvas canvas, Offset center, double size, Paint paint) {
    final path = Path();
    final outerRadius = size;
    final innerRadius = size * 0.4;
    
    for (int i = 0; i < 5; i++) {
      final angle = (i * 4 * math.pi / 5) - math.pi / 2;
      final x = center.dx + outerRadius * math.cos(angle);
      final y = center.dy + outerRadius * math.sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
      
      final innerAngle = angle + (2 * math.pi / 5);
      final innerX = center.dx + innerRadius * math.cos(innerAngle);
      final innerY = center.dy + innerRadius * math.sin(innerAngle);
      path.lineTo(innerX, innerY);
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}