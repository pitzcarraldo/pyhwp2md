"""Custom exceptions for pyhwp2md."""


class Pyhwp2mdError(Exception):
    """Base exception for pyhwp2md."""

    pass


class FileTypeError(Pyhwp2mdError):
    """Cannot determine or unsupported file type."""

    pass


class ConversionError(Pyhwp2mdError):
    """Error during conversion process."""

    pass


class ParsingError(ConversionError):
    """Error parsing input file."""

    pass
