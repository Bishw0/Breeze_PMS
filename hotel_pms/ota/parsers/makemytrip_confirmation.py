import re

from ota.base import BaseOtaParser
from ota.schemas import OtaEmailIngestRequest, ParsedOtaEmail


class MakeMyTripConfirmationParser(BaseOtaParser):
    source_channel = "makemytrip"
    email_type = "confirmation"

    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        content = email.raw_content
        booking_id = self.search(content, r"BOOKING ID\s+([A-Z0-9]+)", re.IGNORECASE | re.MULTILINE)
        guest_name = self.search(
            content,
            r"PRIMARY GUEST DETAILS\s+([A-Za-z][A-Za-z\s]+?)\s+CHECK-IN",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        check_in_date = self.parse_date(
            self.search(content, r"CHECK-IN\s+CHECK-OUT\s+(\d{2}\s+[A-Za-z]{3}\s+'?\d{2})", re.I | re.S),
            ["%d %b '%y", "%d %b %y"],
        )
        check_out_date = self.parse_date(
            self.search(
                content,
                r"CHECK-IN\s+CHECK-OUT\s+\d{2}\s+[A-Za-z]{3}\s+'?\d{2}.*?(\d{2}\s+[A-Za-z]{3}\s+'?\d{2})",
                re.IGNORECASE | re.DOTALL,
            ),
            ["%d %b '%y", "%d %b %y"],
        )
        room_type = self.search(
            content,
            r"1\s+Room\(s\)\s+1\s+x\s+(.+?)\s+2\s+Adults",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        number_of_rooms = self.parse_int(self.search(content, r"(\d+)\s+Room\(s\)", re.IGNORECASE))
        adults = self.parse_int(
            self.search(content, r"TOTAL NO\. OF GUEST\(S\)\s+(\d+)\s+Adults", re.I | re.S)
        )
        currency, total_amount = self._extract_amount(
            content,
            r"Payable to Property\s+([A-Z]{3})\s*([\d.,]+)",
        )

        parsed = ParsedOtaEmail(
            source_channel="makemytrip",
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
            special_requests=None,
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
