"""Reader and writer for Meet Manager records files (.rec), e.g. NCAA, American or pool records.

A .rec file has no line breaks: it is a run of 120-byte rows in Latin-1. The first row is the
header; each row after it is one record. Columns are 0-based ``[start, end)``.

Header::

    0-3    "REC"
    3-7    number of 120-byte rows in the file, header included, right-aligned
    7-13   date the file was written, MMDDYY
    14     course: Y, S or L
    15-35  record list name, e.g. "NCAA"
    35-51  program that wrote it, e.g. "20WIN-MM038.0Gh"

Record::

    0      gender: 1 men, 2 women
    1      stroke: 1 free, 2 back, 3 breast, 4 fly, 5 IM (on a relay: medley relay)
    2-10   distance, left-aligned
    10     I individual, R relay
    11-41  swimmer name; on a relay, the team
    41-91  team; on a relay, the swimmers: "C. Curzan, A. Walsh, G. Walsh, M. Parker"
    91-97  date set, MMDDYY
    97-101 time in seconds: a 4-byte Microsoft Binary Format (MBF) single
    103-108 team abbreviation (first five letters of the team)
    108-111 "A20" on every sample; meaning unknown, kept as ``Record.flag``

Files often repeat a row and keep records that have since been broken; the reader keeps every
row so the file can be written back unchanged. ``RecordFile.current()`` gives the standing ones.
"""

import struct
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Optional, Union

from hyparse import _values as v
from hyparse.codes import Gender, parse_course
from hyparse.exceptions import FileFormatError
from hyparse.models import Record, RecordFile

ROW = 120
ENCODING = "latin-1"
DEFAULT_SOFTWARE = "20WIN-MM038.0Gh"
DEFAULT_FLAG = "A20"

GENDERS: Dict[str, Gender] = {"1": "M", "2": "F"}
STROKES = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}


