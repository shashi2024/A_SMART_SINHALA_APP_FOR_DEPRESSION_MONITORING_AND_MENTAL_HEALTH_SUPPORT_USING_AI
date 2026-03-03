import 'dart:collection';

class TypingAnalyzer {
  final List<double> _keystrokeTimings = [];
  final List<DateTime> _keyPressTimes = [];
  final List<Map<String, dynamic>> _keystrokeEvents = [];
  int _totalKeystrokes = 0;
  int _errors = 0;
  DateTime? _startTime;
  DateTime? _lastKeyPress;

  void startTracking() {
    _startTime = DateTime.now();
    _keystrokeTimings.clear();
    _keyPressTimes.clear();
    _keystrokeEvents.clear();
    _totalKeystrokes = 0;
    _errors = 0;
  }

  void recordKeystroke() {
    recordKeystrokeWithDetails('key');
  }

  void recordKeystrokeWithDetails(String key, {bool isBackspace = false}) {
    final now = DateTime.now();
    final timestamp = now.millisecondsSinceEpoch / 1000.0;
    
    if (_lastKeyPress != null) {
      final duration = now.difference(_lastKeyPress!).inMilliseconds / 1000.0;
      _keystrokeTimings.add(duration);
    }
    
    _keyPressTimes.add(now);
    
    _keystrokeEvents.add({
      'key': key,
      'press_time': timestamp,
      'release_time': timestamp + 0.05, // Approximation
      'is_backspace': isBackspace,
    });
    
    _lastKeyPress = now;
    _totalKeystrokes++;
    if (isBackspace) _errors++;
  }

  void recordError() {
    _errors++;
  }

  Future<Map<String, dynamic>> getAnalysis() async {
    if (_keystrokeEvents.isEmpty) {
      return {
        'keystroke_timings': [],
        'keystroke_events': [],
        'typing_speed': 0.0,
        'pause_duration': 0.0,
        'error_rate': 0.0,
      };
    }

    final totalTime = _keyPressTimes.isNotEmpty
        ? _keyPressTimes.last.difference(_keyPressTimes.first).inSeconds
        : 1;
    
    final typingSpeed = (_totalKeystrokes / (totalTime > 0 ? totalTime : 1)) * 60; // characters per minute
    
    // Calculate average pause duration (pauses > 0.5 seconds)
    final pauses = _keystrokeTimings.where((t) => t > 0.5).toList();
    final pauseDuration = pauses.isNotEmpty
        ? pauses.reduce((a, b) => a + b) / pauses.length
        : 0.0;
    
    final errorRate = _totalKeystrokes > 0 ? _errors / _totalKeystrokes : 0.0;

    return {
      'keystroke_timings': _keystrokeTimings,
      'keystroke_events': _keystrokeEvents,
      'typing_speed': typingSpeed,
      'pause_duration': pauseDuration,
      'error_rate': errorRate,
    };
  }

  void reset() {
    startTracking();
  }

  void stopTracking() {
    // Cleanup if needed
  }
}

