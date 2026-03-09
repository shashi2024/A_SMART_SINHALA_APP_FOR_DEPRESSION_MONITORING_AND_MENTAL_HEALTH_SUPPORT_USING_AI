import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/auth_provider.dart';
import '../providers/call_provider.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';
import 'chat_screen.dart';
import 'profile_screen.dart';
import 'notification_screen.dart';
import 'instructions_screen.dart';
import 'login_screen.dart'; // For AppColors and logo
import '../providers/language_provider.dart';

import '../services/permission_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  String? _selectedMood;
  bool _isSavingMood = false;
  late ApiService _apiService;
  final LocationService _locationService = LocationService();
  final ScrollController _moodScrollController = ScrollController();
  bool _showLeftArrow = false;
  
  // Language settings
  String _selectedLanguage = 'en';
  final Map<String, String> _languageNames = {
    'en': 'English',
    'si': 'සිංහල',
    'ta': 'தமிழ்',
  };

  final List<String> _moodKeys = ['excited', 'happy', 'calm', 'neutral', 'anxious', 'sad'];

  @override
  void dispose() {
    _moodScrollController.dispose();
    _locationService.stopTracking();
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
    _apiService = ApiService();
    
    // Set API token from auth provider
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    _apiService.setToken(authProvider.token);
    
    // Listen to scroll changes to update arrow visibility
    _moodScrollController.addListener(_updateArrowVisibility);
    
    // Load saved language preference
    _loadLanguagePreference();
    
    // Request permissions and initialize location tracking after widget is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final permissionService = Provider.of<PermissionService>(context, listen: false);
      permissionService.requestAllPermissions();
      _initializeLocationTracking();
    });
  }
  
  Future<void> _initializeLocationTracking() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    // Wait a bit for user data to be fully loaded
    await Future.delayed(const Duration(seconds: 2));
    
    final user = authProvider.user;
    final phoneNumber = user?.phoneNumber;
    
    if (phoneNumber != null && phoneNumber.isNotEmpty) {
      print('Initializing location tracking for: $phoneNumber');
      try {
        await _locationService.startTracking(phoneNumber: phoneNumber);
        print('SUCCESS: Location tracking started for: $phoneNumber');
      } catch (e) {
        print('FAILURE: Error starting location tracking for $phoneNumber: $e');
      }
    } else {
      print('WARNING: Phone number not found in user profile. authProvider.user is ${authProvider.user != null ? 'present' : 'null'}. Username is ${authProvider.user?.username ?? 'null'}.');
    }
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
    final languageProvider = Provider.of<LanguageProvider>(context, listen: false);
    await languageProvider.setLanguage(langCode);
    
    // Update CallProvider language
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    callProvider.setLanguage(langCode);
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final languageProvider = Provider.of<LanguageProvider>(context);
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
            ? _buildHomeContent(displayName, languageProvider)
            : _buildOtherScreen(languageProvider),
      ),
      bottomNavigationBar: _buildBottomNavigationBar(languageProvider),
    );
  }

  Widget _buildHomeContent(String firstName, LanguageProvider lp) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with greeting and language selector
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting Section
          Expanded(
            child: Text(
              '${lp.translate('hi')} $firstName!',
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
          ),
          const SizedBox(width: 8),
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
                        _languageNames[lp.currentLanguage] ?? 'EN',
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
                        Icon(Icons.check, color: lp.currentLanguage == 'en' ? Colors.green : Colors.transparent, size: 20),
                        const SizedBox(width: 8),
                        const Text('English'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'si',
                    child: Row(
                      children: [
                        Icon(Icons.check, color: lp.currentLanguage == 'si' ? Colors.green : Colors.transparent, size: 20),
                        const SizedBox(width: 8),
                        const Text('සිංහල (Sinhala)'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'ta',
                    child: Row(
                      children: [
                        Icon(Icons.check, color: lp.currentLanguage == 'ta' ? Colors.green : Colors.transparent, size: 20),
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
            lp.translate('feeling_today'),
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
                  itemCount: _moodKeys.length,
                  itemBuilder: (context, index) {
                    final moodKey = _moodKeys[index];
                    final moodName = lp.translate(moodKey);
                    final isSelected = _selectedMood == moodKey;
                    return Padding(
                      padding: EdgeInsets.only(
                        left: index == 0 ? 0 : 12.0,
                        right: index == _moodKeys.length - 1 ? 40.0 : 12.0,
                      ),
                      child: ElevatedButton(
                        onPressed: _isSavingMood ? null : () async {
                          final newMood = isSelected ? null : moodKey;
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
                        child: Text(moodName),
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
                Text(
                  lp.translate('hi_im_sahana'),
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  lp.translate('sahana_start'),
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
                  child: Text(
                    lp.translate('check_in'),
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
                      Image.asset(
                        'assets/images/logo.png',
                        width: 50,
                        height: 50,
                        fit: BoxFit.contain,
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
                        lp.translate('feeling_lonely'),
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        lp.translate('hi_im_sahana'),
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
          
          const SizedBox(height: 20),

          // Bio-Feedback Assessment Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20.0),
            decoration: BoxDecoration(
              color: AppColors.lightPeach,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.darkGreen.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.bolt, color: AppColors.darkGreen, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        lp.translate('bio_feedback_test'),
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  lp.translate('bio_feedback_desc'),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, '/bio-feedback');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.darkGreen,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(lp.translate('start_assessment')),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),

          // PHQ-9 Mental Health Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.darkGreen.withOpacity(0.3)),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.psychology, color: AppColors.darkGreen, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        lp.translate('mental_health_assessment'),
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  lp.translate('phq9_desc'),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, '/phq9');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.darkGreen,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(lp.translate('start_phq9')),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Keystroke Diagnostic Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20.0),
            decoration: BoxDecoration(
              color: AppColors.paleSageGreen.withOpacity(0.5),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.darkGreen.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.keyboard, color: AppColors.darkGreen, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        lp.translate('typing_rhythm_test'),
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  lp.translate('typing_rhythm_desc'),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, '/keystroke');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.darkGreen,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(lp.translate('start_typing')),
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
                  Expanded(
                    child: Text(
                      lp.translate('energy_trend'),
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[700],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
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
              Text(
                lp.translate('steady'),
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

  Widget _buildOtherScreen(LanguageProvider lp) {
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
      return _buildHomeContent(displayName, lp);
    } else if (_selectedIndex == 3) {
      // Notifications screen
      return const NotificationScreen();
    } else if (_selectedIndex == 4) {
      // Profile screen
      return const ProfileScreen();
    }
    return const SizedBox();
  }

  Widget _buildBottomNavigationBar(LanguageProvider lp) {
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
              _buildNavItem(Icons.home, 0, lp.translate('home')),
              // Instructions
              _buildNavItem(Icons.menu_book, 1, lp.translate('instructions')),
              // Chatbot (bigger centered icon)
              _buildChatbotNavItem(),
              // Notifications
              _buildNavItem(Icons.notifications_outlined, 3, lp.translate('notifications')),
              // Profile
              _buildNavItem(Icons.person_outline, 4, lp.translate('profile')),
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
          child: Image.asset(
            'assets/images/logo.png',
            width: 30,
            height: 30,
            fit: BoxFit.contain,
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

