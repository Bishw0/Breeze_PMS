from ota.errors import UnsupportedSourceError
from ota.schemas import OtaEmailIngestRequest, SupportedOtaSource


def detect_source(email: OtaEmailIngestRequest) -> SupportedOtaSource:
    searchable_text = " ".join(
        filter(
            None,
            [
                email.sender_email,
                email.subject,
                email.raw_content,
            ],
        )
    ).lower()

    if "agoda" in searchable_text:
        return "agoda"
    if "makemytrip" in searchable_text or "make my trip" in searchable_text or "go-mmt.com" in searchable_text:
        return "makemytrip"
    if "trip.com" in searchable_text or "tripcom" in searchable_text:
        return "trip.com"

    raise UnsupportedSourceError("OTA source could not be detected from the email content.")
