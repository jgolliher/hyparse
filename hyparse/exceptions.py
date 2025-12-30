"""Custom exceptions for hyparse package."""


class Hy3ParseError(Exception):
    """Base exception for .hy3 parsing errors."""

    pass


class ChecksumError(Hy3ParseError):
    """Raised when checksum validation fails."""

    def __init__(self, line_num: int, expected: str, actual: str, line: str = ""):
        self.line_num = line_num
        self.expected = expected
        self.actual = actual
        self.line = line
        super().__init__(f"Line {line_num}: Checksum mismatch. Expected {expected}, got {actual}")


class InvalidLineError(Hy3ParseError):
    """Raised when a line cannot be parsed."""

    def __init__(self, line_num: int, line_id: str, message: str):
        self.line_num = line_num
        self.line_id = line_id
        super().__init__(f"Line {line_num} ({line_id}): {message}")


class MissingDataError(Hy3ParseError):
    """Raised when required data is missing."""

    def __init__(self, field_name: str, line_num: int = None):
        self.field_name = field_name
        self.line_num = line_num
        msg = f"Missing required field: {field_name}"
        if line_num:
            msg = f"Line {line_num}: {msg}"
        super().__init__(msg)


class StructuralError(Hy3ParseError):
    """Raised when file structure is invalid (e.g., E2 without E1)."""

    def __init__(self, message: str, line_num: int = None):
        self.line_num = line_num
        if line_num:
            message = f"Line {line_num}: {message}"
        super().__init__(message)


class FileFormatError(Hy3ParseError):
    """Raised when file format is invalid or corrupted."""

    pass
