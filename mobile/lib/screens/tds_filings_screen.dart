import 'package:flutter/material.dart';

/// TDS Filings Screen
class TdsFilingsScreen extends StatefulWidget {
  const TdsFilingsScreen({super.key});

  @override
  State<TdsFilingsScreen> createState() => _TdsFilingsScreenState();
}

class _TdsFilingsScreenState extends State<TdsFilingsScreen> {
  final List<Map<String, dynamic>> _tdsReturns = [
    {
      'id': '1',
      'return_type': '24Q',
      'financial_year': '2024-25',
      'quarter': 'Q3',
      'status': 'draft',
      'tan_number': 'ABCD12345E',
      'total_deducted': 125000,
      'total_deposited': 125000,
    },
    {
      'id': '2',
      'return_type': '26Q',
      'financial_year': '2024-25',
      'quarter': 'Q2',
      'status': 'filed',
      'tan_number': 'ABCD12345E',
      'total_deducted': 85000,
      'total_deposited': 85000,
    },
    {
      'id': '3',
      'return_type': '27Q',
      'financial_year': '2023-24',
      'quarter': 'Q4',
      'status': 'filed',
      'tan_number': 'ABCD12345E',
      'total_deducted': 45000,
      'total_deposited': 45000,
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

  Color _getReturnTypeColor(String type) {
    switch (type) {
      case '24Q':
        return Colors.blue;
      case '26Q':
        return Colors.purple;
      case '27Q':
        return Colors.teal;
      case '27EQ':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TDS Returns'),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Stats Cards
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        'Total Returns',
                        '${_tdsReturns.length}',
                        Colors.indigo,
                        Icons.description,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildStatCard(
                        'Filed',
                        '${_tdsReturns.where((r) => r['status'] == 'filed').length}',
                        Colors.green,
                        Icons.check_circle,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        'Total Deducted',
                        '₹${(_tdsReturns.fold<int>(0, (s, r) => s + (r['total_deducted'] as int)) / 1000).toStringAsFixed(0)}K',
                        Colors.teal,
                        Icons.trending_up,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildStatCard(
                        'Total Deposited',
                        '₹${(_tdsReturns.fold<int>(0, (s, r) => s + (r['total_deposited'] as int)) / 1000).toStringAsFixed(0)}K',
                        Colors.cyan,
                        Icons.account_balance,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Returns List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _tdsReturns.length,
              itemBuilder: (context, index) {
                final ret = _tdsReturns[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: _getReturnTypeColor(ret['return_type']).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                ret['return_type'],
                                style: TextStyle(
                                  color: _getReturnTypeColor(ret['return_type']),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${ret['financial_year']} - ${ret['quarter']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: _getStatusColor(ret['status']).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                ret['status'].toString().toUpperCase(),
                                style: TextStyle(
                                  color: _getStatusColor(ret['status']),
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Icon(Icons.badge, size: 16, color: Colors.grey[600]),
                            const SizedBox(width: 4),
                            Text(
                              'TAN: ${ret['tan_number']}',
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                                fontFamily: 'monospace',
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Deducted',
                                    style: TextStyle(
                                      color: Colors.grey[600],
                                      fontSize: 12,
                                    ),
                                  ),
                                  Text(
                                    '₹${(ret['total_deducted'] as int).toStringAsFixed(0)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Deposited',
                                    style: TextStyle(
                                      color: Colors.grey[600],
                                      fontSize: 12,
                                    ),
                                  ),
                                  Text(
                                    '₹${(ret['total_deposited'] as int).toStringAsFixed(0)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showNewReturnDialog(context),
        icon: const Icon(Icons.add),
        label: const Text('New TDS'),
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
      child: Row(
        children: [
          Icon(icon, color: Colors.white, size: 28),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.8),
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showNewReturnDialog(BuildContext context) {
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
              'New TDS Return',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Return Type',
                border: OutlineInputBorder(),
              ),
              items: [
                const DropdownMenuItem(value: '24Q', child: Text('Form 24Q - Salary')),
                const DropdownMenuItem(value: '26Q', child: Text('Form 26Q - Non-Salary')),
                const DropdownMenuItem(value: '27Q', child: Text('Form 27Q - NRI')),
                const DropdownMenuItem(value: '27EQ', child: Text('Form 27EQ - TCS')),
              ],
              onChanged: (value) {},
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Financial Year',
                      border: OutlineInputBorder(),
                    ),
                    items: ['2024-25', '2023-24']
                        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                        .toList(),
                    onChanged: (value) {},
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Quarter',
                      border: OutlineInputBorder(),
                    ),
                    items: ['Q1', 'Q2', 'Q3', 'Q4']
                        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                        .toList(),
                    onChanged: (value) {},
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              decoration: const InputDecoration(
                labelText: 'TAN Number',
                border: OutlineInputBorder(),
              ),
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
                  child: Text('Create Return'),
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
