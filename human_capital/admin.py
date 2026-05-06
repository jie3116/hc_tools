from django.contrib import admin

from human_capital.models import Employee, LetterRequest, LetterTemplate, PolicyDocument


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_code", "full_name", "linked_user", "department", "position", "employment_status")
    search_fields = ("employee_code", "full_name", "email", "user__username", "user__email")
    list_filter = ("department", "employment_status")
    autocomplete_fields = ("user",)

    def linked_user(self, obj):
        return obj.user.username if obj.user else "-"

    linked_user.short_description = "User"


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "created_at")
    search_fields = ("title", "source_name")
    list_filter = ("language",)


@admin.register(LetterTemplate)
class LetterTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "language", "created_at")
    list_filter = ("language",)
    search_fields = ("name",)


@admin.register(LetterRequest)
class LetterRequestAdmin(admin.ModelAdmin):
    list_display = ("request_no", "employee", "language", "status", "created_at")
    search_fields = ("request_no", "employee__full_name", "employee__employee_code")
    list_filter = ("status", "language")
    autocomplete_fields = ("employee", "template")
