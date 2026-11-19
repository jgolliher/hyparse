"""Readers for HyTek event files that a meet host sends to teams: .ev3 and .hyv.

Both are ``;``-separated text. Line 1 describes the meet; each following line is one event.
Field positions below are 1-based, matching how they're documented in the planning notes.
Unknown fields are ignored, but a line with the wrong number of fields raises
``FileFormatError`` so format changes are caught instead of silently misread.
"""

from pathlib import Path
from typing import List, Union

from hyparse import _values as v
from hyparse.codes import normalize_gender, parse_course
from hyparse.exceptions import FileFormatError
from hyparse.models import EntryLimits, Event, EventFile, Meet

EV3_HEADER_FIELDS = 35
EV3_EVENT_FIELDS = 30
HYV_HEADER_FIELDS = 11
HYV_EVENT_FIELDS = 18

# .hyv stores the stroke as a digit. 6 = diving, where the "distance" field is the board.
HYV_STROKES = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}
HYV_DIVING_BOARDS = {"1": "F", "3": "G", "2": "H"}  # 2 = platform (matches .ev3 "H")


def read_ev3(path: Union[str, Path]) -> EventFile:
    rows = _read_rows(path, strip_suffix="*>")
    header = _expect(rows[0], EV3_HEADER_FIELDS, 1)

    def f(n: int) -> str:
        return header[n - 1]

    meet = Meet(
        name=v.text(f(1)),
        facility=v.text(f(2)),
        start_date=v.slashed_date(f(3)),
        end_date=v.slashed_date(f(4)),
        age_up_date=v.slashed_date(f(5)),
        course=parse_course(f(6)[:1]),  # e.g. "YO" / "LO"
        entry_time_cutoff=v.slashed_date(f(17)),
        entry_limits=EntryLimits(
            total=v.integer(f(19)), individual=v.integer(f(20)), relay=v.integer(f(21))
        ),
        address=v.text(f(25)),
        city=v.text(f(27)),
        state=v.text(f(28)),
        postal_code=v.text(f(29)),
        country=v.text(f(30)),
    )

    events = []
    for number, row in enumerate(rows[1:], start=2):
        e = _expect(row, EV3_EVENT_FIELDS, number)
        is_relay = _relay_flag(e[4], number)
        events.append(
            Event(
                number=_required_int(e[0], "event number", number),
                round=v.text(e[2]),
                is_relay=is_relay,
                gender=normalize_gender(e[5]),
                low_age=v.integer(e[6]),
                high_age=v.integer(e[7]),
                distance=v.integer(e[8]) or None,  # 0 for diving
                stroke=v.text(e[9]),
                num_dives=v.integer(e[10]) or None,
                session=v.integer(e[21]),
                session_order=v.integer(e[22]),
                day=v.integer(e[23]),
                start_time=v.text(e[24]),
                course=parse_course(e[25]),
                relay_swimmers=(v.integer(e[29]) or None) if is_relay else None,
            )
        )
    return EventFile(path=str(path), format="ev3", meet=meet, events=events)


def read_hyv(path: Union[str, Path]) -> EventFile:
    """Read a .hyv event file. It has no entry limits, sessions or facility address."""
    rows = _read_rows(path)
    header = _expect(rows[0], HYV_HEADER_FIELDS, 1)
    meet = Meet(
        name=v.text(header[0]),
        start_date=v.slashed_date(header[1]),
        end_date=v.slashed_date(header[2]),
        age_up_date=v.slashed_date(header[3]),
        course=parse_course(header[4]),
        facility=v.text(header[5]),
    )

    events = []
    for number, row in enumerate(rows[1:], start=2):
        e = _expect(row, HYV_EVENT_FIELDS, number)
        stroke_digit, distance = e[7].strip(), e[6].strip()
        if stroke_digit == "6":
            stroke, distance_value = HYV_DIVING_BOARDS.get(distance), None
        else:
            stroke, distance_value = HYV_STROKES.get(stroke_digit), v.integer(distance)
        if stroke is None:
            raise FileFormatError(f"Unknown stroke code {stroke_digit!r}", line_number=number)
        low_age, high_age = v.integer(e[4]), v.integer(e[5])
        if not low_age and not high_age:  # .hyv writes 0/0 for open events; .ev3 writes 0/109
            low_age, high_age = 0, 109
        events.append(
            Event(
                number=_required_int(e[0], "event number", number),
                round=v.text(e[1]),
                gender=normalize_gender(e[2]),
                is_relay=_relay_flag(e[3], number),
                low_age=low_age,
                high_age=high_age,
                distance=distance_value,
                stroke=stroke,
            )
        )
    return EventFile(path=str(path), format="hyv", meet=meet, events=events)


def _read_rows(path: Union[str, Path], strip_suffix: str = "") -> List[List[str]]:
    with open(path, encoding="latin-1") as f:
        lines = [line.rstrip("\r\n") for line in f if line.strip()]
    if not lines:
        raise FileFormatError("Event file is empty")
    rows = []
    for line in lines:
        if strip_suffix and line.endswith(strip_suffix):
            line = line[: -len(strip_suffix)]
        rows.append(line.split(";"))
    return rows


def _expect(row: List[str], count: int, line_number: int) -> List[str]:
    if len(row) != count:
        raise FileFormatError(
            f"Expected {count} ';'-separated fields, found {len(row)}", line_number=line_number
        )
    return row


def _required_int(raw: str, name: str, line_number: int) -> int:
    value = v.integer(raw)
    if value is None:
        raise FileFormatError(f"Invalid {name} {raw!r}", line_number=line_number)
    return value


def _relay_flag(raw: str, line_number: int) -> bool:
    if raw not in ("I", "R"):
        raise FileFormatError(f"Expected I or R for event type, found {raw!r}", line_number)
    return raw == "R"
