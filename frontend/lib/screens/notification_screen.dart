import 'package:flutter/material.dart';
import 'login_screen.dart'; // For AppColors
import 'package:provider/provider.dart';
import '../providers/language_provider.dart';

class NotificationScreen extends StatelessWidget {
  const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();

    return Scaffold(
      backgroundColor: AppColors.creamYellow,
      appBar: AppBar(
        backgroundColor: AppColors.creamYellow,
        elevation: 0,
        title: Text(
          lp.translate('notifications'),
          style: const TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            // Today Section
            _buildSectionHeader(lp.translate('today')),
            _buildNotificationCard(
              icon: Icons.mood,
              title: lp.translate('notif_daily_checkin_title'),
              message: lp.translate('notif_daily_checkin_msg'),
              time: '2 ${lp.translate('hours_ago')}',
              isRead: false,
              color: AppColors.darkGreen,
            ),
            const SizedBox(height: 12),
            _buildNotificationCard(
              icon: Icons.insights,
              title: lp.translate('notif_weekly_report_title'),
              message: lp.translate('notif_weekly_report_msg'),
              time: '5 ${lp.translate('hours_ago')}',
              isRead: true,
              color: AppColors.paleSageGreen,
            ),
            const SizedBox(height: 24),
            
            // Yesterday Section
            _buildSectionHeader(lp.translate('yesterday')),
            _buildNotificationCard(
              icon: Icons.favorite,
              title: lp.translate('notif_mood_trend_title'),
              message: lp.translate('notif_mood_trend_msg'),
              time: lp.translate('yesterday'),
              isRead: true,
              color: AppColors.lightPeach,
            ),
            const SizedBox(height: 12),
            _buildNotificationCard(
              icon: Icons.chat_bubble,
              title: lp.translate('notif_sahana_msg_title'),
              message: lp.translate('notif_sahana_msg_msg'),
              time: lp.translate('yesterday'),
              isRead: true,
              color: AppColors.veryLightBlue,
            ),
            const SizedBox(height: 24),
            
            // This Week Section
            _buildSectionHeader(lp.translate('this_week')),
            _buildNotificationCard(
              icon: Icons.phone,
              title: lp.translate('notif_call_rem_title'),
              message: lp.translate('notif_call_rem_msg'),
              time: '3 ${lp.translate('days_ago')}',
              isRead: true,
              color: AppColors.darkGreen,
            ),
            const SizedBox(height: 12),
            _buildNotificationCard(
              icon: Icons.warning,
              title: lp.translate('notif_wellness_tip_title'),
              message: lp.translate('notif_wellness_tip_msg'),
              time: '5 ${lp.translate('days_ago')}',
              isRead: true,
              color: AppColors.paleSageGreen,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.black87,
        ),
      ),
    );
  }

  Widget _buildNotificationCard({
    required IconData icon,
    required String title,
    required String message,
    required String time,
    required bool isRead,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: color,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: isRead ? FontWeight.w500 : FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ),
                    if (!isRead)
                      Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          color: AppColors.darkGreen,
                          shape: BoxShape.circle,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  message,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                    fontWeight: isRead ? FontWeight.normal : FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  time,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

