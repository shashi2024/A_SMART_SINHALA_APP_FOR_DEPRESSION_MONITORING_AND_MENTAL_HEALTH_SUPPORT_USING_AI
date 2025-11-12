import 'dart:collection';

class TypingAnalyzer {
  final List<double> _keystrokeTimings = [];
  final List<DateTime> _keyPressTimes = [];
  int _totalKeystrokes = 0;
  int _errors = 0;
  DateTime? _startTime;
  DateTime? _lastKeyPress;

  void startTracking() {
    _startTime = DateTime.now();
    _keystrokeTimings.clear();
    _keyPressTimes.clear();
    _totalKeystrokes = 0;
    _errors = 0;
  }

  void recordKeystroke() {
    final now = DateTime.now();
    
    if (_lastKeyPress != null) {
      final duration = now.difference(_lastKeyPress!).inMilliseconds / 1000.0;
      _keystrokeTimings.add(duration);
    }
    
    _keyPressTimes.add(now);
    _lastKeyPress = now;
    _totalKeystrokes++;
  }

  void recordError() {
    _errors++;
  }

  Future<Map<String, dynamic>> getAnalysis() async {
    if (_keystrokeTimings.isEmpty) {
      return {
        'keystroke_timings': [],
        'typing_speed': 0.0,
        'pause_duration': 0.0,
        'error_rate': 0.0,
      };
    }

    final totalTime = _keyPressTimes.isNotEmpty
        ? _keyPressTimes.last.difference(_keyPressTimes.first).inSeconds
        : 1;
    
    final typingSpeed = (_totalKeystrokes / totalTime) * 60; // characters per minute
    
    // Calculate average pause duration (pauses > 0.5 seconds)
    final pauses = _keystrokeTimings.where((t) => t > 0.5).toList();
    final pauseDuration = pauses.isNotEmpty
        ? pauses.reduce((a, b) => a + b) / pauses.length
        : 0.0;
    
    final errorRate = _totalKeystrokes > 0 ? _errors / _totalKeystrokes : 0.0;

    return {
      'keystroke_timings': _keystrokeTimings,
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

