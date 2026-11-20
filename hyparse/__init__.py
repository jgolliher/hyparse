"""hyparse: read HyTek swim meet files (.hy3 entries/results, .ev3 and .hyv event files,
.rec records files) and write .hy3 entries and .rec records files."""

from hyparse._values import format_time
from hyparse.checksum import hy3_checksum
from hyparse.events import read_ev3, read_hyv
from hyparse.exceptions import ChecksumError, FileFormatError, HyparseError
from hyparse.hy3 import read_hy3
from hyparse.hy3_writer import write_hy3
from hyparse.rec import read_rec, write_rec
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
    Record,
    RecordFile,
    RelayResult,
    Seeding,
    Split,
    Team,
)

__version__ = "0.5.0"

__all__ = [
    "read_hy3",
    "read_ev3",
    "read_hyv",
    "write_hy3",
    "read_rec",
    "write_rec",
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
    "Record",
    "RecordFile",
    "RelayResult",
    "Seeding",
    "Split",
    "Team",
    "HyparseError",
    "FileFormatError",
    "ChecksumError",
    "format_time",
    "hy3_checksum",
    "__version__",
]
