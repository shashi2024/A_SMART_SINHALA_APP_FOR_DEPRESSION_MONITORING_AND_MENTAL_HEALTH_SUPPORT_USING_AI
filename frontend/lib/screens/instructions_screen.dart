import 'package:flutter/material.dart';
import 'login_screen.dart'; // For AppColors
import 'package:provider/provider.dart';
import '../providers/language_provider.dart';

class InstructionsScreen extends StatelessWidget {
  const InstructionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lp = context.watch<LanguageProvider>();

    return Scaffold(
      backgroundColor: AppColors.creamYellow,
      appBar: AppBar(
        backgroundColor: AppColors.creamYellow,
        elevation: 0,
        title: Text(
          lp.translate('instructions'),
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
          padding: const EdgeInsets.all(20.0),
          children: [
            // Welcome Card
            Container(
              padding: const EdgeInsets.all(24.0),
              decoration: BoxDecoration(
                color: AppColors.darkGreen,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lp.translate('welcome_sahana'),
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    lp.translate('welcome_sahana_desc'),
                    style: const TextStyle(
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
              title: lp.translate('getting_started'),
              color: AppColors.paleSageGreen,
              items: [
                lp.translate('gs_item1'),
                lp.translate('gs_item2'),
                lp.translate('gs_item3'),
                lp.translate('gs_item4'),
              ],
            ),
            const SizedBox(height: 16),
            
            // Mood Check-in Section
            _buildSectionCard(
              icon: Icons.mood,
              title: lp.translate('daily_mood_checkin'),
              color: AppColors.lightPeach,
              items: [
                lp.translate('mood_item1'),
                lp.translate('mood_item2'),
                lp.translate('mood_item3'),
                lp.translate('mood_item4'),
              ],
            ),
            const SizedBox(height: 16),
            
            // Chatting with Sahana Section
            _buildSectionCard(
              icon: Icons.chat_bubble_outline,
              title: lp.translate('chatting_sahana'),
              color: AppColors.veryLightBlue,
              items: [
                lp.translate('chat_item1'),
                lp.translate('chat_item2'),
                lp.translate('chat_item3'),
                lp.translate('chat_item4'),
              ],
            ),
            const SizedBox(height: 16),
            
            // Calls Section
            _buildSectionCard(
              icon: Icons.phone,
              title: lp.translate('making_calls'),
              color: AppColors.darkGreen,
              items: [
                lp.translate('calls_item1'),
                lp.translate('calls_item2'),
                lp.translate('calls_item3'),
                lp.translate('calls_item4'),
              ],
            ),
            const SizedBox(height: 16),
            
            // Privacy & Safety Section
            _buildSectionCard(
              icon: Icons.lock_outline,
              title: lp.translate('privacy_safety'),
              color: AppColors.paleSageGreen,
              items: [
                lp.translate('privacy_item1'),
                lp.translate('privacy_item2'),
                lp.translate('privacy_item3'),
                lp.translate('privacy_item4'),
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
                      const Icon(
                        Icons.lightbulb_outline,
                        color: AppColors.darkGreen,
                        size: 28,
                      ),
                      const SizedBox(width: 12),
                      Text(
                        lp.translate('tips_best_experience'),
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildTipItem(lp.translate('tips_item1')),
                  _buildTipItem(lp.translate('tips_item2')),
                  _buildTipItem(lp.translate('tips_item3')),
                  _buildTipItem(lp.translate('tips_item4')),
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

