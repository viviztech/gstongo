import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class FilingsScreen extends StatelessWidget {
  const FilingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final filings = [
      {'id': 1, 'type': 'GSTR-1', 'period': 'Dec 2024', 'status': 'Pending', 'amount': 150},
      {'id': 2, 'type': 'GSTR-3B', 'period': 'Dec 2024', 'status': 'Pending', 'amount': 150},
      {'id': 3, 'type': 'GSTR-1', 'period': 'Nov 2024', 'status': 'Filed', 'amount': 150},
      {'id': 4, 'type': 'GSTR-3B', 'period': 'Nov 2024', 'status': 'Filed', 'amount': 150},
    ];

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
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filings.length,
        itemBuilder: (context, index) {
          final filing = filings[index];
          final statusColor = filing['status'] == 'Filed' 
              ? Colors.green 
              : Colors.orange;
          
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: statusColor.withOpacity(0.1),
                child: Icon(
                  filing['status'] == 'Filed' 
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
                    '₹${filing['amount']}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              onTap: () => context.go('/filings/${filing['id']}'),
            ),
          );
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
}
