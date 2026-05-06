from __future__ import annotations

from django.contrib import messages
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework import exceptions
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from human_capital.access import ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE, get_user_roles, require_roles, user_has_role
from human_capital.forms import CsvImportForm, EmployeeForm, LetterRequestForm, LetterTemplateForm, PolicyDocumentForm
from human_capital.models import Employee, LetterRequest, LetterTemplate, PolicyDocument
from human_capital.permissions import (
    EmployeeApiPermission,
    LetterRequestApiPermission,
    LetterTemplateApiPermission,
    PolicyChatApiPermission,
    PolicyDocumentApiPermission,
)
from human_capital.serializers import (
    EmployeeSerializer,
    LetterRequestSerializer,
    LetterTemplateSerializer,
    PolicyDocumentSerializer,
)
from human_capital.services import (
    WorkflowError,
    admin_review_letter_request,
    approver_review_letter_request,
    ask_policy,
    create_letter_request_from_form,
    generate_request_no,
    import_employees_from_csv,
)
from django.utils import timezone


def _get_visible_requests(user):
    queryset = LetterRequest.objects.select_related("employee", "template")
    if user_has_role(user, ROLE_EMPLOYEE):
        return queryset.filter(employee__user=user)
    return queryset


@require_roles(ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
def dashboard(request: HttpRequest) -> HttpResponse:
    visible_requests = _get_visible_requests(request.user)
    status_counts = {
        item["status"]: item["total"]
        for item in visible_requests.values("status").annotate(total=Count("id"))
    }
    employee_count = Employee.objects.count()
    request_count = visible_requests.count()
    if user_has_role(request.user, ROLE_EMPLOYEE):
        employee_count = 1 if getattr(request.user, "employee_profile", None) else 0
    context = {
        "employee_count": employee_count,
        "policy_count": PolicyDocument.objects.count(),
        "template_count": LetterTemplate.objects.count(),
        "request_count": request_count,
        "status_counts": status_counts,
        "recent_requests": visible_requests[:8],
        "user_roles": get_user_roles(request.user),
    }
    return render(request, "human_capital/dashboard.html", context)


@require_roles(ROLE_ADMIN_HC)
def employee_list(request: HttpRequest) -> HttpResponse:
    context = {
        "employees": Employee.objects.all(),
        "csv_form": CsvImportForm(),
    }
    return render(request, "human_capital/employee_list.html", context)


@require_roles(ROLE_ADMIN_HC)
def employee_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data karyawan berhasil ditambahkan.")
            return redirect("employee_list")
    else:
        form = EmployeeForm()
    return render(request, "human_capital/employee_form.html", {"form": form, "title": "Tambah Karyawan"})


@require_roles(ROLE_ADMIN_HC)
def employee_update(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Data karyawan berhasil diperbarui.")
            return redirect("employee_list")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "human_capital/employee_form.html", {"form": form, "title": "Edit Karyawan"})


@require_roles(ROLE_ADMIN_HC)
@require_http_methods(["POST"])
def employee_delete(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request, "Data karyawan berhasil dihapus.")
    return redirect("employee_list")


@require_roles(ROLE_ADMIN_HC)
@require_http_methods(["POST"])
def employee_import(request: HttpRequest) -> HttpResponse:
    form = CsvImportForm(request.POST, request.FILES)
    if form.is_valid():
        processed = import_employees_from_csv(form.cleaned_data["file"])
        messages.success(request, f"{processed} baris karyawan diproses.")
    else:
        messages.error(request, "Upload CSV tidak valid.")
    return redirect("employee_list")


@require_roles(ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
def policy_chat(request: HttpRequest) -> HttpResponse:
    answer = None
    references = []
    question = ""
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if question:
            result = ask_policy(question)
            answer = result["answer"]
            references = result["references"]
        else:
            messages.error(request, "Pertanyaan wajib diisi.")
    return render(
        request,
        "human_capital/policy_chat.html",
        {"question": question, "answer": answer, "references": references},
    )


@require_roles(ROLE_ADMIN_HC)
def assets(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        if "save_policy" in request.POST:
            policy_form = PolicyDocumentForm(request.POST)
            template_form = LetterTemplateForm()
            if policy_form.is_valid():
                policy_form.save()
                messages.success(request, "Dokumen kebijakan berhasil ditambahkan.")
                return redirect("assets")
        else:
            template_form = LetterTemplateForm(request.POST, request.FILES)
            policy_form = PolicyDocumentForm()
            if template_form.is_valid():
                template_form.save()
                messages.success(request, "Template surat berhasil ditambahkan.")
                return redirect("assets")
    else:
        policy_form = PolicyDocumentForm()
        template_form = LetterTemplateForm()
    context = {
        "policy_form": policy_form,
        "template_form": template_form,
        "policies": PolicyDocument.objects.all(),
        "templates": LetterTemplate.objects.all(),
    }
    return render(request, "human_capital/assets.html", context)


@require_roles(ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
def letter_request_list(request: HttpRequest) -> HttpResponse:
    requests = _get_visible_requests(request.user).all()
    return render(request, "human_capital/letter_request_list.html", {"requests": requests})


@require_roles(ROLE_ADMIN_HC, ROLE_EMPLOYEE)
def letter_request_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LetterRequestForm(request.POST, current_user=request.user)
        if form.is_valid():
            create_letter_request_from_form(form)
            messages.success(request, "Permohonan surat berhasil dikirim.")
            return redirect("letter_request_list")
    else:
        form = LetterRequestForm(current_user=request.user)
    return render(request, "human_capital/letter_request_form.html", {"form": form})


@require_roles(ROLE_ADMIN_HC)
@require_http_methods(["POST"])
def letter_request_admin_review(request: HttpRequest, pk: int) -> HttpResponse:
    letter_request = get_object_or_404(LetterRequest, pk=pk)
    approved = request.POST.get("decision") == "approve"
    try:
        admin_review_letter_request(letter_request, approved, request.POST.get("admin_notes", ""))
    except WorkflowError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Review admin tersimpan.")
    return redirect("letter_request_list")


@require_roles(ROLE_APPROVER)
@require_http_methods(["POST"])
def letter_request_approver_review(request: HttpRequest, pk: int) -> HttpResponse:
    letter_request = get_object_or_404(LetterRequest, pk=pk)
    approved = request.POST.get("decision") == "approve"
    try:
        approver_review_letter_request(letter_request, approved, request.POST.get("approver_notes", ""))
    except (WorkflowError, ValueError) as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Keputusan approver tersimpan.")
    return redirect("letter_request_list")


class EmployeeListCreateApi(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [EmployeeApiPermission]


class PolicyListCreateApi(generics.ListCreateAPIView):
    queryset = PolicyDocument.objects.all()
    serializer_class = PolicyDocumentSerializer
    permission_classes = [PolicyDocumentApiPermission]


class TemplateListCreateApi(generics.ListCreateAPIView):
    queryset = LetterTemplate.objects.all()
    serializer_class = LetterTemplateSerializer
    permission_classes = [LetterTemplateApiPermission]


class LetterRequestListCreateApi(generics.ListCreateAPIView):
    serializer_class = LetterRequestSerializer
    permission_classes = [LetterRequestApiPermission]

    def get_queryset(self):
        return _get_visible_requests(self.request.user).all()

    def perform_create(self, serializer):
        employee = serializer.validated_data.get("employee")
        if user_has_role(self.request.user, ROLE_EMPLOYEE):
            profile = getattr(self.request.user, "employee_profile", None)
            if profile is None:
                raise exceptions.ValidationError({"employee": "Akun employee belum terhubung ke data karyawan."})
            if employee and employee != profile:
                raise exceptions.PermissionDenied("Employee hanya boleh membuat permohonan untuk profilnya sendiri.")
            employee = profile
        if employee is None:
            raise exceptions.ValidationError({"employee": "Employee is required."})
        instance = serializer.save(
            employee=employee,
            request_no=generate_request_no(),
            status=LetterRequest.STATUS_SUBMITTED,
            submitted_at=timezone.now(),
        )
        instance.save(update_fields=["submitted_at"])


class PolicyChatApi(APIView):
    permission_classes = [PolicyChatApiPermission]

    def post(self, request):
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"detail": "question is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ask_policy(question))
