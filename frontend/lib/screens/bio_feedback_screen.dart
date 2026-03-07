import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:record/record.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/language_provider.dart';

class BioFeedbackScreen extends StatefulWidget {
  const BioFeedbackScreen({super.key});

  @override
  State<BioFeedbackScreen> createState() => _BioFeedbackScreenState();
}

class _BioFeedbackScreenState extends State<BioFeedbackScreen> {
  CameraController? _cameraController;
  final AudioRecorder _audioRecorder = AudioRecorder();
  
  bool _isInit = false;
  bool _isRecording = false;
  String _status = "Ready to start assessment"; // Initial value, will be updated in build
  double _progress = 0.0;
  
  List<Map<String, double>> _accelerometerData = [];
  StreamSubscription? _accelSubscription;
  
  String? _imagePath;
  String? _audioPath;
  Map<String, dynamic>? _results;

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
          _results = response['results'];
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
      cameras.firstWhere((c) => c.lensDirection == CameraLensDirection.front, orElse: () => cameras.first),
      ResolutionPreset.medium,
    );

    await _cameraController!.initialize();
    if (mounted) {
      setState(() {
        _isInit = true;
      });
    }
  }

  Future<void> _startAssessment() async {
    final lp = context.read<LanguageProvider>(); // Access lp here
    setState(() {
      _isRecording = true;
      _status = lp.translate('recording_sensors');
      _progress = 0.1;
      _accelerometerData.clear();
    });

    try {
      // 0. Request Permissions
      Map<Permission, PermissionStatus> statuses = await [
        Permission.microphone,
        Permission.camera,
      ].request();

      if (statuses[Permission.microphone] != PermissionStatus.granted ||
          statuses[Permission.camera] != PermissionStatus.granted) {
        setState(() {
          _isRecording = false;
          _status = "Permissions denied. Please allow camera and microphone access.";
        });
        return;
      }

      // 1. Start Accelerometer
      _accelSubscription = accelerometerEvents.listen((event) {
        _accelerometerData.add({'x': event.x, 'y': event.y, 'z': event.z});
      });

      // 2. Start Voice Recording
      final dir = await getTemporaryDirectory();
      _audioPath = '${dir.path}/bio_voice.m4a';
      await _audioRecorder.start(const RecordConfig(), path: _audioPath!);

      // 3. Simulate duration (Wait 10 seconds)
      for (int i = 0; i < 10; i++) {
        await Future.delayed(const Duration(seconds: 1));
        if (!mounted) return;
        setState(() {
          _progress = 0.1 + (i * 0.08);
          _status = "${lp.translate('recording')} (${10 - i}s)";
        });
      }

      // 4. Capture Image (Face) at the END of assessment
      if (_cameraController != null && _cameraController!.value.isInitialized) {
        final image = await _cameraController!.takePicture();
        _imagePath = image.path;
      }

      await _stopAssessment();
    } catch (e) {
      debugPrint("Assessment Error: $e");
      if (mounted) {
        setState(() {
          _isRecording = false;
          _status = "Error: $e";
        });
      }
    }
  }

  Future<void> _stopAssessment() async {
    final lp = context.read<LanguageProvider>();
    _accelSubscription?.cancel();
    
    // Capture the official recorded path
    final path = await _audioRecorder.stop();
    if (path != null) {
      _audioPath = path;
    }
    
    if (mounted) {
      setState(() {
        _status = lp.translate('analyzing_data');
        _progress = 0.9;
      });
    }

    await _uploadData();
  }

  Future<void> _uploadData() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final lp = context.read<LanguageProvider>(); // Access lp here
    final userId = auth.user?.id;
    if (userId == null) return;

    // Use the same backend base URL as the rest of the app so this works
    // both on Chrome and on a physical device (no hard‑coded localhost).
    final url = Uri.parse("${ApiService.baseUrl}/analyze/biofeedback?user_id=$userId");
    
    if (mounted) {
      setState(() {
        _status = "Analyzing Face (Local) & Voice (OpenAI)...";
        _progress = 0.95;
      });
    }

    var request = http.MultipartRequest("POST", url);
    
    // Add sensors data as fields
    request.fields['accelerometer_data'] = jsonEncode(_accelerometerData);
    
    // Simulate HR data (RR intervals in ms)
    List<int> mockHR = List.generate(10, (index) => 700 + (index * 5)); 
    request.fields['rr_intervals'] = jsonEncode(mockHR);

    // Add Files with existence checks
    try {
      if (_imagePath != null && await File(_imagePath!).exists()) {
        request.files.add(await http.MultipartFile.fromPath('image', _imagePath!));
      } else {
        debugPrint("Warning: Image file not found at $_imagePath");
      }
      
      if (_audioPath != null && await File(_audioPath!).exists()) {
        request.files.add(await http.MultipartFile.fromPath('audio', _audioPath!));
      } else {
        debugPrint("Warning: Audio file not found at $_audioPath");
      }
    } catch (e) {
      debugPrint("Error adding files to request: $e");
      if (mounted) {
        setState(() {
          _status = "File Error: $e";
          _isRecording = false;
        });
      }
      return;
    }

    try {
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(responseBody);
        if (!mounted) return;
        setState(() {
          _status = lp.translate('assessment_complete_msg');
          _progress = 1.0;
          _isRecording = false;
          _results = data['results'];
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(lp.translate('bio_feedback_success'))),
        );
      } else {
        setState(() {
          _status = "${lp.translate('analysis_failed')} (Status: ${response.statusCode})";
          _isRecording = false;
        });
      }
    } catch (e) {
      setState(() {
        _status = lp.translate('connection_error');
        _isRecording = false;
      });
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
    // Set initial status if not recording or finished
    if (!_isRecording && _progress == 0.0) {
      _status = lp.translate('ready_start_assessment');
    }

    return Scaffold(
      appBar: AppBar(title: Text(lp.translate('bio_feedback_heading'))),
      body: SingleChildScrollView(
        child: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
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
              
              const SizedBox(height: 40),
              Text(
                _status,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              LinearProgressIndicator(value: _progress),
              const SizedBox(height: 40),
              
              ElevatedButton.icon(
                onPressed: _isRecording ? null : _startAssessment,
                icon: const Icon(Icons.bolt),
                label: Text(lp.translate('start_10s_assessment')),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
              ),
              
              Padding(
                padding: const EdgeInsets.only(top: 20),
                child: Text(
                  lp.translate('bio_data_collection_desc'),
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
              ),
              
              if (_results != null) ...[
                const SizedBox(height: 30),
                _buildResultsCard(lp),
              ],
            ],
          ),
        ),
      ),
    ),);
  }

  Widget _buildResultsCard(LanguageProvider lp) {
    if (_results == null) return const SizedBox.shrink();
    
    final finalAssessment = _results?['final_assessment'];
    final sensors = _results?['sensors'];
    final riskLevel = finalAssessment?['risk_level'] ?? 'unknown';
    
    Color riskColor = Colors.green;
    if (riskLevel == 'severe' || riskLevel == 'high') riskColor = Colors.red;
    else if (riskLevel == 'moderate') riskColor = Colors.orange;

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        width: double.infinity,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [riskColor.withOpacity(0.1), Colors.white],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  lp.translate('stress_risk'),
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: riskColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    riskLevel.toUpperCase(),
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const Divider(height: 30),
            _buildResultRow(
              Icons.face, 
              lp.translate('facial_emotion'), 
              sensors?['face']?['expression'] ?? 'N/A'
            ),
            const SizedBox(height: 12),
            _buildResultRow(
              Icons.directions_walk, 
              lp.translate('physical_activity'), 
              sensors?['movement']?['activity'] ?? 'N/A'
            ),
            const SizedBox(height: 12),
            _buildResultRow(
              Icons.favorite, 
              lp.translate('heart_rate_status'), 
              sensors?['heart_rate']?['stress_level'] ?? 'N/A'
            ),
            if (sensors?['voice'] != null && sensors?['voice']?['level'] != null) ...[
               const SizedBox(height: 12),
               _buildResultRow(
                Icons.mic, 
                lp.translate('voice_stress_level') ?? 'Voice Stress', 
                sensors?['voice']?['level'] ?? 'N/A'
              ),
            ],
            const SizedBox(height: 20),
            Text(
              finalAssessment?['summary'] ?? '',
              style: const TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.blue),
        const SizedBox(width: 10),
        Text("$label:", style: const TextStyle(fontWeight: FontWeight.w600)),
        const Spacer(),
        Text(value, style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
