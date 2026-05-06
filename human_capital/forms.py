from django import forms

from human_capital.access import ROLE_EMPLOYEE, user_has_role
from human_capital.models import Employee, LetterRequest, LetterTemplate, PolicyDocument


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "user",
            "employee_code",
            "full_name",
            "email",
            "department",
            "position",
            "employment_status",
            "join_date",
            "manager_name",
        ]
        widgets = {
            "join_date": forms.DateInput(attrs={"type": "date"}),
        }


class PolicyDocumentForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title", "language", "source_name", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }


class LetterTemplateForm(forms.ModelForm):
    class Meta:
        model = LetterTemplate
        fields = ["name", "language", "file"]


class LetterRequestForm(forms.ModelForm):
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        if current_user and user_has_role(current_user, ROLE_EMPLOYEE):
            employee = getattr(current_user, "employee_profile", None)
            if employee:
                self.fields["employee"].queryset = Employee.objects.filter(pk=employee.pk)
                self.fields["employee"].initial = employee
                self.fields["employee"].required = False
                self.fields["employee"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get("employee")
        template = cleaned_data.get("template")
        language = cleaned_data.get("language")

        if self.current_user and user_has_role(self.current_user, ROLE_EMPLOYEE):
            profile = getattr(self.current_user, "employee_profile", None)
            if profile is None:
                raise forms.ValidationError("Akun employee belum terhubung ke data karyawan.")
            if employee and employee != profile:
                raise forms.ValidationError("Employee hanya boleh membuat permohonan untuk profilnya sendiri.")
            cleaned_data["employee"] = profile
            employee = profile

        if template and language and template.language != language:
            raise forms.ValidationError("Bahasa template harus sama dengan bahasa permohonan.")
        return cleaned_data

    class Meta:
        model = LetterRequest
        fields = ["employee", "template", "purpose", "recipient_name", "language", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class CsvImportForm(forms.Form):
    file = forms.FileField()
