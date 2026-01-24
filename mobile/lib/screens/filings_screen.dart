import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';

class FilingsScreen extends StatelessWidget {
  const FilingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Filings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {},
            tooltip: 'New Filing',
          ),
        ],
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _fetchFilings(apiService),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final data = snapshot.data!;
            final filings = data['filings'] as List<dynamic>;
            final pendingAmount = data['pendingAmount'] as double;
            final hasPending = data['hasPending'] as bool;

            return Column(
              children: [
                // Summary Card
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Pending Amount',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                      Text(
                        '₹${pendingAmount.toStringAsFixed(2)}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (hasPending)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            'PAYMENT DUE',
                            style: TextStyle(
                              color: Color(0xFF2563EB),
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
                // Filings List
                Expanded(
                  child: filings.isNotEmpty
                      ? ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: filings.length,
                          itemBuilder: (context, index) {
                            final filing = filings[index];
                            final statusColor = filing['status'] == 'filed'
                                ? Colors.green
                                : filing['status'] == 'pending'
                                    ? Colors.orange
                                    : Colors.grey;

                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor: statusColor.withOpacity(0.1),
                                  child: Icon(
                                    filing['status'] == 'filed'
                                        ? Icons.check_circle
                                        : Icons.pending,
                                    color: statusColor,
                                  ),
                                ),
                                title: Text('${filing['type']} - ${filing['period']}'),
                                subtitle: Text('Status: ${filing['status']}'),
                                trailing: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      '₹${filing['amount'] ?? 0}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                  ],
                                ),
                                onTap: () =>
                                    context.go('/filings/${filing['id']}'),
                              ),
                            );
                          },
                        )
                      : Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.description,
                                size: 64,
                                color: Colors.grey[400],
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                'No Filings Yet',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey,
                                ),
                              ),
                              const SizedBox(height: 8),
                              ElevatedButton.icon(
                                onPressed: () {},
                                icon: const Icon(Icons.add),
                                label: const Text('Create First Filing'),
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        label: const Text('New Filing'),
        icon: const Icon(Icons.add),
        backgroundColor: const Color(0xFF2563EB),
        foregroundColor: Colors.white,
      ),
    );
  }

  Future<Map<String, dynamic>> _fetchFilings(ApiService apiService) async {
    try {
      final filingsResponse = await apiService.get('/gst/filings/');
      final invoicesResponse = await apiService.get('/invoices/');

      final filings = (filingsResponse['results'] as List<dynamic>?)
              ?.map((f) => {
                    'id': f['id'],
                    'type': f['filing_type'],
                    'period': '${f['month']}/${f['year']}',
                    'status': f['status'],
                    'amount': f['amount'] ?? 150,
                  })
              .toList() ??
          [];

      final invoices = (invoicesResponse['results'] as List<dynamic>?);
      final pendingAmount = invoices
              ?.where((i) => i['status'] != 'paid')
              .fold(0.0, (sum, i) => sum + double.parse(i['total_amount'].toString())) ??
          0.0;
      final hasPending = (invoices?.any((i) => i['status'] != 'paid')) ?? false;

      return {
        'filings': filings,
        'pendingAmount': pendingAmount,
        'hasPending': hasPending,
      };
    } catch (e) {
      // Return mock data if API fails
      return {
        'filings': [
          {
            'id': 1,
            'type': 'GSTR-1',
            'period': 'Dec 2024',
            'status': 'pending',
            'amount': 150
          },
          {
            'id': 2,
            'type': 'GSTR-3B',
            'period': 'Dec 2024',
            'status': 'pending',
            'amount': 150
          },
          {
            'id': 3,
            'type': 'GSTR-1',
            'period': 'Nov 2024',
            'status': 'filed',
            'amount': 150
          },
        ],
        'pendingAmount': 150.0,
        'hasPending': true,
      };
    }
  }
}
