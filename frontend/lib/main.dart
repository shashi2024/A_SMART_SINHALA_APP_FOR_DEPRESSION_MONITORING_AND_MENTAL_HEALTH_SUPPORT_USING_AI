import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/signup_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/voice_call_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/calls_home_screen.dart';
import 'screens/welcome_chat_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'providers/auth_provider.dart';
import 'providers/chatbot_provider.dart';
import 'providers/sensor_provider.dart';
import 'providers/voice_provider.dart';
import 'providers/call_provider.dart';
import 'providers/digital_twin_provider.dart';
import 'services/api_service.dart';
import 'services/sensor_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatbotProvider()),
        ChangeNotifierProvider(create: (_) => SensorProvider()),
        ChangeNotifierProvider(create: (_) => VoiceProvider()),
        ChangeNotifierProvider(create: (_) => CallProvider()),
        ChangeNotifierProvider(create: (_) => DigitalTwinProvider()),
      ],
      child: MaterialApp(
        title: 'Depression Monitoring App',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const AuthWrapper(),
        routes: {
          '/login': (context) => const LoginScreen(),
          '/signup': (context) => const SignUpScreen(),
          '/home': (context) => const HomeScreen(),
          '/chat': (context) => const ChatScreen(),
          '/voice': (context) => const VoiceCallScreen(),
          '/profile': (context) => const ProfileScreen(),
          '/calls': (context) => const CallsHomeScreen(),
          '/welcome': (context) => const WelcomeChatScreen(),
        },
      ),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isCheckingFirstTime = true;
  bool _isFirstTime = false;

  @override
  void initState() {
    super.initState();
    _checkFirstTime();
  }

  Future<void> _checkFirstTime() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final hasSeenWelcome = prefs.getBool('has_seen_welcome') ?? false;
      
      setState(() {
        _isFirstTime = !hasSeenWelcome;
        _isCheckingFirstTime = false;
      });
    } catch (e) {
      // If error, assume not first time
      setState(() {
        _isFirstTime = false;
        _isCheckingFirstTime = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isCheckingFirstTime) {
      // Show loading while checking
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        // Sync token to CallProvider when authenticated
        if (authProvider.isAuthenticated && authProvider.token != null) {
          final callProvider = Provider.of<CallProvider>(context, listen: false);
          callProvider.setToken(authProvider.token);
        }
        
        // First-time user: Show welcome chat screen
        if (_isFirstTime && !authProvider.isAuthenticated) {
          return const WelcomeChatScreen();
        }
        
        // Returning user: Show login if not authenticated
        if (!authProvider.isAuthenticated) {
          return const LoginScreen();
        }
        
        // Authenticated user: Show home screen
        return const HomeScreen();
      },
    );
  }
}

