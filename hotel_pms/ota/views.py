import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ota.models import OtaEmail
from ota.schemas import OtaEmailIngestRequest
from ota.service import ota_parsing_service


def _extract_header(raw_content: str, header_name: str) -> str | None:
    match = re.search(rf"^{header_name}:\s*(.+)$", raw_content, flags=re.MULTILINE)
    return " ".join(match.group(1).split()) if match else None


def _extract_sender(raw_content: str) -> str | None:
    sender_line = _extract_header(raw_content, "From")
    if not sender_line:
        return None

    mailto_match = re.search(r"mailto:([^\]\s>]+)", sender_line, flags=re.IGNORECASE)
    if mailto_match:
        return mailto_match.group(1)

    angle_match = re.search(r"<([^>\s]+)>", sender_line)
    if angle_match:
        return angle_match.group(1)

    email_match = re.search(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", sender_line, flags=re.I)
    if email_match:
        return email_match.group(1)

    return sender_line


@login_required
def inbox_view(request):
    ota_emails = OtaEmail.objects.select_related("reservation").order_by("-created_at")
    return render(request, "ota/inbox.html", {"ota_emails": ota_emails})


@login_required
def ingest_view(request):
    if request.method != "POST":
        return redirect("ota_inbox")

    raw_content = (request.POST.get("raw_content") or "").strip()
    if not raw_content:
        messages.error(request, "Please paste a raw OTA email before parsing.")
        return redirect("ota_inbox")

    subject = _extract_header(raw_content, "Subject")
    sender_email = _extract_sender(raw_content)
    ingest_request = OtaEmailIngestRequest(
        sender_email=sender_email,
        subject=subject,
        raw_content=raw_content,
    )

    ota_email = OtaEmail.objects.create(
        source_channel="unknown",
        subject=subject,
        sender_email=sender_email,
        raw_content=raw_content,
        processing_status=OtaEmail.PROCESSING_STATUS_PENDING,
    )

    try:
        parsed_email = ota_parsing_service.parse(ingest_request)
        ota_email.source_channel = parsed_email.source_channel
        ota_email.parsed_payload = parsed_email.model_dump(mode="json")
        ota_email.processing_status = OtaEmail.PROCESSING_STATUS_PARSED
        ota_email.failure_reason = None
        ota_email.save(
            update_fields=[
                "source_channel",
                "parsed_payload",
                "processing_status",
                "failure_reason",
                "updated_at",
            ]
        )
        messages.success(request, "OTA email parsed successfully.")
    except Exception as exc:
        ota_email.processing_status = OtaEmail.PROCESSING_STATUS_FAILED
        ota_email.failure_reason = str(exc)
        ota_email.save(update_fields=["processing_status", "failure_reason", "updated_at"])
        messages.error(request, f"OTA email parsing failed: {exc}")

    return redirect("ota_inbox")
