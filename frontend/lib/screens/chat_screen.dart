import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chatbot_provider.dart';
import '../providers/auth_provider.dart';
import '../providers/sensor_provider.dart';
import '../services/typing_analyzer.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final TypingAnalyzer _typingAnalyzer = TypingAnalyzer();

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
    _scrollController.animateTo(
      _scrollController.position.maxScrollExtent,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  void _showLanguageSelector(BuildContext context) async {
    final chatbotProvider = Provider.of<ChatbotProvider>(context, listen: false);
    
    final selectedLanguage = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('English'),
              value: 'en',
              groupValue: chatbotProvider.selectedLanguage,
              onChanged: (value) => Navigator.pop(context, value),
            ),
            RadioListTile<String>(
              title: const Text('සිංහල (Sinhala)'),
              value: 'si',
              groupValue: chatbotProvider.selectedLanguage,
              onChanged: (value) => Navigator.pop(context, value),
            ),
            RadioListTile<String>(
              title: const Text('தமிழ் (Tamil)'),
              value: 'ta',
              groupValue: chatbotProvider.selectedLanguage,
              onChanged: (value) => Navigator.pop(context, value),
            ),
          ],
        ),
      ),
    );

    if (selectedLanguage != null) {
      await chatbotProvider.setLanguage(selectedLanguage);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat with AI Assistant'),
        actions: [
          Consumer<ChatbotProvider>(
            builder: (context, provider, child) {
              return PopupMenuButton<String>(
                icon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.language),
                    const SizedBox(width: 4),
                    Text(
                      provider.selectedLanguage == 'si'
                          ? 'සිංහල'
                          : provider.selectedLanguage == 'ta'
                              ? 'தமிழ்'
                              : 'EN',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
                onSelected: (language) async {
                  await provider.setLanguage(language);
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'en',
                    child: Text('English'),
                  ),
                  const PopupMenuItem(
                    value: 'si',
                    child: Text('සිංහල (Sinhala)'),
                  ),
                  const PopupMenuItem(
                    value: 'ta',
                    child: Text('தமிழ் (Tamil)'),
                  ),
                ],
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<ChatbotProvider>(
              builder: (context, provider, child) {
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
                        margin: const EdgeInsets.only(bottom: 8.0),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16.0,
                          vertical: 10.0,
                        ),
                        decoration: BoxDecoration(
                          color: message.isUser
                              ? Colors.blue
                              : Colors.grey[300],
                          borderRadius: BorderRadius.circular(20.0),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              message.text,
                              style: TextStyle(
                                color: message.isUser
                                    ? Colors.white
                                    : Colors.black,
                              ),
                            ),
                            if (message.depressionScore != null)
                              Padding(
                                padding: const EdgeInsets.only(top: 4.0),
                                child: Text(
                                  'Risk: ${message.riskLevel}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: message.isUser
                                        ? Colors.white70
                                        : Colors.black54,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8.0),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.3),
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
                      hintText: 'Type your message...',
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16.0,
                        vertical: 10.0,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

