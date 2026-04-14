from pathlib import Path
import re

from ota.schemas import OtaEmailIngestRequest, SupportedEmailType, SupportedOtaSource

FIXTURE_ROOT = Path(__file__).resolve().parent
SOURCE_DIR_NAMES: dict[SupportedOtaSource, str] = {
    "agoda": "agoda",
    "trip.com": "trip_com",
    "makemytrip": "makemytrip",
}


def load_fixture_email(
    source_channel: SupportedOtaSource,
    email_type: SupportedEmailType = "confirmation",
) -> OtaEmailIngestRequest:
    fixture_path = FIXTURE_ROOT / SOURCE_DIR_NAMES[source_channel] / f"{email_type}.txt"
    raw_content = fixture_path.read_text(encoding="utf-8")

    return OtaEmailIngestRequest(
        sender_email=_extract_sender(raw_content),
        subject=_extract_header(raw_content, "Subject"),
        raw_content=raw_content,
    )


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
