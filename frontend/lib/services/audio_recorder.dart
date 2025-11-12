import 'dart:async';
import 'dart:io';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';

class AudioRecorder {
  final AudioRecorder _recorder = Record();
  String? _currentPath;

  Future<void> startRecording() async {
    try {
      if (await _recorder.hasPermission()) {
        final directory = await getApplicationDocumentsDirectory();
        _currentPath = '${directory.path}/recording_${DateTime.now().millisecondsSinceEpoch}.m4a';
        await _recorder.start(
          const RecordConfig(
            encoder: AudioEncoder.aacLc,
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

