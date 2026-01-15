import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/digital_twin_provider.dart';
import 'login_screen.dart'; // For AppColors
import 'login_screen.dart' as login_screen; // For navigation

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    // Load profile when screen is accessed
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final twinProvider = Provider.of<DigitalTwinProvider>(context, listen: false);
      if (twinProvider.profile == null) {
        twinProvider.loadProfile();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.creamYellow,
      appBar: AppBar(
        backgroundColor: AppColors.creamYellow,
        elevation: 0,
        title: const Text(
          'Profile',
          style: TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
      ),
      body: Consumer2<AuthProvider, DigitalTwinProvider>(
        builder: (context, authProvider, twinProvider, child) {
          final user = authProvider.user;
          String displayName = user?.username ?? 'User';
          if (displayName.contains('@')) {
            displayName = displayName.split('@').first;
          } else {
            displayName = displayName.split(' ').first;
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // User Profile Card
                Container(
                  padding: const EdgeInsets.all(24.0),
                  decoration: BoxDecoration(
                    color: AppColors.darkGreen,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    children: [
                      Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Icon(
                          Icons.person,
                          size: 60,
                          color: AppColors.darkGreen,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        displayName,
                        style: const TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      if (user?.email != null && user!.email.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(
                          user.email,
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.white.withOpacity(0.9),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // User Details Card
                Container(
                  padding: const EdgeInsets.all(20.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.1),
                        spreadRadius: 1,
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.info_outline,
                            color: AppColors.darkGreen,
                            size: 24,
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'User Details',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      _buildDetailRow(
                        'User ID',
                        user?.id.toString() ?? 'N/A',
                        Icons.badge,
                        AppColors.darkGreen,
                      ),
                      const Divider(height: 32),
                      _buildDetailRow(
                        'Username',
                        user?.username ?? 'N/A',
                        Icons.person_outline,
                        AppColors.paleSageGreen,
                      ),
                      const Divider(height: 32),
                      _buildDetailRow(
                        'Email',
                        user?.email ?? 'N/A',
                        Icons.email_outlined,
                        AppColors.lightPeach,
                      ),
                      const Divider(height: 32),
                      _buildDetailRow(
                        'Account Type',
                        user?.isAdmin == true ? 'Admin' : 'User',
                        Icons.admin_panel_settings_outlined,
                        AppColors.veryLightBlue,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Digital Twin Profile Card (if available)
                if (twinProvider.profile != null)
                  Container(
                    padding: const EdgeInsets.all(20.0),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.1),
                          spreadRadius: 1,
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.psychology_outlined,
                              color: AppColors.darkGreen,
                              size: 24,
                            ),
                            const SizedBox(width: 12),
                            const Text(
                              'Mental Health Profile',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        _buildProfileRow(
                          'Total Sessions',
                          twinProvider.profile!['total_sessions']?.toString() ?? '0',
                        ),
                        const Divider(height: 32),
                        _buildProfileRow(
                          'Average Depression Score',
                          twinProvider.profile!['average_depression_score'] != null
                              ? '${(twinProvider.profile!['average_depression_score'] * 100).toStringAsFixed(1)}%'
                              : 'N/A',
                        ),
                        const Divider(height: 32),
                        _buildProfileRow(
                          'Risk Level',
                          twinProvider.profile!['risk_level'] ?? 'Low',
                        ),
                      ],
                    ),
                  ),
                if (twinProvider.profile != null) const SizedBox(height: 24),

                // Risk Factors Card (if available)
                if (twinProvider.riskFactors != null &&
                    twinProvider.riskFactors!.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(20.0),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.1),
                          spreadRadius: 1,
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                          Row(
                            children: [
                              Icon(
                                Icons.warning_amber_rounded,
                                color: Colors.orange.shade700,
                                size: 24,
                              ),
                            const SizedBox(width: 12),
                            const Text(
                              'Risk Factors',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        ...twinProvider.riskFactors!.map((factor) => Padding(
                              padding: const EdgeInsets.only(bottom: 12.0),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    Icons.circle,
                                    size: 8,
                                    color: Colors.orange.shade700,
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      factor,
                                      style: TextStyle(
                                        fontSize: 15,
                                        color: Colors.grey[800],
                                        height: 1.5,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            )),
                      ],
                    ),
                  ),
                if (twinProvider.riskFactors != null &&
                    twinProvider.riskFactors!.isNotEmpty)
                  const SizedBox(height: 24),

                // Logout Button
                Container(
                  height: 56,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.red.withOpacity(0.2),
                        spreadRadius: 1,
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      // Show confirmation dialog
                      final shouldLogout = await showDialog<bool>(
                        context: context,
                        builder: (BuildContext context) {
                          return AlertDialog(
                            title: const Text('Logout'),
                            content: const Text('Are you sure you want to logout?'),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.of(context).pop(false),
                                child: Text(
                                  'Cancel',
                                  style: TextStyle(color: Colors.grey[600]),
                                ),
                              ),
                              ElevatedButton(
                                onPressed: () => Navigator.of(context).pop(true),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red,
                                  foregroundColor: Colors.white,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: const Text('Logout'),
                              ),
                            ],
                          );
                        },
                      );

                      if (shouldLogout == true) {
                        await authProvider.logout();
                        if (context.mounted) {
                          Navigator.of(context).pushReplacement(
                            MaterialPageRoute(
                              builder: (context) => const login_screen.LoginScreen(),
                            ),
                          );
                        }
                      }
                    },
                    icon: const Icon(Icons.logout, color: Colors.white),
                    label: const Text(
                      'Logout',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 0,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, IconData icon, Color iconColor) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: iconColor,
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.black87,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildProfileRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 15,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            color: Colors.black87,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

