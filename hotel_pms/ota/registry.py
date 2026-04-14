from ota.base import BaseOtaParser
from ota.errors import MissingParserError
from ota.parsers.agoda_confirmation import AgodaConfirmationParser
from ota.parsers.makemytrip_confirmation import MakeMyTripConfirmationParser
from ota.parsers.trip_com_confirmation import TripComConfirmationParser
from ota.schemas import SupportedEmailType, SupportedOtaSource


class OtaParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[tuple[SupportedOtaSource, SupportedEmailType], BaseOtaParser] = {}

    def register(self, parser: BaseOtaParser) -> None:
        key = (parser.source_channel, parser.email_type)
        self._parsers[key] = parser

    def get(self, source_channel: SupportedOtaSource, email_type: SupportedEmailType) -> BaseOtaParser:
        parser = self._parsers.get((source_channel, email_type))
        if parser is None:
            raise MissingParserError(
                f"No OTA parser registered for source '{source_channel}' and type '{email_type}'."
            )
        return parser


registry = OtaParserRegistry()
registry.register(AgodaConfirmationParser())
registry.register(TripComConfirmationParser())
registry.register(MakeMyTripConfirmationParser())
