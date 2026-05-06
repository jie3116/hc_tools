import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/employee.dart';
import '../models/letter_request.dart';

class ApiException implements Exception {
  ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiService {
  ApiService({
    this.baseUrl = 'http://10.0.2.2:8000/api',
    this.username,
    this.password,
  });

  final String baseUrl;
  final String? username;
  final String? password;

  Map<String, String> get _headers {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (username != null && password != null) {
      final credentials = base64Encode(utf8.encode('$username:$password'));
      headers['Authorization'] = 'Basic $credentials';
    }
    return headers;
  }

  Future<List<dynamic>> _getList(String path) async {
    final response = await http.get(Uri.parse('$baseUrl/$path'), headers: _headers);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException('Request to $path failed with status ${response.statusCode}.');
    }
    final payload = jsonDecode(response.body);
    if (payload is! List<dynamic>) {
      throw ApiException('Unexpected response format for $path.');
    }
    return payload;
  }

  Future<List<Employee>> fetchEmployees() async {
    final payload = await _getList('employees/');
    return payload.map((item) => Employee.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<List<LetterRequestItem>> fetchLetterRequests() async {
    final payload = await _getList('requests/');
    return payload
        .map((item) => LetterRequestItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
