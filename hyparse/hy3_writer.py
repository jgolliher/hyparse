"""Writer for HyTek .hy3 meet entries files (A1 type 02), the file Team Manager exports.

``write_hy3(hy3)`` turns an ``Hy3File`` into the file's text. Reading a Team Manager entry file
and writing it back gives the same bytes; ``tests/test_hy3_writer.py`` checks this for both
sample files in ``data/entries/``.

Line order, as Team Manager writes it::

    A1, B1, B2
    per team:  C1, C2, C3
               per athlete:  D1, then per entry  E1 [E2 heat/lane]
               per relay:    F1 [F2 heat/lane] F3

Column positions are the reader's (``hyparse.hy3.LINE_SPECS``). A few columns that the reader
doesn't keep are written as Team Manager writes them in every sample file:

* B2: the meet course at 98 and 106, ``0.00`` at 102-105 and ``O`` at 107.
* E1/F1: event fee ``0.00`` at 32-37, and seed slot 1 as ``0`` plus the course.
* E1/F1: the event's gender type (col 14) is the event gender (M/F, the college codes).
* F1: ``0`` at col 11 and the event gender at col 12.
* F3: ``F`` in each swimmer slot before the leg number, for men's relays too.
* D1: ``*`` at col 101 when the citizenship is set and isn't USA.

Only entries are written: results in the ``Hy3File`` are ignored.
"""

import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

from hyparse.checksum import hy3_checksum
from hyparse.hy3 import F3_FIRST_SLOT, F3_SLOT_WIDTH, F3_SLOTS, LINE_LENGTH, LINE_SPECS
from hyparse.models import Athlete, Hy3File, IndividualEntry, RelayEntry, Seeding, Team

NEWLINE = "\r\n"
ENCODING = "latin-1"
ENTRIES_FILE_TYPE = "02"


def write_hy3(hy3: Hy3File, path: Union[str, Path, None] = None) -> str:
    """Return the .hy3 text for ``hy3``'s entries; also save it to ``path`` if given.

    Text is limited to Latin-1: other characters lose their accents (``ő`` → ``o``) or become
    ``?``. Values longer than their column are cut off.
    """
    text = "".join(line + NEWLINE for line in _Hy3Writer(hy3).lines())
    if path is not None:
        Path(path).write_bytes(text.encode(ENCODING))
    return text


class _Line:
    """One line being filled in: 128 characters of fields, then the checksum."""

    def __init__(self, code: str):
        self.code = code
        self.chars = list(code.ljust(LINE_LENGTH - 2))

    def put(self, start: int, end: int, value: object, right: bool = False) -> "_Line":
        text = _latin1("" if value is None else str(value))[: end - start]
        text = text.rjust(end - start) if right else text.ljust(end - start)
        self.chars[start:end] = list(text)
        return self

    def field(self, name: str, value: object, right: bool = False) -> "_Line":
        start, end = LINE_SPECS[self.code][name]
        return self.put(start, end, value, right)

    def done(self) -> str:
        content = "".join(self.chars)
        return content + hy3_checksum(content)