def read_rec(path: Union[str, Path]) -> RecordFile:
    data = Path(path).read_bytes()
    if not data.startswith(b"REC"):
        raise FileFormatError("Not a records file: it doesn't start with REC", line_number=1)
    if len(data) % ROW:
        raise FileFormatError(f"Records file length {len(data)} isn't a multiple of {ROW}")
    header = data[:ROW].decode(ENCODING)
    records = [_record(data[i : i + ROW], i // ROW + 1) for i in range(ROW, len(data), ROW)]
    return RecordFile(
        path=str(path),
        name=v.text(header[15:35]),
        course=parse_course(header[14]),
        created=_mmddyy(header[7:13]),
        software=v.text(header[35:51]),
        records=records,
    )


def _record(row: bytes, number: int) -> Record:
    text = row.decode(ENCODING)
    gender, stroke = GENDERS.get(text[0]), STROKES.get(text[1])
    if gender is None:
        raise FileFormatError(f"Unknown gender code {text[0]!r}", line_number=number)
    if stroke is None:
        raise FileFormatError(f"Unknown stroke code {text[1]!r}", line_number=number)
    distance = v.integer(text[2:10])
    if not distance:
        raise FileFormatError(f"Invalid distance {text[2:10]!r}", line_number=number)
    if text[10] not in ("I", "R"):
        raise FileFormatError(f"Expected I or R, found {text[10]!r}", line_number=number)
    is_relay = text[10] == "R"
    first, second = v.text(text[11:41]), v.text(text[41:91])
    return Record(
        gender=gender,
        distance=distance,
        stroke=stroke,
        is_relay=is_relay,
        time=round(mbf_to_float(row[97:101]), 2),
        name=None if is_relay else first,
        team=first if is_relay else second,
        relay_swimmers=(
            [s.strip() for s in (second or "").split(",") if s.strip()] if is_relay else []
        ),
        team_abbreviation=v.text(text[103:108]),
        swim_date=_mmddyy(text[91:97]),
        flag=v.text(text[108:111]),
    )


def write_rec(records: RecordFile, path: Union[str, Path, None] = None) -> bytes:
    """Return the .rec bytes for ``records``; also save them to ``path`` if given.

    The header date is ``records.created`` (today if unset). Text is limited to Latin-1, and
    values longer than their column are cut off.
    """
    rows = [_header(records)] + [_row(r) for r in records.records]
    data = b"".join(rows)
    if path is not None:
        Path(path).write_bytes(data)
    return data


def _header(records: RecordFile) -> bytes:
    row = _Row()
    row.put(0, 3, "REC").put(3, 7, len(records.records) + 1, right=True)
    row.put(7, 13, _mmddyy_text(records.created or date.today()))
    row.put(14, 15, records.course).put(15, 35, records.name)
    row.put(35, 51, records.software or DEFAULT_SOFTWARE)
    return row.bytes()


def _row(r: Record) -> bytes:
    row = _Row()
    gender = {g: code for code, g in GENDERS.items()}.get(r.gender)
    stroke = {s: code for code, s in STROKES.items()}.get(r.stroke)
    if gender is None or stroke is None:
        raise ValueError(f"Can't write a {r.gender} {r.stroke} record to a .rec file")
    row.put(0, 1, gender).put(1, 2, stroke).put(2, 10, r.distance).put(
        10, 11, "R" if r.is_relay else "I"
    )
    if r.is_relay:
        row.put(11, 41, r.team).put(41, 91, ", ".join(r.relay_swimmers))
    else:
        row.put(11, 41, r.name).put(41, 91, r.team)
    row.put(91, 97, _mmddyy_text(r.swim_date))
    abbreviation = r.team_abbreviation
    if abbreviation is None and not r.is_relay and r.team:
        abbreviation = r.team[:5]
    row.put(103, 108, abbreviation).put(108, 111, r.flag or DEFAULT_FLAG)
    out = row.bytes()
    return out[:97] + float_to_mbf(r.time) + out[101:]


class _Row:
    def __init__(self) -> None:
        self.chars = [" "] * ROW

    def put(self, start: int, end: int, value: object, right: bool = False) -> "_Row":
        text = v.latin1("" if value is None else str(value))[: end - start]
        text = text.rjust(end - start) if right else text.ljust(end - start)
        self.chars[start:end] = list(text)
        return self

    def bytes(self) -> bytes:
        return "".join(self.chars).encode(ENCODING)


def mbf_to_float(raw: bytes) -> float:
    """A 4-byte Microsoft Binary Format single (what old BASIC programs stored) as a float."""
    if len(raw) != 4:
        raise ValueError("An MBF single is 4 bytes")
    if raw[3] == 0:
        return 0.0
    # MBF: mantissa (3 bytes, sign in the top bit of the third), then the exponent byte.
    # IEEE single: sign, exponent 2 lower than MBF's, the same 23-bit mantissa.
    sign, exponent = raw[2] >> 7, raw[3] - 2
    bits = (sign << 31) | (exponent << 23) | ((raw[2] & 0x7F) << 16) | (raw[1] << 8) | raw[0]
    return float(struct.unpack("<f", struct.pack("<I", bits))[0])


def float_to_mbf(value: float) -> bytes:
    """``value`` as a 4-byte MBF single, rounded to single precision as Meet Manager does."""
    if value == 0:
        return b"\x00\x00\x00\x00"
    (bits,) = struct.unpack("<I", struct.pack("<f", value))
    sign, exponent, mantissa = bits >> 31, (bits >> 23) & 0xFF, bits & 0x7FFFFF
    if exponent == 0 or exponent > 253:
        raise ValueError(f"{value} can't be stored as an MBF single")
    return bytes(
        [mantissa & 0xFF, (mantissa >> 8) & 0xFF, (sign << 7) | (mantissa >> 16), exponent + 2]
    )


def _mmddyy(raw: str) -> Optional[date]:
    """Two-digit years follow Python's rule: 00-68 are 2000s, 69-99 are 1900s."""
    try:
        return datetime.strptime(raw.strip(), "%m%d%y").date()
    except ValueError:
        return None


def _mmddyy_text(day: Optional[date]) -> str:
    return day.strftime("%m%d%y") if day else ""
