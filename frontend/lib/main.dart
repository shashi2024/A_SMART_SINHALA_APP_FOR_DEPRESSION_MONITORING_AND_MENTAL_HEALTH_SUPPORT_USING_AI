import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/voice_call_screen.dart';
import 'screens/profile_screen.dart';
import 'providers/auth_provider.dart';
import 'providers/chatbot_provider.dart';
import 'providers/sensor_provider.dart';
import 'services/api_service.dart';
import 'services/sensor_service.dart';

void main() {
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
      ],
      child: MaterialApp(
        title: 'Depression Monitoring App',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const HomeScreen(),
        routes: {
          '/chat': (context) => const ChatScreen(),
          '/voice': (context) => const VoiceCallScreen(),
          '/profile': (context) => const ProfileScreen(),
        },
      ),
    );
  }
}

