import 'package:flutter/material.dart';

import '../models/employee.dart';
import '../models/letter_request.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<Employee>> _employees;
  late Future<List<LetterRequestItem>> _requests;

  @override
  void initState() {
    super.initState();
    _employees = _apiService.fetchEmployees();
    _requests = _apiService.fetchLetterRequests();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Human Capital')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Karyawan', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          FutureBuilder<List<Employee>>(
            future: _employees,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return _ErrorState(message: snapshot.error.toString());
              }
              final employees = snapshot.data!;
              if (employees.isEmpty) {
                return const Text('Tidak ada data karyawan.');
              }
              return Column(
                children: employees
                    .map(
                      (employee) => Card(
                        child: ListTile(
                          title: Text(employee.fullName),
                          subtitle: Text('${employee.employeeCode} | ${employee.department}'),
                          trailing: Text(employee.position),
                        ),
                      ),
                    )
                    .toList(),
              );
            },
          ),
          const SizedBox(height: 24),
          const Text('Permohonan Surat', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          FutureBuilder<List<LetterRequestItem>>(
            future: _requests,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return _ErrorState(message: snapshot.error.toString());
              }
              final requests = snapshot.data!;
              if (requests.isEmpty) {
                return const Text('Tidak ada permohonan surat.');
              }
              return Column(
                children: requests
                    .map(
                      (request) => Card(
                        child: ListTile(
                          title: Text(request.requestNo),
                          subtitle: Text('${request.employeeName} | ${request.purpose}'),
                          trailing: Text(request.status),
                        ),
                      ),
                    )
                    .toList(),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(
        message,
        style: TextStyle(color: Theme.of(context).colorScheme.error),
      ),
    );
  }
}
