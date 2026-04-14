from ota.errors import UnsupportedEmailTypeError
from ota.schemas import OtaEmailIngestRequest, SupportedEmailType


CONFIRMATION_KEYWORDS = [
    "booking confirmation",
    "reservation confirmation",
    "confirmed booking",
    "confirmed reservation",
    "reservation confirmed",
    "booking confirmed",
    "new booking",
    "new booking received",
    "booking status confirmed",
    "accepted",
]


def detect_email_type(email: OtaEmailIngestRequest) -> SupportedEmailType:
    searchable_text = " ".join(
        filter(
            None,
            [
                email.subject,
                email.raw_content,
            ],
        )
    ).lower()

    if any(keyword in searchable_text for keyword in CONFIRMATION_KEYWORDS):
        return "confirmation"

    raise UnsupportedEmailTypeError("Only OTA confirmation emails are supported in this MVP.")
