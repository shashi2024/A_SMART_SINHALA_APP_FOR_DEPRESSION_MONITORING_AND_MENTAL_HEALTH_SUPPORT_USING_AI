import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_provider.dart';
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calls'),
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
          _buildCallOptionsTab(),
          _buildCallHistoryTab(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.phone),
            label: 'New Call',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'History',
          ),
        ],
      ),
    );
  }

  Widget _buildCallOptionsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Start a Call',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          
          // AI Practice Call
          _buildCallOptionCard(
            icon: Icons.smart_toy,
            title: 'AI Practice Call',
            subtitle: 'Practice speaking with our AI assistant',
            color: Colors.blue,
            onTap: () => _startAIPracticeCall(),
          ),
          
          const SizedBox(height: 16),
          
          // Counselor Call
          _buildCallOptionCard(
            icon: Icons.people,
            title: 'Call a Counselor',
            subtitle: 'Connect with a professional counselor',
            color: Colors.green,
            onTap: () => _showCounselorSelection(),
          ),
          
          const SizedBox(height: 16),
          
          // Emergency Call
          _buildCallOptionCard(
            icon: Icons.emergency,
            title: 'Emergency Call',
            subtitle: 'Immediate support in crisis situations',
            color: Colors.red,
            onTap: () => _startEmergencyCall(),
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

  Widget _buildCallHistoryTab() {
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
                  'No call history',
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
            return _buildCallHistoryItem(call);
          },
        );
      },
    );
  }

  Widget _buildCallHistoryItem(Map<String, dynamic> call) {
    final callType = call['call_type'] ?? 'unknown';
    final status = call['status'] ?? 'ended';
    final duration = call['duration'] ?? 0;
    final startedAt = call['started_at'] ?? '';

    String callTypeLabel = 'Call';
    IconData icon = Icons.phone;
    Color color = Colors.blue;

    switch (callType) {
      case 'ai_practice':
        callTypeLabel = 'AI Practice';
        icon = Icons.smart_toy;
        color = Colors.blue;
        break;
      case 'counselor':
        callTypeLabel = 'Counselor';
        icon = Icons.people;
        color = Colors.green;
        break;
      case 'emergency':
        callTypeLabel = 'Emergency';
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
          'Duration: ${_formatDuration(duration)}\n'
          'Status: ${status}',
        ),
        trailing: Text(
          _formatDate(startedAt),
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  String _formatDuration(int seconds) {
    if (seconds < 60) {
      return '${seconds}s';
    }
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes}m ${secs}s';
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inDays == 0) {
        return 'Today';
      } else if (difference.inDays == 1) {
        return 'Yesterday';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} days ago';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return dateStr;
    }
  }

  Future<void> _startAIPracticeCall() async {
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
          SnackBar(content: Text('Failed to start call: $e')),
        );
      }
    }
  }

  Future<void> _showCounselorSelection() async {
    final callProvider = Provider.of<CallProvider>(context, listen: false);
    
    if (callProvider.availableCounselors.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No counselors available at the moment'),
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
            const Text(
              'Select a Counselor',
              style: TextStyle(
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
                title: Text(counselor['name'] ?? 'Counselor'),
                subtitle: Text(
                  'Languages: ${(counselor['languages'] as List?)?.join(', ') ?? 'N/A'}',
                ),
                trailing: const Icon(Icons.phone),
                onTap: () {
                  Navigator.pop(context);
                  _startCounselorCall(counselor['id']);
                },
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Future<void> _startCounselorCall(String counselorId) async {
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
          SnackBar(content: Text('Failed to start call: $e')),
        );
      }
    }
  }

  Future<void> _startEmergencyCall() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Call'),
        content: const Text(
          'This will connect you to emergency support. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Call', style: TextStyle(color: Colors.red)),
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
            SnackBar(content: Text('Failed to start emergency call: $e')),
          );
        }
      }
    }
  }
}

