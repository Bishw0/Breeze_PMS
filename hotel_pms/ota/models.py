from django.db import models


class OtaEmail(models.Model):
    PROCESSING_STATUS_PENDING = "pending"
    PROCESSING_STATUS_PARSED = "parsed"
    PROCESSING_STATUS_FAILED = "failed"

    PROCESSING_STATUS_CHOICES = [
        (PROCESSING_STATUS_PENDING, "Pending"),
        (PROCESSING_STATUS_PARSED, "Parsed"),
        (PROCESSING_STATUS_FAILED, "Failed"),
    ]

    source_channel = models.CharField(max_length=80)
    subject = models.CharField(max_length=255, null=True, blank=True)
    sender_email = models.CharField(max_length=255, null=True, blank=True)
    raw_content = models.TextField()
    parsed_payload = models.JSONField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default=PROCESSING_STATUS_PENDING,
    )
    failure_reason = models.TextField(null=True, blank=True)
    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ota_emails",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        subject = self.subject or "Untitled OTA email"
        return f"{self.source_channel} - {subject}"
