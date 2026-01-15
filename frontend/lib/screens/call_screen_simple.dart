import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import '../providers/call_provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';

/// Voice call screen with AI chatbot integration
/// Uses Speech-to-Text for user input and Text-to-Speech for bot responses
class CallScreenSimple extends StatefulWidget {
  final String callId;
  final String callType;
  final String? calleeName;

  const CallScreenSimple({
    super.key,
    required this.callId,
    required this.callType,
    this.calleeName,
  });

  @override
  State<CallScreenSimple> createState() => _CallScreenSimpleState();
}

class _CallScreenSimpleState extends State<CallScreenSimple> {
  bool _isMuted = false;
  bool _isSpeakerEnabled = true;
  bool _isListening = false;
  bool _isBotSpeaking = false;
  String _currentText = '';
  String _botResponse = '';
  
  // Language settings
  String _selectedLanguage = 'en'; // 'en', 'si', 'ta'
  String _sttLocale = 'en_US';
  String _ttsLanguage = 'en-US';
  
  // Speech recognition
  late stt.SpeechToText _speech;
  bool _speechAvailable = false;
  List<stt.LocaleName> _availableLocales = [];
  
  // Text to speech
  late FlutterTts _flutterTts;
  
  // API service for chatbot
  final ApiService _apiService = ApiService();
  
  // Conversation history for context
  final List<Map<String, String>> _conversationHistory = [];
  
  // Greetings in different languages
  final Map<String, String> _greetings = {
    'en': "Hello friend! I'm here to listen and support you. How are you feeling today?",
    'si': "ආයුබෝවන් මිත්‍රයා! මම ඔබට සවන් දීමට සහ සහාය වීමට මෙහි සිටිමි. අද ඔබට කොහොමද?",
    'ta': "வணக்கம் நண்பரே! நான் உங்களுக்கு செவிசாய்க்கவும் ஆதரவளிக்கவும் இங்கே இருக்கிறேன். இன்று நீங்கள் எப்படி உணர்கிறீர்கள்?",
  };

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();
    
