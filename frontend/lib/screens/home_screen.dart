import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/auth_provider.dart';
import '../providers/call_provider.dart';
import '../services/api_service.dart';
import 'chat_screen.dart';
import 'profile_screen.dart';
import 'notification_screen.dart';
import 'instructions_screen.dart';
import 'login_screen.dart'; // For AppColors and logo

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  String? _selectedMood;
  bool _isSavingMood = false;
  final ApiService _apiService = ApiService();
  final ScrollController _moodScrollController = ScrollController();
  bool _showLeftArrow = false;
  
  // Language settings
  String _selectedLanguage = 'en';
  final Map<String, String> _languageNames = {
    'en': 'English',
    'si': 'සිංහල',
    'ta': 'தமிழ்',
  };

  final List<String> _moods = ['Excited', 'Happy', 'Calm', 'Neutral', 'Anxious', 'Sad'];

  @override
  void dispose() {
    _moodScrollController.dispose();
    super.dispose();
  }

  void _updateArrowVisibility() {
    if (_moodScrollController.hasClients) {
      final currentScroll = _moodScrollController.position.pixels;
      setState(() {
        _showLeftArrow = currentScroll > 0;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    // Set API token from auth provider
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    _apiService.setToken(authProvider.token);
    
    // Listen to scroll changes to update arrow visibility
    _moodScrollController.addListener(_updateArrowVisibility);
    
    // Load saved language preference
    _loadLanguagePreference();
  }
  
  Future<void> _loadLanguagePreference() async {
    final prefs = await SharedPreferences.getInstance();
    final savedLang = prefs.getString('app_language') ?? 'en';
    setState(() {
      _selectedLanguage = savedLang;
    });
    // Update CallProvider language
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    callProvider.setLanguage(savedLang);
  }
  
  Future<void> _setLanguage(String langCode) async {
    setState(() {
      _selectedLanguage = langCode;
    });
    // Save preference
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_language', langCode);
    // Update CallProvider language
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    callProvider.setLanguage(langCode);
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final username = authProvider.user?.username ?? 'User';
    // Extract name from email if username is an email, otherwise use the name part
    String displayName = username;
    if (username.contains('@')) {
      displayName = username.split('@').first;
    } else {
      displayName = username.split(' ').first;
    }
    
    // Update API token if it changed
    _apiService.setToken(authProvider.token);

    return Scaffold(
      backgroundColor: AppColors.creamYellow,
      body: SafeArea(
        child: _selectedIndex == 0
            ? _buildHomeContent(displayName)
            : _buildOtherScreen(),
      ),
      bottomNavigationBar: _buildBottomNavigationBar(),
    );
  }

  Widget _buildHomeContent(String firstName) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with greeting and language selector
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Greeting Section
          Text(
            'Hi $firstName!',
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
              ),
              // Language selector
              PopupMenuButton<String>(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.darkGreen.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.language, color: AppColors.darkGreen, size: 20),
                      const SizedBox(width: 4),
                      Text(
                        _languageNames[_selectedLanguage] ?? 'EN',
                        style: const TextStyle(
                          color: AppColors.darkGreen,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                onSelected: _setLanguage,
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'en',
                    child: Row(
                      children: [
                        Icon(Icons.check, color: _selectedLanguage == 'en' ? Colors.green : Colors.transparent, size: 20),
                        const SizedBox(width: 8),
                        const Text('English'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'si',
                    child: Row(
                      children: [
                        Icon(Icons.check, color: _selectedLanguage == 'si' ? Colors.green : Colors.transparent, size: 20),
                        const SizedBox(width: 8),
                        const Text('සිංහල (Sinhala)'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'ta',
                    child: Row(
                      children: [
                        Icon(Icons.check, color: _selectedLanguage == 'ta' ? Colors.green : Colors.transparent, size: 20),
                        const SizedBox(width: 8),
                        const Text('தமிழ் (Tamil)'),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'How are you feeling today?',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[700],
              fontWeight: FontWeight.w500,
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Mood Selection Buttons with scroll indicator
          Stack(
            children: [
              SizedBox(
                height: 50,
                child: ListView.builder(
                  controller: _moodScrollController,
                  scrollDirection: Axis.horizontal,
                  physics: const BouncingScrollPhysics(),
                  itemCount: _moods.length,
                  itemBuilder: (context, index) {
                    final mood = _moods[index];
                    final isSelected = _selectedMood == mood;
                    return Padding(
                      padding: EdgeInsets.only(
                        left: index == 0 ? 0 : 12.0,
                        right: index == _moods.length - 1 ? 40.0 : 12.0,
                      ),
                      child: ElevatedButton(
                        onPressed: _isSavingMood ? null : () async {
                          final newMood = isSelected ? null : mood;
                          setState(() {
                            _selectedMood = newMood;
                          });
                          
                          // Save mood to database if a mood is selected
                          if (newMood != null) {
                            await _saveMoodCheckIn(newMood);
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isSelected 
                              ? AppColors.darkGreen 
                              : Colors.white,
                          foregroundColor: isSelected 
                              ? Colors.white 
                              : Colors.black87,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(25),
                          ),
                          elevation: isSelected ? 2 : 0,
                        ),
                        child: Text(mood),
                      ),
                    );
                  },
                ),
              ),
              // Scroll indicator arrow on the left (clickable) - only show when scrolled right
              if (_showLeftArrow)
                Positioned(
                  left: 0,
                  top: 0,
                  bottom: 0,
                  child: GestureDetector(
                    onTap: () {
                      // Scroll to the left if we can
                      if (_moodScrollController.hasClients) {
                        final currentScroll = _moodScrollController.position.pixels;
                        
                        if (currentScroll > 0) {
                          // Calculate scroll amount (150px back or to the start, whichever is larger)
                          final scrollAmount = (currentScroll - 150).clamp(0.0, double.infinity);
                          _moodScrollController.animateTo(
                            scrollAmount,
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeInOut,
                          );
                        }
                      }
                    },
                    child: Container(
                      width: 40,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                          colors: [
                            AppColors.creamYellow,
                            AppColors.creamYellow.withOpacity(0.8),
                            AppColors.creamYellow.withOpacity(0.0),
                          ],
                        ),
                      ),
                      child: Icon(
                        Icons.chevron_left,
                        color: Colors.grey[700],
                        size: 28,
                      ),
                    ),
                  ),
                ),
              // Scroll indicator arrow on the right (clickable)
              Positioned(
                right: 0,
                top: 0,
                bottom: 0,
                child: GestureDetector(
                  onTap: () {
                    // Scroll to the right if we can
                    if (_moodScrollController.hasClients) {
                      final maxScroll = _moodScrollController.position.maxScrollExtent;
                      final currentScroll = _moodScrollController.position.pixels;
                      
                      if (currentScroll < maxScroll) {
                        // Calculate scroll amount (150px or to the end, whichever is smaller)
                        final scrollAmount = (currentScroll + 150).clamp(0.0, maxScroll);
                        _moodScrollController.animateTo(
                          scrollAmount,
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      }
                    }
                  },
                  child: Container(
                    width: 40,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                        colors: [
                          AppColors.creamYellow.withOpacity(0.0),
                          AppColors.creamYellow.withOpacity(0.8),
                          AppColors.creamYellow,
                        ],
                      ),
                    ),
                    child: Icon(
                      Icons.chevron_right,
                      color: Colors.grey[700],
                      size: 28,
                    ),
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 32),
          
          // "I'm Finn." Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24.0),
            decoration: BoxDecoration(
              color: AppColors.darkGreen,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'I\'m Sahana.',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Lets get started with a quick mood check.',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    // Navigate to chat or mood check
                    setState(() {
                      _selectedIndex = 2; // Chatbot index
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: AppColors.darkGreen,
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'Check in',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // "Feeling Lonely ?" Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20.0),
            decoration: BoxDecoration(
              color: AppColors.paleSageGreen,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                // Logo/Icon
                SizedBox(
                  width: 60,
                  height: 60,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      CustomPaint(
                        size: const Size(50, 50),
                        painter: LogoPainter(),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Feeling Lonely ?',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Hi, I\'m Sahana',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[700],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Energy Trend Section
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'This week\'s energy trend:',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[700],
                    ),
                  ),
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Text(
                'Steady',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 100,
                      decoration: BoxDecoration(
                        color: AppColors.paleSageGreen,
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Container(
                      height: 100,
                      decoration: BoxDecoration(
                        color: AppColors.lightPeach,
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildOtherScreen() {
    if (_selectedIndex == 1) {
      // Instructions screen
      return const InstructionsScreen();
    } else if (_selectedIndex == 2) {
      // Chatbot screen - navigate to chat route
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pushNamed('/chat');
        setState(() {
          _selectedIndex = 0; // Reset to home after navigation
        });
      });
      final username = Provider.of<AuthProvider>(context).user?.username ?? 'User';
      String displayName = username;
      if (username.contains('@')) {
        displayName = username.split('@').first;
      } else {
        displayName = username.split(' ').first;
      }
      return _buildHomeContent(displayName);
    } else if (_selectedIndex == 3) {
      // Notifications screen
      return const NotificationScreen();
    } else if (_selectedIndex == 4) {
      // Profile screen
      return const ProfileScreen();
    }
    return const SizedBox();
  }

  Widget _buildBottomNavigationBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 5,
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              // Home
              _buildNavItem(Icons.home, 0, 'Home'),
              // Instructions
              _buildNavItem(Icons.menu_book, 1, 'Instructions'),
              // Chatbot (bigger centered icon)
              _buildChatbotNavItem(),
              // Notifications
              _buildNavItem(Icons.notifications_outlined, 3, 'Notifications'),
              // Profile
              _buildNavItem(Icons.person_outline, 4, 'Profile'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, int index, String label) {
    final isSelected = _selectedIndex == index;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedIndex = index;
        });
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isSelected ? AppColors.darkGreen : Colors.grey[600],
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: isSelected ? AppColors.darkGreen : Colors.grey[600],
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatbotNavItem() {
    final isSelected = _selectedIndex == 2;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedIndex = 2;
        });
      },
      child: Container(
        width: 56,
        height: 56,
        decoration: BoxDecoration(
          color: AppColors.lightPeach,
          shape: BoxShape.circle,
          border: Border.all(
            color: isSelected ? AppColors.darkGreen : Colors.transparent,
            width: 3,
          ),
        ),
        child: Center(
          child: CustomPaint(
            size: const Size(30, 30),
            painter: LogoPainter(),
          ),
        ),
      ),
    );
  }

  Future<void> _saveMoodCheckIn(String mood) async {
    if (!mounted) return;
    
    setState(() {
      _isSavingMood = true;
    });

    try {
      await _apiService.createMoodCheckIn(mood);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Mood "$mood" saved successfully!'),
            backgroundColor: AppColors.darkGreen,
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save mood: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSavingMood = false;
        });
      }
    }
  }
}

// Logo painter (reused from login screen)
class LogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final centerX = width / 2;
    final centerY = height / 2;

    // Draw heart shape (pink/purple)
    final heartPaint = Paint()
      ..color = const Color(0xFFE91E63)
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

    // Draw medical cross (green)
    final crossPaint = Paint()
      ..color = AppColors.darkGreen
      ..style = PaintingStyle.fill;

    final crossSize = width * 0.25;
    final crossThickness = width * 0.08;
    
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
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
