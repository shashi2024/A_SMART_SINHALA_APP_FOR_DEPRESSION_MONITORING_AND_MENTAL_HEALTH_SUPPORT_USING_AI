import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/voice_provider.dart';
import '../providers/sensor_provider.dart';
import '../services/audio_recorder.dart';

class VoiceCallScreen extends StatefulWidget {
  const VoiceCallScreen({super.key});

  @override
  State<VoiceCallScreen> createState() => _VoiceCallScreenState();
}

class _VoiceCallScreenState extends State<VoiceCallScreen> {
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isAnalyzing = false;
  Timer? _recordingTimer;
  int _recordingDuration = 0;

  @override
  void dispose() {
    _recordingTimer?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  void _startRecording() async {
    setState(() {
      _isRecording = true;
      _recordingDuration = 0;
    });

    await _audioRecorder.startRecording();

    _recordingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _recordingDuration = timer.tick;
      });
    });
  }

  void _stopRecording() async {
    _recordingTimer?.cancel();
    
    setState(() {
      _isRecording = false;
      _isAnalyzing = true;
    });

    final audioPath = await _audioRecorder.stopRecording();
    final sensorProvider = Provider.of<SensorProvider>(context, listen: false);
    final voiceProvider = Provider.of<VoiceProvider>(context, listen: false);

    // Get sensor data during recording
    final sensorData = await sensorProvider.getCurrentSensorData();

    // Analyze voice with selected language
    await voiceProvider.analyzeVoice(audioPath, sensorData);

    setState(() {
      _isAnalyzing = false;
    });
  }

  void _showLanguageSelector(BuildContext context) async {
    final voiceProvider = Provider.of<VoiceProvider>(context, listen: false);
    
    if (voiceProvider.supportedLanguages == null) {
      await voiceProvider.loadSupportedLanguages();
    }

    final selectedLanguage = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: (voiceProvider.supportedLanguages ?? []).map((lang) {
            return RadioListTile<String>(
              title: Text('${lang['name']} (${lang['native_name']})'),
              value: lang['code'],
              groupValue: voiceProvider.selectedLanguage,
              onChanged: (value) {
                Navigator.pop(context, value);
              },
            );
          }).toList(),
        ),
      ),
    );

    if (selectedLanguage != null) {
      await voiceProvider.setLanguage(selectedLanguage);
    }
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Call Analysis'),
        actions: [
          Consumer<VoiceProvider>(
            builder: (context, provider, child) {
              return IconButton(
                icon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.language),
                    const SizedBox(width: 4),
                    Text(
                      provider.selectedLanguage.toUpperCase(),
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
                onPressed: () => _showLanguageSelector(context),
                tooltip: 'Select Language',
              );
            },
          ),
        ],
      ),
      body: Consumer<VoiceProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Language indicator
                Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      children: [
                        const Icon(Icons.language, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'Language: ${provider.selectedLanguage == 'sinhala' ? 'සිංහල' : provider.selectedLanguage == 'tamil' ? 'தமிழ்' : 'English'}',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        Icon(
                          _isRecording ? Icons.mic : Icons.mic_none,
                          size: 80,
                          color: _isRecording ? Colors.red : Colors.grey,
                        ),
                        const SizedBox(height: 16),
                        if (_isRecording)
                          Text(
                            _formatDuration(_recordingDuration),
                            style: const TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        else
                          const Text(
                            'Tap to start recording',
                            style: TextStyle(fontSize: 18),
                          ),
                        const SizedBox(height: 24),
                        ElevatedButton.icon(
                          onPressed: _isRecording ? _stopRecording : _startRecording,
                          icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                          label: Text(_isRecording ? 'Stop Recording' : 'Start Recording'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 32,
                              vertical: 16,
                            ),
                            backgroundColor: _isRecording ? Colors.red : Colors.blue,
                          ),
                        ),
                        if (_isAnalyzing)
                          const Padding(
                            padding: EdgeInsets.only(top: 16.0),
                            child: CircularProgressIndicator(),
                          ),
                      ],
                    ),
                  ),
                ),
                if (provider.lastAnalysis != null) ...[
                  const SizedBox(height: 16),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Analysis Results',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 16),
                          _buildAnalysisRow(
                            'Emotion',
                            provider.lastAnalysis!['emotion'] ?? 'N/A',
                          ),
                          _buildAnalysisRow(
                            'Depression Score',
                            '${(provider.lastAnalysis!['depression_score'] * 100).toStringAsFixed(1)}%',
                          ),
                          _buildAnalysisRow(
                            'Risk Level',
                            provider.lastAnalysis!['risk_level'] ?? 'N/A',
                          ),
                          _buildAnalysisRow(
                            'Call Bot Detection',
                            provider.lastAnalysis!['is_call_bot'] == true
                                ? 'Bot Detected'
                                : 'Authentic',
                            isWarning: provider.lastAnalysis!['is_call_bot'] == true,
                          ),
                          if (provider.lastAnalysis!['bot_confidence'] != null)
                            _buildAnalysisRow(
                              'Bot Confidence',
                              '${(provider.lastAnalysis!['bot_confidence'] * 100).toStringAsFixed(1)}%',
                              isWarning: provider.lastAnalysis!['is_call_bot'] == true,
                            ),
                          if (provider.lastAnalysis!['bot_type'] != null)
                            _buildAnalysisRow(
                              'Bot Type',
                              provider.lastAnalysis!['bot_type'] ?? 'N/A',
                              isWarning: true,
                            ),
                          if (provider.lastAnalysis!['transcription'] != null &&
                              provider.lastAnalysis!['transcription'].toString().isNotEmpty) ...[
                            const SizedBox(height: 12),
                            const Text(
                              'Transcription:',
                              style: TextStyle(
                                fontWeight: FontWeight.w500,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade100,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                provider.lastAnalysis!['transcription'],
                                style: const TextStyle(fontSize: 12),
                              ),
                            ),
                          ],
                          if (provider.lastAnalysis!['recommendations'] != null)
                            ...(provider.lastAnalysis!['recommendations'] as List)
                                .map((rec) => Padding(
                                      padding: const EdgeInsets.only(top: 8.0),
                                      child: Row(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          const Icon(Icons.info_outline,
                                              size: 16),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(rec.toString()),
                                          ),
                                        ],
                                      ),
                                    ))
                                .toList(),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildAnalysisRow(String label, String value, {bool isWarning = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: isWarning ? Colors.red : Colors.black,
            ),
          ),
        ],
      ),
    );
  }
}
