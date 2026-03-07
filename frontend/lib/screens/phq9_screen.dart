import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../providers/auth_provider.dart';
import '../providers/language_provider.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';

class PHQ9Screen extends StatefulWidget {
  @override
  _PHQ9ScreenState createState() => _PHQ9ScreenState();
}

class _PHQ9ScreenState extends State<PHQ9Screen> {
  bool _isLoading = true;
  String? _sessionId;
  String _currentQuestion = "";
  int _currentQuestionNum = 1;
  bool _isComplete = false;
  Map<String, dynamic>? _result;


  @override
  void initState() {
    super.initState();
    _startPHQ9();
  }

  Future<void> _startPHQ9() async {
    setState(() => _isLoading = true);
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final token = authProvider.token;
      
      // Use language from provider
      final lp = Provider.of<LanguageProvider>(context, listen: false);
      final lang = lp.currentLanguage;

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/chatbot/phq9/start'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'language': lang,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _sessionId = data['session_id'];
          _currentQuestion = data['question'].split('\n\n')[0];
          _currentQuestionNum = data['question_num'];
          _isLoading = false;
        });
      }
    } catch (e) {
      print("Error starting PHQ-9: $e");
      setState(() => _isLoading = false);
    }
  }

  Future<void> _submitAnswer(int score) async {
    if (_sessionId == null) return;
    
    setState(() => _isLoading = true);
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final token = authProvider.token;

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/chatbot/phq9/answer'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'session_id': _sessionId,
          'answer': score.toString(),
          'language': Provider.of<LanguageProvider>(context, listen: false).currentLanguage,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['is_complete']) {
          _fetchResult();
        } else {
          setState(() {
            _currentQuestion = data['question'].split('\n\n')[0];
            _currentQuestionNum = data['question_num'];
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      print("Error submitting answer: $e");
      setState(() => _isLoading = false);
    }
  }

  Future<void> _fetchResult() async {
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final token = authProvider.token;

      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/chatbot/phq9/result/$_sessionId'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          _result = jsonDecode(response.body);
          _isComplete = true;
          _isLoading = false;
        });
      }
    } catch (e) {
      print("Error fetching result: $e");
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();

    if (_isComplete && _result != null) {
      return _buildResultScreen(lp);
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(lp.translate('mental_health_assessment')),
        backgroundColor: const Color(0xFF185846),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  LinearProgressIndicator(
                    value: _currentQuestionNum / 9,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF185846)),
                  ),
                  const SizedBox(height: 32),
                  Text(
                    "${lp.translate('question')} $_currentQuestionNum ${lp.translate('of')} 9",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _currentQuestion,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF185846),
                    ),
                  ),
                  const SizedBox(height: 40),
                  ...List.generate(4, (index) {
                    final options = [
                      'not_at_all',
                      'several_days',
                      'more_than_half',
                      'nearly_every_day'
                    ];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          foregroundColor: const Color(0xFF185846),
                          backgroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: BorderSide(color: const Color(0xFF185846).withOpacity(0.3)),
                          ),
                          elevation: 0,
                        ),
                        onPressed: () => _submitAnswer(index),
                        child: Text(
                          lp.translate(options[index]),
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }

  Widget _buildResultScreen(LanguageProvider lp) {
    final severity = _result!['severity'];
    final score = _result!['score'];
    final recommendation = _result!['recommendation'];

    // Localize severity if it comes from backend as a key
    String localizedSeverity = severity.toString().replaceAll('_', ' ').toUpperCase();
    if (severity is String) {
      localizedSeverity = lp.translate(severity.toLowerCase());
      if (localizedSeverity == severity.toLowerCase()) {
        // Fallback to title case if no translation found
        localizedSeverity = severity.toString().replaceAll('_', ' ').toUpperCase();
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(lp.translate('assessment_result')),
        backgroundColor: const Color(0xFF185846),
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFF185846).withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Text(
                "$score",
                style: const TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF185846),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              "${lp.translate('severity')}: $localizedSeverity",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              recommendation,
              style: TextStyle(fontSize: 16, color: Colors.grey[600], height: 1.5),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF185846),
                padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () => Navigator.pop(context),
              child: Text(lp.translate('finish'), style: const TextStyle(fontSize: 18, color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}
