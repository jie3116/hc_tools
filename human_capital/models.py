from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="employee_profile")
    employee_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=50)
    join_date = models.DateField()
    manager_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.full_name}"


class PolicyDocument(models.Model):
    LANGUAGE_CHOICES = [("ID", "Indonesia"), ("EN", "English")]

    title = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    source_name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class LetterTemplate(models.Model):
    LANGUAGE_CHOICES = [("ID", "Indonesia"), ("EN", "English")]

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    file = models.FileField(upload_to="templates/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.language})"


class LetterRequest(models.Model):
    STATUS_SUBMITTED = "submitted"
    STATUS_PENDING_APPROVAL = "pending_approval"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_PENDING_APPROVAL, "Pending Approval"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]
    LANGUAGE_CHOICES = [("ID", "Indonesia"), ("EN", "English")]

    request_no = models.CharField(max_length=50, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="letter_requests")
    template = models.ForeignKey(LetterTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.CharField(max_length=255)
    recipient_name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    admin_notes = models.TextField(blank=True)
    approver_notes = models.TextField(blank=True)
    generated_file = models.FileField(upload_to="generated/", null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    admin_reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.request_no