class _Hy3Writer:
    def __init__(self, hy3: Hy3File):
        self.hy3 = hy3
        self.course = hy3.meet.course or ""
        self.athletes: Dict[Tuple[str, str], Athlete] = {
            (a.team_code, a.team_athlete_id): a for a in hy3.athletes
        }

    def lines(self) -> Iterable[str]:
        yield self._a1()
        yield self._b1()
        yield self._b2()
        for team in self.hy3.teams:
            yield from self._team(team)

    # --- header -----------------------------------------------------------------------------

    def _a1(self) -> str:
        info = self.hy3.file_info
        created = info.created or datetime.now()
        line = _Line("A1")
        line.field("file_type", info.file_type or ENTRIES_FILE_TYPE)
        line.field("description", info.description or "Meet Entries")
        line.field("vendor", info.vendor)
        line.field("software", info.software)
        line.field("date", _mmddyyyy(created.date()))
        line.field("time", created.strftime("%I:%M %p").lstrip("0"), right=True)
        line.field("licensed_to", info.licensed_to)
        return line.done()

    def _b1(self) -> str:
        meet = self.hy3.meet
        line = _Line("B1")
        line.field("name", meet.name)
        line.field("facility", meet.facility)
        line.field("start_date", _mmddyyyy(meet.start_date))
        line.field("end_date", _mmddyyyy(meet.end_date))
        line.field("age_up_date", _mmddyyyy(meet.age_up_date))
        return line.done()

    def _b2(self) -> str:
        line = _Line("B2").field("course", self.course)
        return line.put(102, 106, "0.00").put(106, 107, self.course).put(107, 108, "O").done()

    # --- teams and athletes -----------------------------------------------------------------

    def _team(self, team: Team) -> Iterable[str]:
        contact = team.contact
        c1 = _Line("C1").field("code", team.code).field("name", team.name)
        c1.field("short_name", team.short_name).field("lsc", team.lsc)
        yield c1.field("team_type", team.team_type).done()

        c2 = _Line("C2")
        if contact:
            c2.field("name", contact.name).field("address", contact.address)
            c2.field("city", contact.city).field("state", contact.state)
            c2.field("postal_code", contact.postal_code).field("country", contact.country)
        yield c2.field("registration", team.registration).done()
        yield _Line("C3").field("email", contact.email if contact else None).done()

        entries: Dict[str, List[IndividualEntry]] = {}
        for entry in self.hy3.entries:
            if (entry.team_code or team.code) == team.code:
                entries.setdefault(entry.team_athlete_id, []).append(entry)
        for athlete in self.hy3.athletes:
            if athlete.team_code != team.code:
                continue
            yield self._d1(athlete)
            for entry in entries.pop(athlete.team_athlete_id, []):
                yield from self._entry(entry, athlete)
        for leftover in entries.values():  # entries for athletes the file doesn't list
            for entry in leftover:
                yield from self._entry(entry, None)

        for relay in self.hy3.relay_entries:
            if relay.team_code == team.code:
                yield from self._relay(relay)

    def _d1(self, a: Athlete) -> str:
        line = _Line("D1")
        line.field("gender", a.gender).field("team_athlete_id", a.team_athlete_id, right=True)
        line.field("last_name", a.last_name).field("first_name", a.first_name)
        line.field("preferred_name", a.preferred_name)
        line.field("middle_initial", a.middle_initial)
        line.field("registration_id", a.registration_id)
        line.field("birth_date", _mmddyyyy(a.birth_date))
        line.field("age", a.age, right=True).field("class_year", a.class_year)
        if a.citizenship and a.citizenship != "USA":
            line.put(101, 102, "*")
        return line.field("flag", a.flag).field("citizenship", a.citizenship).done()

    # --- entries ----------------------------------------------------------------------------

    def _entry(self, e: IndividualEntry, athlete: Optional[Athlete]) -> Iterable[str]:
        line = _Line("E1")
        line.put(2, 3, athlete.gender if athlete and athlete.gender else e.event_gender)
        line.field("team_athlete_id", e.team_athlete_id, right=True)
        line.put(8, 13, _abbreviation(athlete.last_name if athlete else None))
        self._event_fields(line, e)
        line.field("exhibition", "X" if e.exhibition else "")
        yield line.field("seed_flag", e.seed_flag).done()
        if e.seeding:
            yield _seeding_line("E2", e.seeding)

    def _relay(self, r: RelayEntry) -> Iterable[str]:
        line = _Line("F1").field("team_code", r.team_code).field("relay_letter", r.relay_letter)
        line.put(11, 12, "0").put(12, 13, r.event_gender)
        self._event_fields(line, r)
        yield line.field("exhibition", "X" if r.exhibition else "").done()
        if r.seeding:
            yield _seeding_line("F2", r.seeding)

        f3 = _Line("F3")
        for slot, leg in enumerate(r.legs[:F3_SLOTS]):
            athlete = self.athletes.get((r.team_code, leg.team_athlete_id))
            start = F3_FIRST_SLOT + slot * F3_SLOT_WIDTH
            f3.put(start, start + 1, leg.gender or (athlete.gender if athlete else ""))
            f3.put(start + 1, start + 6, leg.team_athlete_id, right=True)
            f3.put(start + 6, start + 11, _abbreviation(athlete.last_name if athlete else None))
            f3.put(start + 11, start + 12, "F")  # always F, even for men; maybe a round code
            f3.put(start + 12, start + 13, leg.leg)
        yield f3.done()

    def _event_fields(self, line: _Line, e: Union[IndividualEntry, RelayEntry]) -> None:
        """Event identity, fee and both seed slots: the same columns on E1 and F1."""
        line.field("event_gender", e.event_gender)
        line.put(14, 15, e.event_gender)  # gender type: M/F (men/women)
        distance = e.num_dives if e.discipline == "dive" else e.distance
        line.field("distance", distance, right=True).field("stroke", e.stroke)
        line.field("low_age", 0 if e.low_age is None else e.low_age, right=True)
        line.field("high_age", 109 if e.high_age is None else e.high_age, right=True)
        line.put(32, 38, "0.00", right=True)  # event fee
        line.field("event_number", e.event_number, right=True)
        course = e.seed_course or self.course
        line.field("seed_time_1", "0", right=True).field("seed_course_1", course)
        line.field("seed_time_2", _seed(e.seed_time), right=True)
        line.field("seed_course_2", course)


def _seeding_line(code: str, s: Seeding) -> str:
    line = _Line(code).field("round", s.round)
    return line.field("heat", s.heat, right=True).field("lane", s.lane, right=True).done()


def _seed(seconds: Optional[float]) -> str:
    """Seconds with two decimals (``112.42``); no time is ``0.00``."""
    return f"{seconds or 0:.2f}"


def _abbreviation(last_name: Optional[str]) -> str:
    return (last_name or "")[:5]


def _mmddyyyy(day: Optional[date]) -> str:
    return day.strftime("%m%d%Y") if day else ""


def _latin1(text: str) -> str:
    """Keep characters Latin-1 can hold; strip accents from the rest, else use ``?``."""
    out = []
    for ch in text:
        if ch in "\r\n\t":
            ch = " "
        try:
            ch.encode(ENCODING)
            out.append(ch)
        except UnicodeEncodeError:
            base = unicodedata.normalize("NFKD", ch)
            base = "".join(c for c in base if not unicodedata.combining(c))
            out.append(base if base and base.isascii() else "?")
    return "".join(out)
