class LetterRequestItem {
  final int id;
  final String requestNo;
  final String employeeName;
  final String purpose;
  final String status;
  final String? generatedFileUrl;

  LetterRequestItem({
    required this.id,
    required this.requestNo,
    required this.employeeName,
    required this.purpose,
    required this.status,
    this.generatedFileUrl,
  });

  factory LetterRequestItem.fromJson(Map<String, dynamic> json) {
    return LetterRequestItem(
      id: json['id'] as int,
      requestNo: json['request_no'] as String,
      employeeName: json['employee_name'] as String? ?? '',
      purpose: json['purpose'] as String,
      status: json['status'] as String,
      generatedFileUrl: json['generated_file_url'] as String?,
    );
  }
}
