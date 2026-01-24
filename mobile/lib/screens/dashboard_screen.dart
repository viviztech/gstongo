import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authService = AuthService();
    final apiService = ApiService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => context.go('/profile'),
          ),
        ],
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _fetchDashboardData(apiService),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final data = snapshot.data!;
            final user = data['user'] as Map<String, dynamic>?;
            final filings = data['filings'] as List<dynamic>;
            final pendingAmount = data['pendingAmount'] as double;

            final pendingFilings = filings.where((f) => f['status'] == 'pending').length;
            final filedFilings = filings.where((f) => f['status'] == 'filed').length;

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome to GSTONGO',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),
                  _buildQuickActions(context),
                  const SizedBox(height: 24),
                  _buildFilingStatus(context, pendingFilings, filedFilings),
                  const SizedBox(height: 24),
                  _buildRecentActivity(context, filings),
                ],
              ),
            );
          }
        },
      ),
      drawer: _buildDrawer(context, authService),
    );
  }

  Future<Map<String, dynamic>> _fetchDashboardData(ApiService apiService) async {
    try {
      final userResponse = await apiService.get('/auth/me/');
      final filingsResponse = await apiService.get('/gst/filings/');
      final invoicesResponse = await apiService.get('/invoices/');

      final filings = filingsResponse['results'] as List<dynamic>;
      final invoices = invoicesResponse['results'] as List<dynamic>;
      final pendingAmount = invoices
          .where((i) => i['status'] != 'paid')
          .fold(0.0, (sum, i) => sum + double.parse(i['total_amount'].toString()));

      return {
        'user': userResponse,
        'filings': filings,
        'pendingAmount': pendingAmount,
      };
    } catch (e) {
      // Return mock data if API fails
      return {
        'user': {'first_name': 'User'},
        'filings': [
          {'id': 1, 'type': 'GSTR-1', 'period': 'Dec 2024', 'status': 'pending'},
          {'id': 2, 'type': 'GSTR-3B', 'period': 'Dec 2024', 'status': 'pending'},
          {'id': 3, 'type': 'GSTR-1', 'period': 'Nov 2024', 'status': 'filed'},
        ],
        'pendingAmount': 150.0,
      };
    }
  }

  Widget _buildQuickActions(BuildContext context) {
    final actions = [
      {'icon': Icons.upload_file, 'label': 'Upload GST Data', 'color': Colors.blue, 'route': '/filings'},
      {'icon': Icons.receipt, 'label': 'View Invoices', 'color': Colors.green, 'route': '/invoices'},
      {'icon': Icons.payment, 'label': 'Pay Now', 'color': Colors.orange, 'route': '/invoices'},
      {'icon': Icons.description, 'label': 'My Filings', 'color': Colors.purple, 'route': '/filings'},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.2,
      ),
      itemCount: actions.length,
      itemBuilder: (context, index) {
        final action = actions[index];
        return Card(
          child: InkWell(
            onTap: () => context.go(action['route'] as String),
            borderRadius: BorderRadius.circular(12),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  action['icon'] as IconData,
                  size: 40,
                  color: action['color'] as Color,
                ),
                const SizedBox(height: 8),
                Text(
                  action['label'] as String,
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildFilingStatus(BuildContext context, int pending, int filed) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Filing Status',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildStatusTile(context, 'GSTR-1', 'Due: 11th Jan', Icons.pending, Colors.orange),
            _buildStatusTile(context, 'GSTR-3B', 'Due: 20th Jan', Icons.pending, Colors.orange),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(context, 'Pending', pending.toString(), Colors.orange),
                _buildStatItem(context, 'Filed', filed.toString(), Colors.green),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusTile(BuildContext context, String title, String subtitle, IconData icon, Color color) {
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {},
    );
  }

  Widget _buildStatItem(BuildContext context, String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(label, style: Theme.of(context).textTheme.bodyMedium),
      ],
    );
  }

  Widget _buildRecentActivity(BuildContext context, List<dynamic> filings) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Recent Activity',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            if (filings.isNotEmpty)
              ...filings.take(3).map((filing) => _buildActivityTile(
                context,
                '${filing['type']} - ${filing['period']}',
                filing['status'] as String,
              ))
            else
              _buildActivityTile(context, 'No filings yet', 'info'),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityTile(BuildContext context, String title, String status) {
    final isFiled = status == 'filed';
    return ListTile(
      leading: CircleAvatar(
        radius: 16,
        backgroundColor: isFiled ? Colors.green : Colors.orange,
        child: Icon(
          isFiled ? Icons.check : Icons.pending,
          size: 16,
          color: Colors.white,
        ),
      ),
      title: Text(title),
      subtitle: Text(status),
      contentPadding: EdgeInsets.zero,
    );
  }

  Drawer _buildDrawer(BuildContext context, AuthService authService) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          const UserAccountsDrawerHeader(
            decoration: BoxDecoration(
              color: Color(0xFF2563EB),
            ),
            accountName: Text('John Doe'),
            accountEmail: Text('john@example.com'),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                'JD',
                style: TextStyle(
                  color: Color(0xFF2563EB),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Dashboard'),
            onTap: () => context.go('/dashboard'),
          ),
          ListTile(
            leading: const Icon(Icons.description),
            title: const Text('My Filings'),
            onTap: () => context.go('/filings'),
          ),
          ListTile(
            leading: const Icon(Icons.receipt),
            title: const Text('Invoices'),
            onTap: () => context.go('/invoices'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.person),
            title: const Text('Profile'),
            onTap: () => context.go('/profile'),
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Logout'),
            onTap: () async {
              await authService.logout();
              context.go('/login');
            },
          ),
        ],
      ),
    );
  }
}
