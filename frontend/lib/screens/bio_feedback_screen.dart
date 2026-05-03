import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:record/record.dart';
import 'package:heart_bpm/heart_bpm.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/language_provider.dart';

// Assessment Step Enum
enum AssessmentStep {
  ready,
  face,
  voice,
  heartRate,
  accelerometer,
  complete,
}

class BioFeedbackScreen extends StatefulWidget {
  const BioFeedbackScreen({super.key});

  @override
  State<BioFeedbackScreen> createState() => _BioFeedbackScreenState();
}

class _BioFeedbackScreenState extends State<BioFeedbackScreen> {
  CameraController? _cameraController;
  final AudioRecorder _audioRecorder = AudioRecorder();

  bool _isInit = false;
  bool _isProcessing = false;
  bool _isHeartRateMonitoring = false;
  String _status = "Ready to start assessment";
  double _progress = 0.0;
  AssessmentStep _currentStep = AssessmentStep.ready;

  // Data storage for each modality
  List<Map<String, double>> _accelerometerData = [];
  StreamSubscription? _accelSubscription;

  String? _imagePath;
  String? _audioPath;
  int? _heartRate;
  final List<int> _heartRateSamples = [];
  Timer? _heartRateTimer;

  // Results from each endpoint
  Map<String, dynamic>? _faceResults;
  Map<String, dynamic>? _voiceResults;
  Map<String, dynamic>? _hrResults;
  Map<String, dynamic>? _accelResults;
  Map<String, dynamic>? _finalResults;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchLatestResults();
    });
  }

  Future<void> _fetchLatestResults() async {
    try {
      final authProvider = context.read<AuthProvider>();
      final user = authProvider.user;
      if (user == null || user.id.isEmpty) return;

      final apiService = context.read<ApiService>();
      final response = await apiService.getLatestBiofeedback(user.id);

      if (response['status'] == 'success' && response['results'] != null) {
        if (!mounted) return;
        setState(() {
          _finalResults = response['results'];
        });
      }
    } catch (e) {
      debugPrint("Error fetching latest biofeedback: $e");
    }
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    if (cameras.isEmpty) return;

    _cameraController = CameraController(
      cameras.firstWhere((c) => c.lensDirection == CameraLensDirection.front,
          orElse: () => cameras.first),
      ResolutionPreset.medium,
    );

    await _cameraController!.initialize();
    if (mounted) {
      setState(() {
        _isInit = true;
      });
    }
  }

  /// Start the assessment flow - Step 1: Face Capture
  Future<void> _startAssessment() async {
    final lp = context.read<LanguageProvider>();

    // Request permissions
    Map<Permission, PermissionStatus> statuses = await [
      Permission.microphone,
      Permission.camera,
    ].request();

    if (statuses[Permission.microphone] != PermissionStatus.granted ||
        statuses[Permission.camera] != PermissionStatus.granted) {
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _status =
              "Permissions denied. Please allow camera and microphone access.";
        });
      }
      return;
    }

    setState(() {
      _currentStep = AssessmentStep.face;
      _isProcessing = true;
      _status = lp.translate('capturing_face') ?? 'Capturing your face...';
      _progress = 0.0;
    });
    // Immediately capture the face photo so the first step is automatic.
    // The next button will then proceed to voice recording as expected.
    try {
      await _captureFace();
    } catch (e) {
      debugPrint('Automatic face capture failed: $e');
    }
  }

  /// Step 1: Capture Face
  Future<void> _captureFace() async {
    final lp = context.read<LanguageProvider>();

    try {
      if (_cameraController == null ||
          !_cameraController!.value.isInitialized) {
        setState(() {
          _status = "Camera not initialized";
          _isProcessing = false;
        });
        return;
      }

      // Capture image
      final image = await _cameraController!.takePicture();
      _imagePath = image.path;

      // Upload to face endpoint
      await _uploadFaceData();

      // Move to next step
      if (mounted) {
        setState(() {
          _currentStep = AssessmentStep.voice;
          _progress = 0.25;
          _status = lp.translate('capturing_voice') ?? 'Recording voice...';
          _isProcessing =
              false; // allow user to press Next to start voice recording
        });
      }
    } catch (e) {
      debugPrint("Face capture error: $e");
      if (mounted) {
        setState(() {
          _status = "Face capture error: $e";
          _isProcessing = false;
        });
      }
    }
  }

  /// Step 2: Voice Recording
  Future<void> _recordVoice() async {
    final lp = context.read<LanguageProvider>();

    try {
      setState(() {
        _isProcessing = true;
      });
      final dir = await getTemporaryDirectory();
      _audioPath =
          '${dir.path}/bio_voice_${DateTime.now().millisecondsSinceEpoch}.wav';

      await _audioRecorder.start(
        const RecordConfig(encoder: AudioEncoder.wav),
        path: _audioPath!,
      );

      // Record for 10 seconds
      for (int i = 0; i < 10; i++) {
        await Future.delayed(const Duration(seconds: 1));
        if (!mounted) return;
        setState(() {
          _progress = 0.25 + (i * 0.075);
          _status =
              "${lp.translate('recording') ?? 'Recording'} voice... (${10 - i}s)";
        });
      }

      // Stop recording
      final recordedPath = await _audioRecorder.stop();
      if (recordedPath != null) {
        _audioPath = recordedPath;
      }

      // Mock upload to voice endpoint (local simulation)
      await _uploadVoiceData();

      setState(() {
        _isProcessing = false;
      });

      // Move to next step
      if (mounted) {
        setState(() {
          _currentStep = AssessmentStep.heartRate;
          _progress = 0.5;
          _status =
              lp.translate('measuring_heart_rate') ?? 'Measuring heart rate...';
        });
      }
    } catch (e) {
      debugPrint("Voice recording error: $e");
      if (mounted) {
        setState(() {
          _status = "Voice recording error: $e";
          _isProcessing = false;
        });
      }
    }
  }

  /// Step 3: Heart Rate Measurement
  Future<void> _measureHeartRate() async {
    final lp = context.read<LanguageProvider>();

    try {
      _heartRateTimer?.cancel();
      _heartRateSamples.clear();

      setState(() {
        _isProcessing = true;
        _isHeartRateMonitoring = true;
        _progress = 0.5;
        _status =
            lp.translate('measuring_heart_rate') ?? 'Measuring heart rate...';
      });

      const totalSeconds = 12;
      var elapsedSeconds = 0;
      final completion = Completer<void>();

      _heartRateTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        if (!mounted) {
          timer.cancel();
          if (!completion.isCompleted) completion.complete();
          return;
        }

        elapsedSeconds++;

        setState(() {
          _progress = 0.5 + ((elapsedSeconds / totalSeconds) * 0.2);
          _status =
              "${lp.translate('measuring_heart_rate') ?? 'Measuring heart rate'} (${totalSeconds - elapsedSeconds}s)";
        });

        if (elapsedSeconds >= totalSeconds) {
          timer.cancel();
          if (!completion.isCompleted) completion.complete();
        }
      });

      await completion.future;

      if (_heartRateSamples.isNotEmpty) {
        final avgBpm = _heartRateSamples.reduce((a, b) => a + b) /
            _heartRateSamples.length;
        _heartRate = avgBpm.round();
        _hrResults = {
          'status': 'success',
          'bpm': _heartRate,
          'stress_level': _deriveStressLevelFromBpm(_heartRate!),
        };

        final rrIntervals = _heartRateSamples
            .where((bpm) => bpm > 0)
            .map((bpm) => 60000 ~/ bpm)
            .toList();
        if (rrIntervals.isNotEmpty) {
          await _uploadHeartRateData(rrIntervals);
        }
      }

      // Move to next step
      if (mounted) {
        setState(() {
          _isHeartRateMonitoring = false;
          _currentStep = AssessmentStep.accelerometer;
          _progress = 0.7;
          _status =
              lp.translate('recording_sensors') ?? 'Recording movement...';
          _isProcessing = false;
        });
      }
    } catch (e) {
      debugPrint("Heart rate measurement error: $e");
      if (mounted) {
        setState(() {
          _status = "Heart rate error: $e";
          _isProcessing = false;
          _isHeartRateMonitoring = false;
        });
      }
    } finally {
      _heartRateTimer?.cancel();
      _heartRateTimer = null;
    }
  }

  /// Step 4: Accelerometer Data Collection
  Future<void> _collectAccelerometerData() async {
    final lp = context.read<LanguageProvider>();

    try {
      _accelerometerData.clear();

      _accelSubscription = accelerometerEvents.listen((event) {
        _accelerometerData.add({
          'x': event.x,
          'y': event.y,
          'z': event.z,
        });
      });

      // Collect for 10 seconds
      for (int i = 0; i < 10; i++) {
        await Future.delayed(const Duration(seconds: 1));
        if (!mounted) return;

        setState(() {
          _progress = 0.7 + (i * 0.03);
          _status =
              "${lp.translate('recording_sensors') ?? 'Recording movement'} (${10 - i}s)";
        });
      }

      _accelSubscription?.cancel();

      // Upload to accelerometer endpoint
      await _uploadAccelerometerData();

      // NEW: Save all combined results together
      await _saveCombinedResults();

      // Assessment complete
      if (mounted) {
        setState(() {
          _currentStep = AssessmentStep.complete;
          _progress = 1.0;
          _status =
              lp.translate('assessment_complete_msg') ?? 'Assessment Complete!';
          _isProcessing = false;
        });
      }
    } catch (e) {
      debugPrint("Accelerometer collection error: $e");
      if (mounted) {
        setState(() {
          _status = "Accelerometer error: $e";
          _isProcessing = false;
        });
      }
    }
  }

  /// Proceed to next step
  Future<void> _nextStep() async {
    switch (_currentStep) {
      case AssessmentStep.ready:
        await _startAssessment();
        break;
      case AssessmentStep.face:
        await _captureFace();
        break;
      case AssessmentStep.voice:
        await _recordVoice();
        break;
      case AssessmentStep.heartRate:
        await _measureHeartRate();
        break;
      case AssessmentStep.accelerometer:
        await _collectAccelerometerData();
        break;
      case AssessmentStep.complete:
        _resetAssessment();
        break;
    }
  }

  /// Reset assessment to initial state
  void _resetAssessment() {
    setState(() {
      _currentStep = AssessmentStep.ready;
      _isProcessing = false;
      _progress = 0.0;
      _status = context
              .read<LanguageProvider>()
              .translate('ready_start_assessment') ??
          'Ready to start assessment';
      _imagePath = null;
      _audioPath = null;
      _heartRate = null;
      _accelerometerData.clear();
      _faceResults = null;
      _voiceResults = null;
      _hrResults = null;
      _accelResults = null;
    });
  }

  /// Upload face data to face analysis endpoint
  Future<void> _uploadFaceData() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userId = auth.user?.id;
    if (userId == null || _imagePath == null) return;

    final url = Uri.parse('${ApiService.baseUrl}/predict-expression-ai');
    try {
      if (!await File(_imagePath!).exists()) {
        debugPrint('Face image not found: $_imagePath');
        return;
      }

      var request = http.MultipartRequest('POST', url);
      // API expects 'image' field as binary. Ensure correct content-type.
      String mimeType = _imagePath!.toLowerCase().endsWith('.png')
          ? 'image/png'
          : 'image/jpeg';
      final parts = mimeType.split('/');
      request.files.add(await http.MultipartFile.fromPath(
        'image',
        _imagePath!,
        contentType: MediaType(parts[0], parts[1]),
      ));

      final streamed = await request.send();
      final body = await streamed.stream.bytesToString();

      if (streamed.statusCode == 200) {
        try {
          final Map<String, dynamic> json = jsonDecode(body);
          // Backend returns { status, predicted_expression, stress_level }
          debugPrint(json.toString());
          if (json['status'] == 'success') {
            setState(() {
              _faceResults = {
                'expression': json['predicted_expression'] ??
                    json['expression'] ??
                    'unknown',
                'stress_level': json['stress_level'] ?? 'unknown',
              };
            });
          } else {
            debugPrint('Face API returned error: ${json.toString()}');
          }
        } catch (e) {
          debugPrint('Face response decode error: $e');
        }
      } else {
        debugPrint('Face upload failed: ${streamed.statusCode}');
        debugPrint('Face upload response body: $body');
      }
    } catch (e) {
      debugPrint('Face upload error: $e');
    }
  }

  /// Upload voice data to voice analysis endpoint
  Future<void> _uploadVoiceData() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userId = auth.user?.id;
    if (userId == null || _audioPath == null) return;

    final url = Uri.parse('${ApiService.baseUrl}/predict-voice-stress-ai');
    try {
      if (!await File(_audioPath!).exists()) {
        debugPrint('Audio file not found: $_audioPath');
        return;
      }

      var request = http.MultipartRequest('POST', url);
      final mimeType = _audioPath!.toLowerCase().endsWith('.wav')
          ? 'audio/wav'
          : 'audio/mpeg';
      final mimeParts = mimeType.split('/');
      request.files.add(await http.MultipartFile.fromPath(
        'audio',
        _audioPath!,
        contentType: MediaType(mimeParts[0], mimeParts[1]),
      ));

      final streamed = await request.send();
      debugPrint('Voice upload status: ${streamed.statusCode}');
      final body = await streamed.stream.bytesToString();

      if (streamed.statusCode == 200) {
        try {
          final Map<String, dynamic> json = jsonDecode(body);
          setState(() {
            _voiceResults = json;
          });
        } catch (e) {
          debugPrint('Voice response decode error: $e');
        }
      } else {
        debugPrint('Voice upload failed: ${streamed.statusCode}');
        debugPrint('Voice upload response body: $body');
        if (!mounted) return;
        setState(() {
          _voiceResults = {
            'status': 'success',
            'stress_level': 'low',
            'message': 'Voice backend unavailable, using local fallback',
          };
        });
      }
    } catch (e) {
      debugPrint('Voice upload error: $e');
      if (!mounted) return;
      setState(() {
        _voiceResults = {
          'status': 'success',
          'stress_level': 'low',
          'message': 'Voice upload failed locally: $e',
        };
      });
    }
  }

  /// Upload heart rate data to heart rate analysis endpoint
  Future<void> _uploadHeartRateData(List<int> rrIntervals) async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userId = auth.user?.id;
    if (userId == null) return;

    final url =
        Uri.parse('${ApiService.baseUrl}/analyze/heart-rate?user_id=$userId');
    try {
      final payload = {
        'timestamp': DateTime.now().toIso8601String(),
        'rr_intervals': rrIntervals,
      };

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        try {
          final Map<String, dynamic> json = jsonDecode(response.body);
          setState(() {
            _hrResults = json;
          });
        } catch (e) {
          debugPrint('Heart rate response decode error: $e');
        }
      } else {
        debugPrint('Heart rate upload failed: ${response.statusCode}');
        debugPrint('Heart rate upload response body: ${response.body}');
        if (!mounted) return;
        setState(() {
          _hrResults = {
            'status': 'mock',
            'stress_level': 'unknown',
            'message': 'Heart-rate backend unavailable, using local estimate',
          };
        });
      }
    } catch (e) {
      debugPrint('Heart rate upload error: $e');
      if (!mounted) return;
      setState(() {
        _hrResults = {
          'status': 'mock',
          'stress_level': 'unknown',
          'message': 'Heart-rate upload failed locally: $e',
        };
      });
    }
  }

  /// Upload accelerometer data to accelerometer analysis endpoint
  Future<void> _uploadAccelerometerData() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userId = auth.user?.id;
    if (userId == null) return;

    final url =
        Uri.parse('${ApiService.baseUrl}/analyze/activity?user_id=$userId');
    try {
      // Attach timestamps to samples if missing
      final samples = _accelerometerData.map((d) {
        return {
          'x': d['x'],
          'y': d['y'],
          'z': d['z'],
          'timestamp': DateTime.now().toIso8601String(),
        };
      }).toList();

      final payload = {
        'timestamp': DateTime.now().toIso8601String(),
        'accelerometer_data': samples,
      };

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        try {
          final Map<String, dynamic> json = jsonDecode(response.body);
          setState(() {
            _accelResults = json;
          });
        } catch (e) {
          debugPrint('Accel response decode error: $e');
        }
      } else {
        debugPrint('Accelerometer upload failed: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Accelerometer upload error: $e');
    }
  }

  Future<void> _saveCombinedResults() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userId = auth.user?.id;
    if (userId == null) return;
    
    try {
      final apiService = context.read<ApiService>();
      final payload = {
        'user_id': userId,
        'face': _faceResults ?? {'error': 'No data'},
        'voice': _voiceResults ?? {'error': 'No data'},
        'heart_rate': _hrResults ?? {'error': 'No data'},
        'movement': _accelResults ?? {'error': 'No data'},
      };
      
      final response = await apiService.post('/analyze/biofeedback/save', payload);
      if (response['status'] == 'success') {
        if (!mounted) return;
        setState(() {
          _finalResults = response['results'];
        });
      }
    } catch (e) {
      debugPrint("Save combined results error: $e");
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _audioRecorder.dispose();
    _accelSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();

    return Scaffold(
      appBar: AppBar(title: Text(lp.translate('bio_feedback_heading'))),
      body: SingleChildScrollView(
        child: Center(
          child: Padding(
            padding: EdgeInsets.fromLTRB(
                24, 24, 24, 24 + MediaQuery.of(context).padding.bottom + 16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Step Indicators
                _buildStepIndicators(lp),

                const SizedBox(height: 40),

                // Camera Preview for Face Step
                if (_currentStep == AssessmentStep.ready ||
                    _currentStep == AssessmentStep.face)
                  if (_isInit && _cameraController != null)
                    Container(
                      height: 200,
                      width: 200,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(100),
                        border: Border.all(color: Colors.blue, width: 4),
                      ),
                      clipBehavior: Clip.hardEdge,
                      child: CameraPreview(_cameraController!),
                    )
                  else
                    const Icon(Icons.face, size: 100, color: Colors.grey),

                // Icons for other steps
                if (_currentStep == AssessmentStep.voice)
                  const Icon(Icons.mic, size: 100, color: Colors.red),
                if (_currentStep == AssessmentStep.heartRate)
                  if (_isHeartRateMonitoring)
                    Card(
                      elevation: 4,
                      color: Colors.black,
                      child: SizedBox(
                        height: 300,
                        width: double.infinity,
                        child: _buildHeartRateMonitor(),
                      ),
                    )
                  else
                    const Icon(Icons.favorite, size: 100, color: Colors.red),
                if (_currentStep == AssessmentStep.accelerometer)
                  const Icon(Icons.speed, size: 100, color: Colors.orange),
                if (_currentStep == AssessmentStep.complete)
                  const Icon(Icons.check_circle,
                      size: 100, color: Colors.green),

                const SizedBox(height: 40),

                Text(
                  _status,
                  style: const TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 20),
                LinearProgressIndicator(
                  value: _progress,
                  minHeight: 8,
                ),

                const SizedBox(height: 40),

                // Next Button
                ElevatedButton.icon(
                  onPressed: _isProcessing ? null : _nextStep,
                  icon: Icon(_currentStep == AssessmentStep.complete
                      ? Icons.refresh
                      : Icons.arrow_forward),
                  label: Text(
                    _currentStep == AssessmentStep.complete
                        ? lp.translate('start_over') ?? 'Start Over'
                        : lp.translate('next') ?? 'Next',
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 32, vertical: 16),
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                  ),
                ),

                const SizedBox(height: 20),

                Padding(
                  padding: const EdgeInsets.only(top: 20),
                  child: Text(
                    lp.translate('bio_data_collection_desc') ??
                        'Step-by-step biometric data collection',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                    textAlign: TextAlign.center,
                  ),
                ),

                // Results Display
                if (_currentStep == AssessmentStep.complete) ...[
                  const SizedBox(height: 40),
                  _buildResultsDisplay(lp),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Build step indicator widgets
  Widget _buildStepIndicators(LanguageProvider lp) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildStepBadge(
              'Face',
              AssessmentStep.face,
              Icons.face,
            ),
            _buildStepBadge(
              'Voice',
              AssessmentStep.voice,
              Icons.mic,
            ),
            _buildStepBadge(
              'Heart',
              AssessmentStep.heartRate,
              Icons.favorite,
            ),
            _buildStepBadge(
              'Motion',
              AssessmentStep.accelerometer,
              Icons.speed,
            ),
          ],
        ),
      ],
    );
  }

  /// Build individual step badge
  Widget _buildStepBadge(String label, AssessmentStep step, IconData icon) {
    bool isCompleted = _currentStep.index > step.index;
    bool isCurrent = _currentStep == step;

    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isCurrent
                ? Colors.blue
                : isCompleted
                    ? Colors.green
                    : Colors.grey.shade300,
          ),
          child: Icon(
            isCompleted ? Icons.check : icon,
            color: isCurrent || isCompleted ? Colors.white : Colors.grey,
            size: 30,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: isCurrent ? Colors.blue : Colors.grey,
          ),
        ),
      ],
    );
  }

  /// Build results display for current assessment
  Widget _buildResultsDisplay(LanguageProvider lp) {
    final aggregatedStress = _computeAggregatedStressLevel();

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              lp.translate('Assessment Results'),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (aggregatedStress != null) ...[
              _buildAggregatedStressCard(aggregatedStress),
              const SizedBox(height: 16),
            ],
            if (_faceResults != null) ...[
              _buildResultItem('Face Analysis', _faceResults),
              const Divider(height: 20),
            ],
            if (_voiceResults != null) ...[
              _buildResultItem('Voice Analysis', _voiceResults),
              const Divider(height: 20),
            ],
            if (_hrResults != null) ...[
              _buildResultItem(
                'Heart Rate',
                {'bpm': _heartRate, ...?_hrResults},
              ),
              const Divider(height: 20),
            ],
            if (_accelResults != null) ...[
              _buildResultItem('Movement Analysis', _accelResults),
            ],
          ],
        ),
      ),
    );
  }

  String? _computeAggregatedStressLevel() {
    final scores = <int>[];

    final faceScore = _faceStressScore();
    if (faceScore != null) scores.add(faceScore);

    final voiceScore = _voiceStressScore();
    if (voiceScore != null) scores.add(voiceScore);

    final heartScore = _heartStressScore();
    if (heartScore != null) scores.add(heartScore);

    if (scores.isEmpty) return null;

    final avg = scores.reduce((a, b) => a + b) / scores.length;
    if (avg >= 2.5) return 'High';
    if (avg >= 1.5) return 'Medium';
    return 'Low';
  }

  String _deriveStressLevelFromBpm(int bpm) {
    if (bpm >= 100) return 'High';
    if (bpm >= 75) return 'Medium';
    return 'Low';
  }

  Widget _buildHeartRateMonitor() {
    return HeartBPMDialog(
      context: context,
      onBPM: (int bpm) {
        if (!mounted) return;
        setState(() {
          _heartRate = bpm;
          _heartRateSamples.add(bpm);
          _hrResults = {
            'status': 'measuring',
            'bpm': bpm,
            'stress_level': _deriveStressLevelFromBpm(bpm),
          };
        });
      },
      onRawData: (SensorValue value) {
        debugPrint('Heart rate raw value: ${value.value}');
      },
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.fingerprint,
            size: 64,
            color: Colors.white,
          ),
          const SizedBox(height: 16),
          const Text(
            'Place your finger on the camera',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Cover both camera and flash completely',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          if (_heartRate != null)
            Text(
              '$_heartRate BPM',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
        ],
      ),
    );
  }

  int? _faceStressScore() {
    final rawStress =
        _faceResults?['stress_level']?.toString().toLowerCase().trim();
    if (rawStress != null) {
      if (rawStress.contains('high')) return 3;
      if (rawStress.contains('medium')) return 2;
      if (rawStress.contains('low')) return 1;
    }

    final expression =
        _faceResults?['expression']?.toString().toLowerCase().trim();
    const stressLevelMap = {
      'angry': 3,
      'fear': 3,
      'happy': 1,
      'neutral': 1,
      'sad': 2,
      'surprise': 2,
    };
    return stressLevelMap[expression];
  }

  int? _voiceStressScore() {
    final stress =
        _voiceResults?['stress_level']?.toString().toLowerCase().trim();
    final level = _voiceResults?['level']?.toString().toLowerCase().trim();
    final value = stress ?? level;
    if (value == null) return null;
    if (value.contains('high')) return 3;
    if (value.contains('medium') || value.contains('moderate')) return 2;
    if (value.contains('low')) return 1;
    return null;
  }

  int? _heartStressScore() {
    final explicit =
        _hrResults?['stress_level']?.toString().toLowerCase().trim();
    if (explicit != null) {
      if (explicit.contains('high')) return 3;
      if (explicit.contains('elevated')) return 3;
      if (explicit.contains('normal')) return 2;
      if (explicit.contains('relaxed')) return 1;
    }

    final dynamic rmssdRaw = _hrResults?['rmssd'] ??
        _hrResults?['metrics']?['rmssd'] ??
        _hrResults?['hrv_metrics']?['rmssd'];
    final rmssd = rmssdRaw is num
        ? rmssdRaw.toDouble()
        : double.tryParse(rmssdRaw?.toString() ?? '');
    if (rmssd == null) return null;

    if (rmssd > 50) return 1;
    if (rmssd >= 30 && rmssd <= 50) return 2;
    if (rmssd >= 15 && rmssd < 30) return 3;
    return 3;
  }

  Widget _buildAggregatedStressCard(String stressLevel) {
    Color color;
    if (stressLevel == 'High') {
      color = Colors.red;
    } else if (stressLevel == 'Medium') {
      color = Colors.orange;
    } else {
      color = Colors.green;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          Icon(Icons.analytics, color: color),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              'Aggregated Stress',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
            ),
          ),
          Text(
            stressLevel,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  /// Build individual result item
  Widget _buildResultItem(String title, Map<String, dynamic>? data) {
    if (data == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        const SizedBox(height: 8),
        ...data.entries.map((e) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: Text(
                      e.key,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 2,
                    child: Text(
                      e.value.toString(),
                      style: const TextStyle(fontWeight: FontWeight.w600),
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  Widget _buildResultRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.blue),
        const SizedBox(width: 10),
        Flexible(
          flex: 1,
          child: Text("$label:",
              style: const TextStyle(fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis),
        ),
        const SizedBox(width: 8),
        Flexible(
          flex: 1,
          child: Text(value,
              style: const TextStyle(
                  color: Colors.blueAccent, fontWeight: FontWeight.bold),
              textAlign: TextAlign.right,
              overflow: TextOverflow.ellipsis),
        ),
      ],
    );
  }
}
