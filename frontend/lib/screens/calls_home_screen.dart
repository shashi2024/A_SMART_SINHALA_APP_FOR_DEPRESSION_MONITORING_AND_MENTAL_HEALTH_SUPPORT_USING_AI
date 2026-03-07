import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_provider.dart';
import '../providers/language_provider.dart';
import 'call_screen_simple.dart';

class CallsHomeScreen extends StatefulWidget {
  const CallsHomeScreen({super.key});

  @override
  State<CallsHomeScreen> createState() => _CallsHomeScreenState();
}

class _CallsHomeScreenState extends State<CallsHomeScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    callProvider.loadCallHistory();
    callProvider.loadAvailableCounselors();
  }

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();
    return Scaffold(
      appBar: AppBar(
        title: Text(lp.translate('calls')),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              final callProvider = Provider.of<CallProvider>(context, listen: false);
              callProvider.loadCallHistory();
              callProvider.loadAvailableCounselors();
            },
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _buildCallOptionsTab(lp),
          _buildCallHistoryTab(lp),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.phone),
            label: lp.translate('new_call'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.history),
            label: lp.translate('history'),
          ),
        ],
      ),
    );
  }

  Widget _buildCallOptionsTab(LanguageProvider lp) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            lp.translate('start_a_call'),
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          
          // AI Practice Call
          _buildCallOptionCard(
            icon: Icons.smart_toy,
            title: lp.translate('practice_ai'),
            subtitle: lp.translate('practice_ai_desc'),
            color: Colors.blue,
            onTap: () => _startAIPracticeCall(lp),
          ),
          
          const SizedBox(height: 16),
          
          // Counselor Call
          _buildCallOptionCard(
            icon: Icons.people,
            title: lp.translate('call_counselor'),
            subtitle: lp.translate('connect_counselor_desc'),
            color: Colors.green,
            onTap: () => _showCounselorSelection(lp),
          ),
          
          const SizedBox(height: 16),
          
          // Emergency Call
          _buildCallOptionCard(
            icon: Icons.emergency,
            title: lp.translate('emergency_call'),
            subtitle: lp.translate('emergency_desc'),
            color: Colors.red,
            onTap: () => _startEmergencyCall(lp),
          ),
        ],
      ),
    );
  }

  Widget _buildCallOptionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCallHistoryTab(LanguageProvider lp) {
    return Consumer<CallProvider>(
      builder: (context, callProvider, child) {
        if (callProvider.callHistory.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.history,
                  size: 64,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  lp.translate('no_call_history'),
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16.0),
          itemCount: callProvider.callHistory.length,
          itemBuilder: (context, index) {
            final call = callProvider.callHistory[index];
            return _buildCallHistoryItem(call, lp);
          },
        );
      },
    );
  }

  Widget _buildCallHistoryItem(Map<String, dynamic> call, LanguageProvider lp) {
    final callType = call['call_type'] ?? 'unknown';
    final status = call['status'] ?? 'ended';
    final duration = call['duration'] ?? 0;
    final startedAt = call['started_at'] ?? '';

    String callTypeLabel = lp.translate('calls');
    IconData icon = Icons.phone;
    Color color = Colors.blue;

    switch (callType) {
      case 'ai_practice':
        callTypeLabel = lp.translate('practice_ai');
        icon = Icons.smart_toy;
        color = Colors.blue;
        break;
      case 'counselor':
        callTypeLabel = lp.translate('counselor');
        icon = Icons.people;
        color = Colors.green;
        break;
      case 'emergency':
        callTypeLabel = lp.translate('emergency_call');
        icon = Icons.emergency;
        color = Colors.red;
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color),
        ),
        title: Text(callTypeLabel),
        subtitle: Text(
          '${lp.translate('duration')}: ${_formatDuration(duration, lp)}\n'
          '${lp.translate('status')}: ${status}',
        ),
        trailing: Text(
          _formatDate(startedAt, lp),
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  String _formatDuration(int seconds, LanguageProvider lp) {
    if (seconds < 60) {
      return '${seconds}s';
    }
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes}m ${secs}s';
  }

  String _formatDate(String dateStr, LanguageProvider lp) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inDays == 0) {
        return lp.translate('today');
      } else if (difference.inDays == 1) {
        return lp.translate('yesterday');
      } else if (difference.inDays < 7) {
        return '${difference.inDays} ${lp.translate('days_ago')}';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return dateStr;
    }
  }

  Future<void> _startAIPracticeCall(LanguageProvider lp) async {
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    
    try {
      final callId = await callProvider.createCall(
        callType: CallType.aiPractice,
        language: callProvider.language,
      );

      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => CallScreenSimple(
              callId: callId,
              callType: 'ai_practice',
              calleeName: 'AI Assistant',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${lp.translate('failed_start_call')}: $e')),
        );
      }
    }
  }

  Future<void> _showCounselorSelection(LanguageProvider lp) async {
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    
    if (callProvider.availableCounselors.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(lp.translate('no_counselors')),
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              lp.translate('select_counselor'),
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...callProvider.availableCounselors.map((counselor) {
              return ListTile(
                leading: const CircleAvatar(
                  child: Icon(Icons.person),
                ),
                title: Text(counselor['name'] ?? lp.translate('counselor')),
                subtitle: Text(
                  '${lp.translate('languages')}: ${(counselor['languages'] as List?)?.join(', ') ?? 'N/A'}',
                ),
                trailing: const Icon(Icons.phone),
                onTap: () {
                  Navigator.pop(context);
                  _startCounselorCall(counselor['id'], lp);
                },
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Future<void> _startCounselorCall(String counselorId, LanguageProvider lp) async {
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    
    try {
      final callId = await callProvider.createCall(
        callType: CallType.counselor,
        calleeId: counselorId,
        language: callProvider.language,
      );

      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => CallScreenSimple(
              callId: callId,
              callType: 'counselor',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${lp.translate('failed_start_call')}: $e')),
        );
      }
    }
  }

  Future<void> _startEmergencyCall(LanguageProvider lp) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(lp.translate('emergency_call')),
        content: Text(
          lp.translate('emergency_confirm_msg'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(lp.translate('cancel')),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(lp.translate('emergency_call'), style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final callProvider = Provider.of<CallProvider>(context, listen: false);
      
      try {
        final callId = await callProvider.createCall(
          callType: CallType.emergency,
          language: callProvider.language,
        );

        if (mounted) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => CallScreenSimple(
                callId: callId,
                callType: 'emergency',
              ),
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${lp.translate('failed_emergency_call')}: $e')),
          );
        }
      }
    }
  }
}
