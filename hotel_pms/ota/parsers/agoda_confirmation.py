import re

from ota.base import BaseOtaParser
from ota.errors import ParserExtractionError
from ota.schemas import OtaEmailIngestRequest, ParsedOtaEmail


class AgodaConfirmationParser(BaseOtaParser):
    source_channel = "agoda"
    email_type = "confirmation"

    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        content = email.raw_content
        booking_id = self.search(content, r"Booking ID\s+(\d{6,})", re.IGNORECASE | re.MULTILINE)
        first_name = self.search(
            content,
            r"Customer First Name\s+([A-Za-z][^\n]+)",
            re.IGNORECASE | re.MULTILINE,
        )
        last_name = self.search(
            content,
            r"Customer Last Name\s+([A-Za-z][^\n]+)",
            re.IGNORECASE | re.MULTILINE,
        )
        guest_name = self.clean(" ".join(part for part in [first_name, last_name] if part))
        check_in_date = self.parse_date(
            self.search(content, r"Check-in\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.I | re.M),
            ["%B %d, %Y"],
        )
        check_out_date = self.parse_date(
            self.search(content, r"Check-out\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.I | re.M),
            ["%B %d, %Y"],
        )
        room_type = self.search(
            content,
            r"Room Type\s+No\. of Rooms\s+Occupancy\s+No\. of Extra Bed\s+(.+?)\s+\d+\s+\d+\s+Adults",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        number_of_rooms = self.parse_int(
            self.search(
                content,
                r"Room Type\s+No\. of Rooms\s+Occupancy\s+No\. of Extra Bed\s+.+?\s+(\d+)\s+\d+\s+Adults",
                re.IGNORECASE | re.MULTILINE | re.DOTALL,
            )
        )
        adults = self.parse_int(
            self.search(
                content,
                r"Room Type\s+No\. of Rooms\s+Occupancy\s+No\. of Extra Bed\s+.+?\s+\d+\s+(\d+)\s+Adults",
                re.IGNORECASE | re.MULTILINE | re.DOTALL,
            )
        )
        special_requests = self.search(
            content,
            r"Special Requests.*?\)\s+(.+?)\s+Cancellation Policy",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        currency, total_amount = self._extract_amount(
            content,
            r"Net rate \(incl\. taxes & fees\)\s+([A-Z]{3})\s*([\d.,]+)",
        )

        parsed = ParsedOtaEmail(
            source_channel="agoda",
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

    def _extract_amount(self, content: str, pattern: str):
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return None, None

        currency = self.clean(match.group(1))
        amount = self.parse_amount(match.group(2))
        return currency, amount
