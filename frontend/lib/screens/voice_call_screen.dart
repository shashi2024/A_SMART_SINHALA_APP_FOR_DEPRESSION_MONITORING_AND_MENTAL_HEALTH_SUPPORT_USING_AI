import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
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

    // Analyze voice
    await voiceProvider.analyzeVoice(audioPath, sensorData);

    setState(() {
      _isAnalyzing = false;
    });
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
      ),
      body: Consumer<VoiceProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
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
                            'Fake Detection',
                            provider.lastAnalysis!['is_fake'] == true
                                ? 'Suspicious'
                                : 'Authentic',
                            isWarning: provider.lastAnalysis!['is_fake'] == true,
                          ),
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

