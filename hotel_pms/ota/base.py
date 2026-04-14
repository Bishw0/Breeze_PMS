from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

from ota.errors import ParserExtractionError

from ota.schemas import OtaEmailIngestRequest, ParsedOtaEmail


class BaseOtaParser(ABC):
    source_channel: str
    email_type: str

    @abstractmethod
    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        raise NotImplementedError

    def search(self, content: str, pattern: str, flags: int = re.IGNORECASE) -> str | None:
        match = re.search(pattern, content, flags)
        if not match:
            return None
        return self.clean(match.group(1))

    def clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        return " ".join(value.replace("\xa0", " ").split()).strip()

    def parse_int(self, value: str | None) -> int | None:
        cleaned = self.clean(value)
        if not cleaned:
            return None
        try:
            return int(cleaned)
        except ValueError as exc:
            raise ParserExtractionError(f"Invalid integer value: {cleaned}") from exc

    def parse_date(self, value: str | None, formats: list[str]) -> date | None:
        cleaned = self.clean(value)
        if not cleaned:
            return None

        for pattern in formats:
            try:
                return datetime.strptime(cleaned, pattern).date()
            except ValueError:
                continue

        raise ParserExtractionError(f"Invalid date value: {cleaned}")

    def parse_amount(self, value: str | None) -> Decimal | None:
        cleaned = self.clean(value)
        if not cleaned:
            return None

        normalized = re.sub(r"[^0-9.-]", "", cleaned)
        if not normalized:
            return None

        try:
            return Decimal(normalized)
        except InvalidOperation as exc:
            raise ParserExtractionError(f"Invalid decimal value: {cleaned}") from exc

    def require(self, value: object | None, field_name: str) -> None:
        if value in (None, ""):
            raise ParserExtractionError(
                f"{self.source_channel} {self.email_type} parser could not extract '{field_name}'."
            )
