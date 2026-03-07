import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/language_provider.dart';
import '../services/api_service.dart';
import '../services/typing_analyzer.dart';

class KeystrokeDiagnosticScreen extends StatefulWidget {
  @override
  _KeystrokeDiagnosticScreenState createState() => _KeystrokeDiagnosticScreenState();
}

class _KeystrokeDiagnosticScreenState extends State<KeystrokeDiagnosticScreen> {
  final TextEditingController _controller = TextEditingController();
  final TypingAnalyzer _analyzer = TypingAnalyzer();
  final Map<String, double> _pressTimes = {};
  
  bool _isLoading = false;
  String? _result;
  
  final String _targetText = "The quick brown fox jumps over the lazy dog. Mental health is just as important as physical health, and talking about it is the first step towards feeling better.";

  void _handleKeyEvent(KeyEvent event) {
    // Current time in seconds since epoch
    final double now = DateTime.now().millisecondsSinceEpoch / 1000.0;
    final String keyLabel = event.logicalKey.debugName ?? 'unknown';
    final bool isBackspace = event.logicalKey == LogicalKeyboardKey.backspace;

    if (event is KeyDownEvent) {
      _pressTimes[keyLabel] = now;
    } else if (event is KeyUpEvent) {
      if (_pressTimes.containsKey(keyLabel)) {
        _analyzer.recordKeystrokeWithDetails(keyLabel, isBackspace: isBackspace);
        _pressTimes.remove(keyLabel);
      }
    }
  }

  Future<void> _submitData() async {
    final analysis = await _analyzer.getAnalysis();
    if ((analysis['keystroke_events'] as List).isEmpty) {
      final lp = Provider.of<LanguageProvider>(context, listen: false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(lp.translate('please_type_something'))),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final token = authProvider.token;

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/typing/analyze'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'keystroke_timings': analysis['keystroke_timings'],
          'typing_speed': analysis['typing_speed'],
          'pause_duration': analysis['pause_duration'],
          'error_rate': analysis['error_rate'],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        setState(() {
          _result = "${lp.translate('stress_level')}: ${data['risk_level'].toString().toUpperCase()}\n\n${lp.translate('typing_speed')}: ${analysis['typing_speed']?.toStringAsFixed(2)} cpm";
          _isLoading = false;
        });
      } else {
        throw Exception("Failed to analyze keystroke data");
      }
    } catch (e) {
      print("Error submitting keystroke data: $e");
      final lp = Provider.of<LanguageProvider>(context, listen: false);
      setState(() {
        _isLoading = false;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(lp.translate('error_analyze_typing'))),
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();

    if (_result != null) {
      return _buildResultScreen(lp);
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(lp.translate('typing_diagnostic')),
        backgroundColor: Color(0xFF185846),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              lp.translate('typing_pattern_test'),
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF185846)),
            ),
            SizedBox(height: 12),
            Text(
              lp.translate('typing_instruction'),
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
            ),
            SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Text(
                lp.translate('target_text'),
                style: const TextStyle(fontSize: 16, height: 1.5, fontStyle: FontStyle.italic),
              ),
            ),
            const SizedBox(height: 24),
            KeyboardListener(
              focusNode: FocusNode(),
              onKeyEvent: _handleKeyEvent,
              child: TextField(
                controller: _controller,
                maxLines: 5,
                decoration: InputDecoration(
                  hintText: lp.translate('start_typing_here'),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF185846), width: 2),
                  ),
                ),
              ),
            ),
            SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFF185846),
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: _isLoading ? null : _submitData,
              child: _isLoading 
                ? CircularProgressIndicator(color: Colors.white) 
                : Text(lp.translate('submit_analysis'), style: TextStyle(fontSize: 18, color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultScreen(LanguageProvider lp) {
    return Scaffold(
      appBar: AppBar(
        title: Text(lp.translate('analysis_complete')),
        backgroundColor: Color(0xFF185846),
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.check_circle_outline, size: 80, color: Color(0xFF185846)),
              SizedBox(height: 24),
              Text(
                lp.translate('assessment_submitted'),
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 16),
              Text(
                _result!,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, color: Colors.grey[700]),
              ),
              SizedBox(height: 48),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF185846),
                  padding: EdgeInsets.symmetric(horizontal: 48, vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () => Navigator.pop(context),
                child: Text(lp.translate('finish'), style: TextStyle(fontSize: 18, color: Colors.white)),
              ),
            ],
          ),
          ),
      ),
    );
  }
}
