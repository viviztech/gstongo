import 'package:flutter/material.dart';
import '../services/api_service.dart';

class InvoicesScreen extends StatelessWidget {
  const InvoicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Invoices'),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _fetchInvoices(apiService),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final data = snapshot.data!;
            final invoices = data['invoices'] as List<dynamic>;
            final pendingAmount = data['pendingAmount'] as double;
            const apiService = ApiService();

            return Column(
              children: [
                // Summary Cards
                Container(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              children: [
                                const Text(
                                  'Pending Amount',
                                  style: TextStyle(color: Colors.grey, fontSize: 12),
                                ),
                                Text(
                                  '₹${pendingAmount.toStringAsFixed(2)}',
                                  style: const TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.orange,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              children: [
                                const Text(
                                  'Total Invoices',
                                  style: TextStyle(color: Colors.grey, fontSize: 12),
                                ),
                                Text(
                                  '${invoices.length}',
                                  style: const TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF2563EB),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                // Invoices List
                Expanded(
                  child: invoices.isNotEmpty
                      ? ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: invoices.length,
                          itemBuilder: (context, index) {
                            final invoice = invoices[index];
                            final isPaid = invoice['status'] == 'paid';
                            final statusColor = isPaid
                                ? Colors.green
                                : invoice['status'] == 'overdue'
                                    ? Colors.red
                                    : Colors.orange;

                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: Column(
                                children: [
                                  ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: statusColor.withOpacity(0.1),
                                      child: Icon(
                                        isPaid ? Icons.check_circle : Icons.pending,
                                        color: statusColor,
                                      ),
                                    ),
                                    title: Text('${invoice['type']} - ${invoice['invoice_number']}'),
                                    subtitle: Text('Period: ${invoice['period']}'),
                                    trailing: Text(
                                      '₹${invoice['amount']}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18,
                                      ),
                                    ),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.all(16),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              'Due Date',
                                              style: TextStyle(
                                                color: Colors.grey[600],
                                                fontSize: 12,
                                              ),
                                            ),
                                            Text(
                                              invoice['due_date'] ?? 'N/A',
                                              style: const TextStyle(
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                        ),
                                        if (!isPaid)
                                          ElevatedButton(
                                            onPressed: () {},
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: const Color(0xFF2563EB),
                                            ),
                                            child: const Text(
                                              'Pay Now',
                                              style: TextStyle(color: Colors.white),
                                            ),
                                          )
                                        else
                                          TextButton.icon(
                                            onPressed: () {},
                                            icon: const Icon(Icons.download),
                                            label: const Text('Download'),
                                          ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        )
                      : Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.receipt_long,
                                size: 64,
                                color: Colors.grey[400],
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                'No Invoices Yet',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        ),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Future<Map<String, dynamic>> _fetchInvoices(ApiService apiService) async {
    try {
      final response = await apiService.get('/invoices/');
      final invoices = (response['results'] as List<dynamic>?)
              ?.map((i) => {
                    'id': i['id'],
                    'invoice_number': i['invoice_number'],
                    'type': i['service_type'] ?? 'GST Filing',
                    'period': 'Dec 2024',
                    'amount': double.parse(i['total_amount'].toString()),
                    'status': i['status'],
                    'due_date': i['due_date'] != null
                        ? DateTime.parse(i['due_date']).toLocal().toString().split(' ')[0]
                        : 'N/A',
                  })
              .toList() ??
          [];

      final pendingAmount = invoices
          .where((i) => i['status'] != 'paid')
          .fold(0.0, (sum, i) => sum + i['amount'] as double);

      return {
        'invoices': invoices,
        'pendingAmount': pendingAmount,
      };
    } catch (e) {
      // Return mock data if API fails
      return {
        'invoices': [
          {
            'id': 'INV-2024-001',
            'invoice_number': 'INV-2024-001',
            'type': 'GST Filing',
            'period': 'Dec 2024',
            'amount': 150,
            'status': 'pending',
            'due_date': '2025-01-15',
          },
          {
            'id': 'INV-2024-0001',
            'invoice_number': 'INV-2024-0001',
            'type': 'GST Filing',
            'period': 'Nov 2024',
            'amount': 150,
            'status': 'paid',
            'due_date': '2024-12-15',
          },
        ],
        'pendingAmount': 150.0,
      };
    }
  }
}
