from rest_framework import serializers

from human_capital.models import Employee, LetterRequest, LetterTemplate, PolicyDocument


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class PolicyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocument
        fields = "__all__"


class LetterTemplateSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = LetterTemplate
        fields = ["id", "name", "language", "file", "file_url", "created_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class LetterRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    generated_file_url = serializers.SerializerMethodField()

    class Meta:
        model = LetterRequest
        fields = "__all__"
        extra_kwargs = {
            "employee": {"required": False},
        }
        read_only_fields = [
            "request_no",
            "status",
            "generated_file",
            "submitted_at",
            "admin_reviewed_at",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def get_generated_file_url(self, obj):
        request = self.context.get("request")
        if obj.generated_file and request:
            return request.build_absolute_uri(obj.generated_file.url)
        return obj.generated_file.url if obj.generated_file else None
