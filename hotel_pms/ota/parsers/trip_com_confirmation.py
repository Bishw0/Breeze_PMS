import re

from ota.base import BaseOtaParser
from ota.schemas import OtaEmailIngestRequest, ParsedOtaEmail


class TripComConfirmationParser(BaseOtaParser):
    source_channel = "trip.com"
    email_type = "confirmation"

    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        content = email.raw_content
        booking_id = self.search(content, r"Reservation no\.?\s*#?(\d{6,})", re.I)
        guest_name = self._extract_guest_name(content)
        staying_match = re.search(
            r"Staying period:([A-Za-z]{3}\s+\d{1,2},\s+\d{4})\s*-\s*([A-Za-z]{3}\s+\d{1,2},\s+\d{4})",
            content,
            re.IGNORECASE,
        )
        check_in_date = (
            self.parse_date(staying_match.group(1), ["%b %d, %Y"]) if staying_match else None
        )
        check_out_date = (
            self.parse_date(staying_match.group(2), ["%b %d, %Y"]) if staying_match else None
        )
        room_type = self.search(
            content,
            r"Room Type:(.+?)(?:B2C：|\|)",
            re.IGNORECASE | re.MULTILINE,
        )
        number_of_rooms = self.parse_int(
            self.search(content, r"Room Type:.*?\|\s*(\d+)\s*room\(s\)", re.I | re.S)
        )
        adults = self.parse_int(
            self.search(content, r"Guests \(estimated\):\s*(\d+)\s*adults", re.IGNORECASE)
        )
        currency, total_amount = self._extract_amount(
            content,
            r"Your payout\s*([A-Z]{3})\s*([\d.,]+)",
        )
        special_requests = self._extract_special_requests(content)

        parsed = ParsedOtaEmail(
            source_channel="trip.com",
            email_type="confirmation",
            external_booking_id=booking_id,
            guest_name=guest_name,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type,
            number_of_rooms=number_of_rooms,
            adults=adults,
            children=0,
            total_amount=total_amount,
            currency=currency,
            special_requests=special_requests,
            raw_email_subject=email.subject,
            raw_email_sender=email.sender_email,
        )

        self.require(parsed.external_booking_id, "external_booking_id")
        self.require(parsed.guest_name, "guest_name")
        self.require(parsed.check_in_date, "check_in_date")
        self.require(parsed.check_out_date, "check_out_date")
        self.require(parsed.room_type, "room_type")

        return parsed

    def _extract_guest_name(self, content: str) -> str | None:
        raw_guest = self.search(content, r"Guest Name:\s*([^\n]+)", re.IGNORECASE)
        if not raw_guest:
            return None

        cleaned = re.sub(r"\([^)]*\)", "", raw_guest).replace("/", " ")
        return self.clean(cleaned)

    def _extract_special_requests(self, content: str) -> str | None:
        section_match = re.search(
            r"Special requests\s+Bed type preference:\s*(.+?)\s+Other requests:\s*(.+?)\s+Cancellation Policy",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if not section_match:
            return None

        bed_pref = self.clean(section_match.group(1))
        other_requests = self.clean(section_match.group(2))
        parts = [part for part in [bed_pref, other_requests] if part]
        return "; ".join(parts) if parts else None

    def _extract_amount(self, content: str, pattern: str):
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return None, None

        currency = self.clean(match.group(1))
        amount = self.parse_amount(match.group(2))
        return currency, amount
