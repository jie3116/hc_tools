from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from secrets import token_hex

from django.core.files.base import ContentFile
from django.utils import timezone
from docx import Document

from human_capital.models import Employee, LetterRequest, LetterTemplate, PolicyDocument
from human_capital.rag import cosine_similarity, normalize_text, split_into_chunks


class WorkflowError(ValueError):
    pass


def ask_policy(question: str) -> dict:
    query_tokens = normalize_text(question)
    scored_chunks: list[dict] = []
    for policy in PolicyDocument.objects.all():
        for chunk in split_into_chunks(policy.content):
            score = cosine_similarity(query_tokens, normalize_text(chunk))
            if score > 0:
                scored_chunks.append(
                    {
                        "title": policy.title,
                        "language": policy.language,
                        "source_name": policy.source_name,
                        "content": chunk,
                        "score": score,
                    }
                )
    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    references = scored_chunks[:3]
    if not references:
        return {
            "answer": "Belum ada dokumen kebijakan yang cukup relevan. Tambahkan atau perbarui basis kebijakan HC.",
            "references": [],
        }
    lines = ["Jawaban dirangkum dari dokumen kebijakan terdekat:"]
    for item in references:
        excerpt = item["content"][:280]
        if len(item["content"]) > 280:
            excerpt += "..."
        lines.append(f"- {item['title']} ({item['language']}): {excerpt}")
    return {"answer": "\n".join(lines), "references": references}


def import_employees_from_csv(uploaded_file) -> int:
    decoded = uploaded_file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    count = 0
    for row in reader:
        Employee.objects.update_or_create(
            employee_code=row["employee_code"].strip(),
            defaults={
                "full_name": row["full_name"].strip(),
                "email": row["email"].strip(),
                "department": row["department"].strip(),
                "position": row["position"].strip(),
                "employment_status": row["employment_status"].strip(),
                "join_date": row["join_date"].strip(),
                "manager_name": row.get("manager_name", "").strip(),
            },
        )
        count += 1
    return count


def generate_request_no() -> str:
    return f"SK-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{token_hex(2).upper()}"


def create_letter_request_from_form(form) -> LetterRequest:
    request = form.save(commit=False)
    request.request_no = generate_request_no()
    request.status = LetterRequest.STATUS_SUBMITTED
    request.submitted_at = timezone.now()
    request.save()
    return request


def admin_review_letter_request(letter_request: LetterRequest, approved: bool, notes: str) -> LetterRequest:
    if letter_request.status != LetterRequest.STATUS_SUBMITTED:
        raise WorkflowError("Only submitted requests can be reviewed by admin.")
    letter_request.admin_notes = notes
    letter_request.admin_reviewed_at = timezone.now()
    letter_request.status = (
        LetterRequest.STATUS_PENDING_APPROVAL if approved else LetterRequest.STATUS_REJECTED
    )
    letter_request.save(update_fields=["admin_notes", "admin_reviewed_at", "status", "updated_at"])
    return letter_request


def approver_review_letter_request(letter_request: LetterRequest, approved: bool, notes: str) -> LetterRequest:
    if letter_request.status != LetterRequest.STATUS_PENDING_APPROVAL:
        raise WorkflowError("Only requests pending approval can be reviewed by approver.")
    letter_request.approver_notes = notes
    if approved:
        letter_request.status = LetterRequest.STATUS_APPROVED
        letter_request.approved_at = timezone.now()
        generate_letter_document(letter_request)
    else:
        letter_request.status = LetterRequest.STATUS_REJECTED
    letter_request.save()
    return letter_request


def generate_letter_document(letter_request: LetterRequest) -> None:
    if not letter_request.template:
        raise ValueError("Template surat belum dipilih.")
    document = Document(letter_request.template.file.path)
    replacements = {
        "{{request_no}}": letter_request.request_no,
        "{{full_name}}": letter_request.employee.full_name,
        "{{employee_code}}": letter_request.employee.employee_code,
        "{{department}}": letter_request.employee.department,
        "{{position}}": letter_request.employee.position,
        "{{join_date}}": letter_request.employee.join_date.strftime("%Y-%m-%d"),
        "{{employment_status}}": letter_request.employee.employment_status,
        "{{purpose}}": letter_request.purpose,
        "{{recipient_name}}": letter_request.recipient_name,
        "{{today}}": timezone.localtime().strftime("%d %B %Y"),
    }
    for paragraph in document.paragraphs:
        text = paragraph.text
        for key, value in replacements.items():
            text = text.replace(key, value)
        if paragraph.runs:
            paragraph.runs[0].text = text
            for run in paragraph.runs[1:]:
                run.text = ""
    output_path = f"{letter_request.request_no}_{letter_request.employee.employee_code}.docx"
    temp_file = Path(letter_request.template.file.path).parent / output_path
    document.save(temp_file)
    with temp_file.open("rb") as stream:
        letter_request.generated_file.save(output_path, ContentFile(stream.read()), save=False)
    temp_file.unlink(missing_ok=True)
