# Expose main classes and version
from .objects import MeetInfo, Athlete, Team, IndividualResult, RelayResult
from .parser import Hy3File
from .parser.validator import ChecksumValidator, validate_file_structure
from .parser.line_specs import LINE_SPECS, STROKE_CODES, COURSE_CODES, ROUND_CODES
from .transformers import (
    DataFrameTransformer,
    IndividualResultTransformer,
    RelayResultTransformer,
)
from .exceptions import (
    Hy3ParseError,
    ChecksumError,
    InvalidLineError,
    MissingDataError,
    StructuralError,
    FileFormatError,
)
from .utils import ss_to_display, rank_times

__version__ = "0.3.0"  # Updated version after refactor

__all__ = [
    # Core parser and data models
    "Hy3File",
    "MeetInfo",
    "Athlete",
    "Team",
    "IndividualResult",
    "RelayResult",
    # Validators
    "ChecksumValidator",
    "validate_file_structure",
    # Transformers
    "DataFrameTransformer",
    "IndividualResultTransformer",
    "RelayResultTransformer",
    # Exceptions
    "Hy3ParseError",
    "ChecksumError",
    "InvalidLineError",
    "MissingDataError",
    "StructuralError",
    "FileFormatError",
    # Utilities
    "ss_to_display",
    "rank_times",
    # Constants
    "LINE_SPECS",
    "STROKE_CODES",
    "COURSE_CODES",
    "ROUND_CODES",
    # Version
    "__version__",
]
