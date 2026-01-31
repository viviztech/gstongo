import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Dashboard Screen with navigation to all services
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('GSTONGO'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push('/profile'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Section
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).primaryColor,
                    Theme.of(context).primaryColor.withOpacity(0.8),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Welcome Back!',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Manage your tax filings effortlessly',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Quick Stats
                  Row(
                    children: [
                      Expanded(
                        child: _buildQuickStat('Pending', '3', Colors.orange),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildQuickStat('Filed', '12', Colors.green),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildQuickStat('Due Soon', '2', Colors.red),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Services Grid
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Services',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 3,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    children: [
                      _buildServiceItem(
                        'GST Filing',
                        Icons.description,
                        Colors.blue,
                        () => context.push('/filings'),
                      ),
                      _buildServiceItem(
                        'ITR Filing',
                        Icons.calculate,
                        Colors.green,
                        () => context.push('/itr'),
                      ),
                      _buildServiceItem(
                        'TDS Returns',
                        Icons.account_balance,
                        Colors.purple,
                        () => context.push('/tds'),
                      ),
                      _buildServiceItem(
                        'Business',
                        Icons.business,
                        Colors.orange,
                        () => context.push('/services'),
                      ),
                      _buildServiceItem(
                        'Vault',
                        Icons.folder,
                        Colors.teal,
                        () => context.push('/vault'),
                      ),
                      _buildServiceItem(
                        'Invoices',
                        Icons.receipt,
                        Colors.indigo,
                        () => context.push('/invoices'),
                      ),
                      _buildServiceItem(
                        'Support',
                        Icons.support_agent,
                        Colors.pink,
                        () => context.push('/support'),
                      ),
                      _buildServiceItem(
                        'Analytics',
                        Icons.analytics,
                        Colors.cyan,
                        () => context.push('/analytics'),
                      ),
                      _buildServiceItem(
                        'Profile',
                        Icons.person,
                        Colors.grey,
                        () => context.push('/profile'),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Upcoming Deadlines
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Upcoming Deadlines',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () {},
                        child: const Text('View All'),
                      ),
                    ],
                  ),
                  _buildDeadlineCard(
                    'GSTR-1',
                    'January 2025',
                    'Feb 11, 2025',
                    Colors.red,
                    '3 days left',
                  ),
                  _buildDeadlineCard(
                    'GSTR-3B',
                    'January 2025',
                    'Feb 20, 2025',
                    Colors.orange,
                    '12 days left',
                  ),
                  _buildDeadlineCard(
                    'TDS Return',
                    'Q3 2024-25',
                    'Feb 15, 2025',
                    Colors.blue,
                    '7 days left',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Recent Activity
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Recent Activity',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildActivityItem(
                    'GSTR-1 Filed',
                    'December 2024 filed successfully',
                    '2 hours ago',
                    Icons.check_circle,
                    Colors.green,
                  ),
                  _buildActivityItem(
                    'Payment Received',
                    'Invoice #INV-001 - ₹5,000',
                    '1 day ago',
                    Icons.payment,
                    Colors.blue,
                  ),
                  _buildActivityItem(
                    'Document Uploaded',
                    'Form 16 for AY 2024-25',
                    '2 days ago',
                    Icons.upload_file,
                    Colors.orange,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 100),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() => _currentIndex = index);
          switch (index) {
            case 0:
              break;
            case 1:
              context.push('/filings');
              break;
            case 2:
              context.push('/invoices');
              break;
            case 3:
              context.push('/analytics');
              break;
            case 4:
              context.push('/profile');
              break;
          }
        },
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.description_outlined),
            activeIcon: Icon(Icons.description),
            label: 'Filings',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_outlined),
            activeIcon: Icon(Icons.receipt),
            label: 'Invoices',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics_outlined),
            activeIcon: Icon(Icons.analytics),
            label: 'Analytics',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStat(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceItem(String label, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeadlineCard(String title, String period, String date, Color color, String remaining) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(Icons.event, color: color),
        ),
        title: Text(
          '$title - $period',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('Due: $date'),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            remaining,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActivityItem(String title, String subtitle, String time, IconData icon, Color color) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
        trailing: Text(
          time,
          style: TextStyle(color: Colors.grey[600], fontSize: 11),
        ),
      ),
    );
  }
}
