"""Exceptions raised by hyparse readers."""


class HyparseError(Exception):
    """Base class for all hyparse errors."""


class FileFormatError(HyparseError):
    """The file is not the format it claims to be, or a line has an unexpected shape."""

    def __init__(self, message: str, line_number: int | None = None):
        self.line_number = line_number
        prefix = f"Line {line_number}: " if line_number is not None else ""
        super().__init__(prefix + message)


class ChecksumError(FileFormatError):
    """A .hy3 line's checksum doesn't match its content (strict mode only)."""
