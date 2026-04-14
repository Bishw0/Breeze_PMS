from ota.base import BaseOtaParser
from ota.detectors.email_type import detect_email_type
from ota.detectors.source import detect_source
from ota.registry import registry
from ota.schemas import (
    OtaEmailIngestRequest,
    ParsedOtaEmail,
    SupportedEmailType,
    SupportedOtaSource,
)


class OtaParsingService:
    def resolve_parser(
        self,
        email: OtaEmailIngestRequest,
    ) -> tuple[SupportedOtaSource, SupportedEmailType, BaseOtaParser]:
        source_channel = detect_source(email)
        email_type = detect_email_type(email)
        parser = registry.get(source_channel, email_type)
        return source_channel, email_type, parser

    def parse(self, email: OtaEmailIngestRequest) -> ParsedOtaEmail:
        _, _, parser = self.resolve_parser(email)
        return parser.parse(email)


ota_parsing_service = OtaParsingService()
