from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SupportedOtaSource = Literal["agoda", "trip.com", "makemytrip"]
SupportedEmailType = Literal["confirmation"]


class OtaEmailIngestRequest(BaseModel):
    sender_email: str | None = None
    subject: str | None = None
    raw_content: str = Field(min_length=1)
    received_at: datetime | None = None


class ParsedOtaEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_channel: SupportedOtaSource
    email_type: SupportedEmailType
    external_booking_id: str | None = None
    guest_name: str | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    room_type: str | None = None
    number_of_rooms: int | None = None
    adults: int | None = None
    children: int | None = None
    total_amount: Decimal | None = None
    currency: str | None = None
    special_requests: str | None = None
    raw_email_subject: str | None = None
    raw_email_sender: str | None = None


class OtaEmailParseResponse(BaseModel):
    ota_email_id: str
    processing_status: str
    parsed_output: ParsedOtaEmail | None = None
    reservation_id: str | None = None
    reservation_action: str | None = None
    failure_reason: str | None = None


class OtaSampleParseRequest(BaseModel):
    source_channel: SupportedOtaSource
