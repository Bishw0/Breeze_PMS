class OtaParsingError(Exception):
    """Base OTA parsing error."""


class UnsupportedSourceError(OtaParsingError):
    """Raised when the OTA source cannot be detected."""


class UnsupportedEmailTypeError(OtaParsingError):
    """Raised when the email type cannot be mapped to a supported parser."""


class MissingParserError(OtaParsingError):
    """Raised when no parser exists for the detected source and email type."""


class ParserExtractionError(OtaParsingError):
    """Raised when a parser cannot extract the minimum required fields."""
