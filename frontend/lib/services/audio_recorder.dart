import 'dart:async';
import 'package:record/record.dart' as record_package;
import 'package:path_provider/path_provider.dart';

class AudioRecorder {
  final record_package.AudioRecorder _recorder = record_package.AudioRecorder();
  String? _currentPath;

  Future<void> startRecording() async {
    try {
      if (await _recorder.hasPermission()) {
        final directory = await getApplicationDocumentsDirectory();
        _currentPath = '${directory.path}/recording_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _recorder.start(
          const record_package.RecordConfig(
            encoder: record_package.AudioEncoder.aacLc,
            bitRate: 128000,
            sampleRate: 44100,
          ),
          path: _currentPath!,
        );
      }
    } catch (e) {
      throw Exception('Failed to start recording: $e');
    }
  }

  Future<String> stopRecording() async {
    try {
      final path = await _recorder.stop();
      return path ?? _currentPath ?? '';
    } catch (e) {
      throw Exception('Failed to stop recording: $e');
    }
  }

  void dispose() {
    _recorder.dispose();
  }
}

