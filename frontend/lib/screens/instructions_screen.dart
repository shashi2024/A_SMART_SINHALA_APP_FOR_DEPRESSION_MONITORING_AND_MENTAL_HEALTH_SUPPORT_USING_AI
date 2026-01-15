import 'package:flutter/material.dart';
import 'login_screen.dart'; // For AppColors

class InstructionsScreen extends StatelessWidget {
  const InstructionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.creamYellow,
      appBar: AppBar(
        backgroundColor: AppColors.creamYellow,
        elevation: 0,
        title: const Text(
          'Instructions',
          style: TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20.0),
          children: [
            // Welcome Card
            Container(
              padding: const EdgeInsets.all(24.0),
              decoration: BoxDecoration(
                color: AppColors.darkGreen,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome to Sahana!',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Your mental health companion designed to support you through your journey.',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Getting Started Section
            _buildSectionCard(
              icon: Icons.play_circle_outline,
              title: 'Getting Started',
              color: AppColors.paleSageGreen,
              items: [
                'Complete your daily mood check-in',
                'Chat with Sahana, your AI companion',
                'Track your weekly energy trends',
                'Schedule calls with counselors when needed',
              ],
            ),
            const SizedBox(height: 16),
            
            // Mood Check-in Section
            _buildSectionCard(
              icon: Icons.mood,
              title: 'Daily Mood Check-in',
              color: AppColors.lightPeach,
              items: [
                'Select how you\'re feeling from the mood options',
                'Be honest about your current emotional state',
                'Your mood data helps Sahana understand you better',
                'Regular check-ins help track your progress',
              ],
            ),
            const SizedBox(height: 16),
            
            // Chatting with Sahana Section
            _buildSectionCard(
              icon: Icons.chat_bubble_outline,
              title: 'Chatting with Sahana',
              color: AppColors.veryLightBlue,
              items: [
                'Tap the Sahana icon in the bottom navigation',
                'Share your thoughts, feelings, or concerns',
                'Sahana provides empathetic responses and support',
                'Your conversations are private and secure',
              ],
            ),
            const SizedBox(height: 16),
            
            // Calls Section
            _buildSectionCard(
              icon: Icons.phone,
              title: 'Making Calls',
              color: AppColors.darkGreen,
              items: [
                'Practice with AI for voice interactions',
                'Schedule calls with professional counselors',
                'Use emergency calls for urgent support',
                'All calls are confidential and secure',
              ],
            ),
            const SizedBox(height: 16),
            
            // Privacy & Safety Section
            _buildSectionCard(
              icon: Icons.lock_outline,
              title: 'Privacy & Safety',
              color: AppColors.paleSageGreen,
              items: [
                'All your data is encrypted and secure',
                'Your conversations are confidential',
                'You can delete your data at any time',
                'We comply with mental health data protection standards',
              ],
            ),
            const SizedBox(height: 24),
            
            // Tips Card
            Container(
              padding: const EdgeInsets.all(20.0),
              decoration: BoxDecoration(
                color: AppColors.lightPeach,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: AppColors.darkGreen.withOpacity(0.3),
                  width: 2,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.lightbulb_outline,
                        color: AppColors.darkGreen,
                        size: 28,
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Tips for Best Experience',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildTipItem('Check in daily for accurate tracking'),
                  _buildTipItem('Be open and honest with Sahana'),
                  _buildTipItem('Review your weekly trends regularly'),
                  _buildTipItem('Reach out to counselors when needed'),
                ],
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionCard({
    required IconData icon,
    required String title,
    required Color color,
    required List<String> items,
  }) {
    return Container(
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
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...items.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 6, right: 12),
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: color,
                        shape: BoxShape.circle,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        item,
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
    );
  }

  Widget _buildTipItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.check_circle_outline,
            color: AppColors.darkGreen,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 15,
                color: Colors.black87,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

