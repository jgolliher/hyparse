"""hyparse: read HyTek swim meet files (.hy3 entries/results, .ev3 and .hyv event files)."""

from hyparse._values import format_time
from hyparse.checksum import hy3_checksum
from hyparse.events import read_ev3, read_hyv
from hyparse.exceptions import ChecksumError, FileFormatError, HyparseError
from hyparse.hy3 import read_hy3
from hyparse.models import (
    Athlete,
    Contact,
    EntryLimits,
    Event,
    EventFile,
    FileInfo,
    Hy3File,
    IndividualEntry,
    IndividualResult,
    Meet,
    ParseIssue,
    RelayEntry,
    RelayLeg,
    RelayResult,
    Seeding,
    Team,
)

__version__ = "0.4.0"

__all__ = [
    "read_hy3",
    "read_ev3",
    "read_hyv",
    "Athlete",
    "Contact",
    "EntryLimits",
    "Event",
    "EventFile",
    "FileInfo",
    "Hy3File",
    "IndividualEntry",
    "IndividualResult",
    "Meet",
    "ParseIssue",
    "RelayEntry",
    "RelayLeg",
    "RelayResult",
    "Seeding",
    "Team",
    "HyparseError",
    "FileFormatError",
    "ChecksumError",
    "format_time",
    "hy3_checksum",
    "__version__",
]