    // Sync token from auth provider
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _syncToken();
      // Start the conversation with bot greeting
      _startConversation();
    });
  }

  void _syncToken() {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    if (authProvider.token != null) {
      _apiService.setToken(authProvider.token);
    }
    
    // Get language from CallProvider (set from home screen)
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    _setLanguage(callProvider.language);
  }

  Future<void> _initSpeech() async {
    _speech = stt.SpeechToText();
    _speechAvailable = await _speech.initialize(
      onStatus: (status) {
        debugPrint('Speech status: $status');
        if (status == 'done' || status == 'notListening') {
          setState(() => _isListening = false);
          // Process the recognized text
          if (_currentText.isNotEmpty && !_isBotSpeaking) {
            _sendToChatbot(_currentText);
          }
        }
      },
      onError: (error) {
        debugPrint('Speech error: $error');
        setState(() => _isListening = false);
      },
    );
    
    // Get available locales for language selection
    if (_speechAvailable) {
      _availableLocales = await _speech.locales();
      debugPrint('Available locales: ${_availableLocales.map((l) => l.localeId).toList()}');
    }
    setState(() {});
  }
  
  void _setLanguage(String langCode) {
    setState(() {
      _selectedLanguage = langCode;
      switch (langCode) {
        case 'si':
          _sttLocale = 'si_LK'; // Sinhala
          _ttsLanguage = 'si-LK';
          break;
        case 'ta':
          _sttLocale = 'ta_IN'; // Tamil
          _ttsLanguage = 'ta-IN';
          break;
        default:
          _sttLocale = 'en_US';
          _ttsLanguage = 'en-US';
      }
    });
    _flutterTts.setLanguage(_ttsLanguage);
  }

  Future<void> _initTts() async {
    _flutterTts = FlutterTts();
    
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.setVolume(1.0);
    await _flutterTts.setPitch(1.0);
    
    _flutterTts.setStartHandler(() {
      setState(() => _isBotSpeaking = true);
    });
    
    _flutterTts.setCompletionHandler(() {
      setState(() => _isBotSpeaking = false);
      // Auto-start listening after bot finishes speaking
      if (!_isMuted && _speechAvailable) {
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted && !_isBotSpeaking) {
            _startListening();
          }
        });
      }
    });
    
    _flutterTts.setErrorHandler((msg) {
      debugPrint('TTS Error: $msg');
      setState(() => _isBotSpeaking = false);
    });
  }

  Future<void> _startConversation() async {
    // Wait a moment for the call to be established
    await Future.delayed(const Duration(seconds: 1));
    
    // Bot greeting in selected language
    final greeting = _greetings[_selectedLanguage] ?? _greetings['en']!;
    _botResponse = greeting;
    _conversationHistory.add({'role': 'assistant', 'content': greeting});
    
    setState(() {});
    await _speak(greeting);
  }

  Future<void> _speak(String text) async {
    if (text.isEmpty) return;
    
    setState(() {
      _isBotSpeaking = true;
      _botResponse = text;
    });
    
    await _flutterTts.speak(text);
  }

  Future<void> _stopSpeaking() async {
    await _flutterTts.stop();
    setState(() => _isBotSpeaking = false);
  }

  void _startListening() {
    if (!_speechAvailable || _isListening || _isMuted || _isBotSpeaking) return;
    
    setState(() {
      _isListening = true;
      _currentText = '';
    });
    
    _speech.listen(
      onResult: (result) {
        setState(() {
          _currentText = result.recognizedWords;
        });
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      partialResults: true,
      localeId: _sttLocale,
    );
  }

  void _stopListening() {
    if (!_isListening) return;
    _speech.stop();
    setState(() => _isListening = false);
  }

  Future<void> _sendToChatbot(String userMessage) async {
    if (userMessage.trim().isEmpty) return;
    
    // Add user message to history
    _conversationHistory.add({'role': 'user', 'content': userMessage});
    
    setState(() {
      _currentText = '';
    });
    
    try {
      // Send to chatbot API with language (don't send callId as sessionId - it's not a chat session)
      final response = await _apiService.sendChatMessage(
        userMessage,
        language: _selectedLanguage == 'si' ? 'sinhala' : _selectedLanguage == 'ta' ? 'tamil' : 'english',
      );
      
      final botMessage = response['response'] ?? response['message'] ?? _getDefaultResponse();
      
      // Add bot response to history
      _conversationHistory.add({'role': 'assistant', 'content': botMessage});
      
      // Speak the response
      await _speak(botMessage);
      
    } catch (e) {
      debugPrint('Chatbot error: $e');
      await _speak(_getErrorMessage());
    }
  }
  
  String _getDefaultResponse() {
    switch (_selectedLanguage) {
      case 'si':
        return "මම තේරුම් ගත්තා. කරුණාකර තවත් කියන්න.";
      case 'ta':
        return "நான் புரிந்துகொண்டேன். தயவுசெய்து மேலும் சொல்லுங்கள்.";
      default:
        return "I understand. Please tell me more.";
    }
  }
  
  String _getErrorMessage() {
    switch (_selectedLanguage) {
      case 'si':
        return "සමාවෙන්න, මට තේරුම් ගැනීමට අපහසු විය. කරුණාකර නැවත කියන්න.";
      case 'ta':
        return "மன்னிக்கவும், புரிந்துகொள்வதில் சிரமம் ஏற்பட்டது. தயவுசெய்து மீண்டும் சொல்லுங்கள்.";
      default:
        return "I'm sorry, I had trouble understanding. Could you please repeat that?";
    }
  }

  void _toggleMute() {
    setState(() {
      _isMuted = !_isMuted;
    });
    
    if (_isMuted) {
      _stopListening();
    }
  }

  void _toggleSpeaker() {
    setState(() {
      _isSpeakerEnabled = !_isSpeakerEnabled;
    });
    
    // Adjust TTS volume
    _flutterTts.setVolume(_isSpeakerEnabled ? 1.0 : 0.0);
  }

  String _getCallTypeLabel() {
    switch (widget.callType) {
      case 'counselor':
        return 'Counselor Call';
      case 'ai_practice':
        return 'AI Support Call';
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
    return widget.callType == 'ai_practice' ? 'Sahana' : 'Counselor';
  }

  @override
  void dispose() {
    _speech.stop();
    _flutterTts.stop();
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
                  const SizedBox(width: 48),
                ],
              ),
            ),

            // Call view with avatar and status
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Avatar with speaking indicator
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      // Pulsing circle when bot is speaking
                      if (_isBotSpeaking)
                        TweenAnimationBuilder<double>(
                          tween: Tween(begin: 1.0, end: 1.2),
                          duration: const Duration(milliseconds: 600),
                          builder: (context, value, child) {
                            return Container(
                              width: 200 * value,
                              height: 200 * value,
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.3),
                                shape: BoxShape.circle,
                              ),
                            );
                          },
                        ),
                      Container(
                        width: 180,
                        height: 180,
                        decoration: BoxDecoration(
                          color: _isBotSpeaking ? Colors.green[700] : Colors.grey[700],
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: _isBotSpeaking ? Colors.green : Colors.grey,
                            width: 3,
                          ),
                        ),
                        child: Center(
                          child: Icon(
                            _isBotSpeaking ? Icons.record_voice_over : Icons.person,
                            size: 80,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Caller name
                  Text(
                    _getCallerName(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // Status indicator
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _isBotSpeaking 
                          ? Colors.green.withOpacity(0.3)
                          : _isListening 
                              ? Colors.blue.withOpacity(0.3)
                              : Colors.grey.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _isBotSpeaking 
                              ? Icons.volume_up
                              : _isListening 
                                  ? Icons.mic
                                  : Icons.call,
                          color: _isBotSpeaking 
                              ? Colors.green
                              : _isListening 
                                  ? Colors.blue
                                  : Colors.white70,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _isBotSpeaking 
                              ? 'Speaking...'
                              : _isListening 
                                  ? 'Listening...'
                                  : callProvider.callStatus == CallStatus.connected
                                      ? 'Connected'
                                      : 'Connecting...',
                          style: TextStyle(
                            color: _isBotSpeaking 
                                ? Colors.green
                                : _isListening 
                                    ? Colors.blue
                                    : Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Current speech/response display
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Container(
                      constraints: const BoxConstraints(maxHeight: 150),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[900],
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _isListening ? Colors.blue : Colors.grey[700]!,
                          width: 1,
                        ),
                      ),
                      child: SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (_botResponse.isNotEmpty) ...[
                              Row(
                                children: [
                                  Icon(Icons.smart_toy, color: Colors.green[400], size: 16),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Sahana:',
                                    style: TextStyle(
                                      color: Colors.green[400],
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                _botResponse,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                ),
                              ),
                            ],
                            if (_currentText.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  Icon(Icons.person, color: Colors.blue[400], size: 16),
                                  const SizedBox(width: 8),
                                  Text(
                                    'You:',
                                    style: TextStyle(
                                      color: Colors.blue[400],
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                _currentText,
                                style: const TextStyle(
                                  color: Colors.white70,
                                  fontSize: 14,
                                  fontStyle: FontStyle.italic,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                  
                  if (!_speechAvailable && !kIsWeb) ...[
                    const SizedBox(height: 16),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 24),
                      child: Text(
                        'Speech recognition not available on this device',
                        style: TextStyle(color: Colors.orange, fontSize: 12),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ],
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
                    color: _isMuted ? Colors.red : (_isListening ? Colors.blue : Colors.white),
                    label: _isMuted ? 'Unmute' : (_isListening ? 'Listening' : 'Muted'),
                    onPressed: _toggleMute,
                  ),

                  // Manual listen button (tap to speak)
                  _buildControlButton(
                    icon: Icons.touch_app,
                    color: _isListening ? Colors.blue : Colors.white,
                    label: 'Tap to Speak',
                    size: 56,
                    onPressed: () {
                      if (_isBotSpeaking) {
                        _stopSpeaking();
                      }
                      if (_isListening) {
                        _stopListening();
                      } else if (!_isMuted) {
                        _startListening();
                      }
                    },
                  ),

                  // Speaker button
                  _buildControlButton(
                    icon: _isSpeakerEnabled ? Icons.volume_up : Icons.volume_off,
                    color: _isSpeakerEnabled ? Colors.green : Colors.white,
                    label: _isSpeakerEnabled ? 'Speaker On' : 'Speaker Off',
                    onPressed: _toggleSpeaker,
                  ),
                ],
              ),
            ),
            
            // End call button
            Padding(
              padding: const EdgeInsets.only(bottom: 32),
              child: _buildControlButton(
                icon: Icons.call_end,
                color: Colors.red,
                label: 'End Call',
                size: 64,
                onPressed: () async {
                  await _stopSpeaking();
                  _stopListening();
                  await callProvider.endCall();
                  if (mounted) {
                    Navigator.pop(context);
                  }
                },
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
    String? label,
    double size = 48,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            shape: BoxShape.circle,
            border: Border.all(color: color.withOpacity(0.5), width: 2),
          ),
          child: IconButton(
            icon: Icon(icon, color: color, size: size * 0.5),
            onPressed: onPressed,
            padding: EdgeInsets.zero,
          ),
        ),
        if (label != null) ...[
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 10,
            ),
          ),
        ],
      ],
    );
  }
}
