class Employee {
  final int id;
  final String employeeCode;
  final String fullName;
  final String department;
  final String position;

  Employee({
    required this.id,
    required this.employeeCode,
    required this.fullName,
    required this.department,
    required this.position,
  });

  factory Employee.fromJson(Map<String, dynamic> json) {
    return Employee(
      id: json['id'] as int,
      employeeCode: json['employee_code'] as String,
      fullName: json['full_name'] as String,
      department: json['department'] as String,
      position: json['position'] as String,
    );
  }
}
