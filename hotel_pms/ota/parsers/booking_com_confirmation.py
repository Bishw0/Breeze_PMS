import re

from ota.base import BaseOtaParser
from ota.errors import ParserExtractionError
from ota.schemas import OtaEmailIngestRequest, ParsedOtaEmail


class BookingComConfirmationParser(BaseOtaParser):
    source_channel = "booking.com"
    email_type = "confirmation"

    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        content = email.raw_content
        booking_id = self.search(
            content,
            r"Booking\s*(?:number|No)\s*:\s*([A-Z0-9-]+)",
            re.IGNORECASE | re.MULTILINE,
        )
        guest_name = self.search(
            content,
            r"(?:Guest information|Guest name)\s*:\s*([^\n]+)",
            re.IGNORECASE | re.MULTILINE,
        )
        check_in_date = self.parse_date(
            self.search(
                content,
                r"Check-in\s*:\s*([A-Za-z]{3},\s*[A-Za-z]{3}\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
                re.IGNORECASE | re.MULTILINE,
            ),
            ["%a, %b %d, %Y", "%d %B %Y"],
        )
        check_out_date = self.parse_date(
            self.search(
                content,
                r"Check-out\s*:\s*([A-Za-z]{3},\s*[A-Za-z]{3}\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
                re.IGNORECASE | re.MULTILINE,
            ),
            ["%a, %b %d, %Y", "%d %B %Y"],
        )
        room_type = self.search(
            content,
            r"(?:Total units/rooms:\s*\n\s*\d+\s*\n\s*)([A-Z][^\n]+(?:Room|Suite|Studio|Apartment)[^\n]*)",
            re.IGNORECASE | re.MULTILINE,
            )
        if not room_type:
            room_type = self.search(
            content,
            r"((?:Deluxe|Standard|Superior|Classic|Family|Twin|Double|Single|Triple)[^\n]+)",
            re.IGNORECASE | re.MULTILINE,
            )
        adults = self.parse_int(self.search(content, r"(\d+)\s+adults?\b", re.IGNORECASE))
        special_requests = self.search(
            content,
            r"Special requests\s*:\s*(.+?)(?:\n[A-Z][^\n]*:|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        currency, total_amount = self._extract_amount(
            content,
            r"Total price\s*:\s*(US\$|USD|[A-Z]{3})\s*([\d.,]+)",
        )

        parsed = ParsedOtaEmail(
            source_channel="booking.com",
            email_type="confirmation",
            external_booking_id=booking_id,
            guest_name=guest_name,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type,
            number_of_rooms=1,
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

    def _extract_amount(self, content: str, pattern: str):
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return None, None

        currency = self.clean(match.group(1))
        amount = self.parse_amount(match.group(2))
        return currency, amount
