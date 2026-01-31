import 'package:flutter/material.dart';

/// ITR Filings Screen
class ItrFilingsScreen extends StatefulWidget {
  const ItrFilingsScreen({super.key});

  @override
  State<ItrFilingsScreen> createState() => _ItrFilingsScreenState();
}

class _ItrFilingsScreenState extends State<ItrFilingsScreen> {
  final List<Map<String, dynamic>> _itrFilings = [
    {
      'id': '1',
      'assessment_year': '2024-25',
      'filing_type': 'ITR-1',
      'status': 'draft',
      'total_income': 850000,
      'tax_payable': 25000,
    },
    {
      'id': '2',
      'assessment_year': '2023-24',
      'filing_type': 'ITR-1',
      'status': 'filed',
      'total_income': 780000,
      'tax_payable': 18000,
    },
  ];

  Color _getStatusColor(String status) {
    switch (status) {
      case 'filed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'draft':
        return Colors.grey;
      default:
        return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ITR Filings'),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Stats Cards
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Total',
                    '${_itrFilings.length}',
                    Colors.blue,
                    Icons.description,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Filed',
                    '${_itrFilings.where((f) => f['status'] == 'filed').length}',
                    Colors.green,
                    Icons.check_circle,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Pending',
                    '${_itrFilings.where((f) => f['status'] != 'filed').length}',
                    Colors.orange,
                    Icons.pending,
                  ),
                ),
              ],
            ),
          ),
          // Filings List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _itrFilings.length,
              itemBuilder: (context, index) {
                final filing = _itrFilings[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _getStatusColor(filing['status']).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.description,
                        color: _getStatusColor(filing['status']),
                      ),
                    ),
                    title: Text(
                      '${filing['filing_type']} - ${filing['assessment_year']}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Income: ₹${(filing['total_income'] as int).toStringAsFixed(0)} • Tax: ₹${(filing['tax_payable'] as int).toStringAsFixed(0)}',
                    ),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: _getStatusColor(filing['status']).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        filing['status'].toString().toUpperCase(),
                        style: TextStyle(
                          color: _getStatusColor(filing['status']),
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    onTap: () {
                      // Navigate to detail
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          _showNewFilingDialog(context);
        },
        icon: const Icon(Icons.add),
        label: const Text('New ITR'),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color, color.withOpacity(0.7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  void _showNewFilingDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
          left: 16,
          right: 16,
          top: 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'New ITR Filing',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Assessment Year',
                border: OutlineInputBorder(),
              ),
              items: ['2024-25', '2023-24', '2022-23']
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (value) {},
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'ITR Type',
                border: OutlineInputBorder(),
              ),
              items: ['ITR-1', 'ITR-2', 'ITR-3', 'ITR-4']
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (value) {},
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('Start Filing'),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
