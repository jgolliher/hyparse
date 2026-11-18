"""Reader for HyTek .hy3 files: meet entries (A1 type 02) and meet results (A1 type 07).

Every line is 130 characters: a 2-character line code, 126 characters of fixed-width fields
and a 2-digit checksum. Column positions below are 0-based, end-exclusive slices, verified
against the sample files in ``data/`` and the format notes in ``resources/``.

How entry and result lines pair up:

* ``E1`` (individual) / ``F1`` (relay) describe an athlete or relay in an event with a seed time.
* An ``E2`` / ``F2`` after it with a time is a result for one round.
* An ``E2`` / ``F2`` after it with a *blank* time is a pre-assigned heat/lane in an entry file
  (dual meets), not a result.
* ``F3`` lists the relay swimmers and their legs (up to 8).
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from hyparse import _values as v
from hyparse.checksum import has_valid_checksum, hy3_checksum
from hyparse.codes import FILE_KINDS, discipline, normalize_gender, parse_course
from hyparse.exceptions import ChecksumError, FileFormatError
from hyparse.models import (
    Athlete,
    Contact,
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

LINE_LENGTH = 130

Span = Tuple[int, int]

LINE_SPECS: Dict[str, Dict[str, Span]] = {
    "A1": {
        "file_type": (2, 4),
        "description": (4, 29),
        "vendor": (29, 44),
        "software": (44, 58),
        "date": (58, 66),
        "time": (67, 75),
        "licensed_to": (75, 128),
    },
    "B1": {
        "name": (2, 47),
        "facility": (47, 92),
        "start_date": (92, 100),
        "end_date": (100, 108),
        "age_up_date": (108, 116),
    },
    "B2": {
        "course": (98, 99),
    },
    "C1": {
        "code": (2, 7),
        "name": (7, 37),
        "short_name": (37, 53),
        "lsc": (53, 55),
    },
    "C2": {
        "name": (2, 32),
        "address": (32, 62),
        "city": (62, 92),
        "state": (92, 94),
        "postal_code": (94, 104),
        "country": (104, 107),
    },
    "C3": {
        "email": (92, 128),
    },
    "D1": {
        "gender": (2, 3),
        "team_athlete_id": (3, 8),
        "last_name": (8, 28),
        "first_name": (28, 48),
        "preferred_name": (48, 68),
        "middle_initial": (68, 69),
        "registration_id": (69, 83),
        "birth_date": (88, 96),
        "age": (97, 99),
        "class_year": (99, 101),
        "citizenship": (112, 115),
    },
    "E1": {
        "team_athlete_id": (3, 8),
        "event_gender": (13, 14),
        "distance": (17, 21),
        "stroke": (21, 22),
        "low_age": (22, 25),
        "high_age": (25, 28),
        "event_number": (38, 41),
        "seed_time_1": (43, 50),
        "seed_course_1": (50, 51),
        "seed_time_2": (52, 59),
        "seed_course_2": (59, 60),
        "exhibition": (83, 84),
    },
    "E2": {
        "round": (2, 3),
        "time": (3, 11),
        "course": (11, 12),
        "time_code": (12, 13),
        "dq_code": (13, 15),
        "heat": (20, 23),
        "lane": (23, 26),
        "heat_place": (26, 29),
        "place": (29, 33),
        "points": (33, 36),
        "reaction_time": (82, 87),
        "swim_date": (87, 95),
    },
    "F1": {
        "team_code": (2, 7),
        "relay_letter": (7, 8),
        "event_gender": (13, 14),
        "distance": (17, 21),
        "stroke": (21, 22),
        "low_age": (22, 25),
        "high_age": (25, 28),
        "event_number": (38, 41),
        "seed_time_1": (43, 50),
        "seed_course_1": (50, 51),
        "seed_time_2": (52, 59),
        "seed_course_2": (59, 60),
        "exhibition": (83, 84),
    },
    "F2": {
        "round": (2, 3),
        "time": (3, 11),
        "course": (11, 12),
        "time_code": (12, 13),
        "dq_code": (13, 15),
        "heat": (20, 23),
        "lane": (23, 26),
        "heat_place": (26, 29),
        "place": (29, 33),
        "points": (33, 36),
        "reaction_time_1": (82, 87),
        "reaction_time_2": (87, 92),
        "reaction_time_3": (92, 97),
        "reaction_time_4": (97, 102),
        "swim_date": (102, 110),
    },
}

# F3: up to 8 swimmer slots of 13 characters starting at column 2.
# Within a slot: gender [0], athlete id [1:6], last-name abbreviation [6:11],
# event gender [11], leg number [12].
F3_SLOTS = 8
F3_SLOT_WIDTH = 13
F3_FIRST_SLOT = 2


def fields(line: str, line_code: str) -> Dict[str, str]:
    """Slice a line into raw (stripped) field strings using LINE_SPECS."""
    return {name: line[a:b].strip() for name, (a, b) in LINE_SPECS[line_code].items()}


def read_hy3(path: Union[str, Path], strict: bool = False) -> Hy3File:
    """Read a .hy3 entries or results file.

    With ``strict=False`` (default) problems are collected in ``Hy3File.issues`` and parsing
    continues. With ``strict=True`` the first problem raises ``FileFormatError`` (or
    ``ChecksumError``).
    """
    with open(path, encoding="latin-1") as f:
        lines = [line.rstrip("\r\n") for line in f]
    return _Hy3Reader(str(path), lines, strict).read()


class _Hy3Reader:
    def __init__(self, path: str, lines: List[str], strict: bool):
        self.path = path
        self.lines = lines
        self.strict = strict
        self.issues: List[ParseIssue] = []
        self.file_info = FileInfo()
        self.meet = Meet()
        self.teams: List[Team] = []
        self.athletes: List[Athlete] = []
        self.entries: List[IndividualEntry] = []
        self.relay_entries: List[RelayEntry] = []
        self.results: List[IndividualResult] = []
        self.relay_results: List[RelayResult] = []
        self.team: Optional[Team] = None
        self.pending_e1: Optional[Dict[str, Any]] = None
        self.pending_f1: Optional[Dict[str, Any]] = None

    def read(self) -> Hy3File:
        if not self.lines or not self.lines[0].startswith("A1"):
            raise FileFormatError("Not a .hy3 file: the first line must be an A1 line")

        for number, line in enumerate(self.lines, start=1):
            if not line.strip():
                continue
            self._check_line(number, line)
            handler = getattr(self, f"_line_{line[:2]}", None)
            if handler:  # Other codes (G1 splits, H1 DQ text, D2-D7, ...) are skipped.
                handler(number, line)
        self._flush()

        return Hy3File(
            path=self.path,
            file_info=self.file_info,
            meet=self.meet,
            teams=self.teams,
            athletes=self.athletes,
            entries=self.entries,
            relay_entries=self.relay_entries,
            results=self.results,
            relay_results=self.relay_results,
            issues=self.issues,
        )

    # --- problems ---------------------------------------------------------------------------

    def _issue(self, number: int, line: str, message: str, error=FileFormatError) -> None:
        if self.strict:
            raise error(message, line_number=number)
        self.issues.append(ParseIssue(line_number=number, message=message, line=line))

    def _check_line(self, number: int, line: str) -> None:
        if len(line) != LINE_LENGTH:
            self._issue(number, line, f"Line is {len(line)} characters, expected {LINE_LENGTH}")
        elif not has_valid_checksum(line):
            expected = hy3_checksum(line[:-2])
            self._issue(
                number,
                line,
                f"Checksum mismatch: expected {expected!r}, found {line[-2:]!r}",
                ChecksumError,
            )

    # --- header lines -----------------------------------------------------------------------

    def _line_A1(self, number: int, line: str) -> None:
        f = fields(line, "A1")
        created = None
        if f["date"]:
            try:
                created = datetime.strptime(f"{f['date']} {f['time']}", "%m%d%Y %I:%M %p")
            except ValueError:
                created_date = v.mmddyyyy(f["date"])
                created = (
                    datetime.combine(created_date, datetime.min.time()) if created_date else None
                )
        self.file_info = FileInfo(
            file_type=v.text(f["file_type"]),
            kind=FILE_KINDS.get(f["file_type"]),
            description=v.text(f["description"]),
            vendor=v.text(f["vendor"]),
            software=v.text(f["software"]),
            created=created,
            licensed_to=v.text(f["licensed_to"]),
        )

    def _line_B1(self, number: int, line: str) -> None:
        f = fields(line, "B1")
        self.meet.name = v.text(f["name"])
        self.meet.facility = v.text(f["facility"])
        self.meet.start_date = v.mmddyyyy(f["start_date"])
        self.meet.end_date = v.mmddyyyy(f["end_date"])
        self.meet.age_up_date = v.mmddyyyy(f["age_up_date"])

    def _line_B2(self, number: int, line: str) -> None:
        self.meet.course = parse_course(fields(line, "B2")["course"])

    def _line_C1(self, number: int, line: str) -> None:
        self._flush()
        f = fields(line, "C1")
        if not f["code"]:
            self._issue(number, line, "Team line has no team code")
            self.team = None
            return
        self.team = Team(
            code=f["code"],
            name=v.text(f["name"]),
            short_name=v.text(f["short_name"]),
            lsc=v.text(f["lsc"]),
        )
        self.teams.append(self.team)

    def _line_C2(self, number: int, line: str) -> None:
        if self.team is None:
            return
        f = fields(line, "C2")
        contact = self.team.contact or Contact()
        contact.name = v.text(f["name"])
        contact.address = v.text(f["address"])
        contact.city = v.text(f["city"])
        contact.state = v.text(f["state"])
        contact.postal_code = v.text(f["postal_code"])
        contact.country = v.text(f["country"])
        self.team.contact = contact

    def _line_C3(self, number: int, line: str) -> None:
        if self.team is None:
            return
        contact = self.team.contact or Contact()
        contact.email = v.text(fields(line, "C3")["email"])
        self.team.contact = contact

    def _line_D1(self, number: int, line: str) -> None:
        self._flush()
        if self.team is None:
            self._issue(number, line, "Athlete line before any team line")
            return
        f = fields(line, "D1")
        if not f["team_athlete_id"]:
            self._issue(number, line, "Athlete line has no athlete ID")
            return
        self.athletes.append(
            Athlete(
                team_code=self.team.code,
                team_athlete_id=f["team_athlete_id"],
                gender=normalize_gender(f["gender"]),
                last_name=v.text(f["last_name"]),
                first_name=v.text(f["first_name"]),
                preferred_name=v.text(f["preferred_name"]),
                middle_initial=v.text(f["middle_initial"]),
                registration_id=v.text(f["registration_id"]),
                birth_date=v.mmddyyyy(f["birth_date"]),
                age=v.integer(f["age"]),
                class_year=v.text(f["class_year"]),
                citizenship=v.text(f["citizenship"]),
            )
        )

    # --- individual events ------------------------------------------------------------------

    def _line_E1(self, number: int, line: str) -> None:
        self._flush()
        f = fields(line, "E1")
        self.pending_e1 = {
            **_event_ref(f),
            **_seed(f),
            "team_code": self.team.code if self.team else None,
            "team_athlete_id": f["team_athlete_id"],
            "exhibition": f["exhibition"] == "X",
        }

    def _line_E2(self, number: int, line: str) -> None:
        if self.pending_e1 is None:
            self._issue(number, line, "E2 line without a preceding E1 line")
            return
        f = fields(line, "E2")
        entry, self.pending_e1 = self.pending_e1, None
        if not f["time"]:
            self.entries.append(IndividualEntry(**entry, seeding=_seeding(f)))
            return
        self.results.append(
            IndividualResult(**entry, **_swim(f), reaction_time=v.time(f["reaction_time"]))
        )

    # --- relays -----------------------------------------------------------------------------

    def _line_F1(self, number: int, line: str) -> None:
        self._flush()
        f = fields(line, "F1")
        self.pending_f1 = {
            "entry": {
                **_event_ref(f),
                **_seed(f),
                "team_code": f["team_code"] or (self.team.code if self.team else ""),
                "relay_letter": v.text(f["relay_letter"]),
                "exhibition": f["exhibition"] == "X",
            },
            "f2": None,
            "legs": [],
        }

    def _line_F2(self, number: int, line: str) -> None:
        if self.pending_f1 is None:
            self._issue(number, line, "F2 line without a preceding F1 line")
            return
        self.pending_f1["f2"] = fields(line, "F2")

    def _line_F3(self, number: int, line: str) -> None:
        if self.pending_f1 is None:
            self._issue(number, line, "F3 line without a preceding F1 line")
            return
        for slot in range(F3_SLOTS):
            start = F3_FIRST_SLOT + slot * F3_SLOT_WIDTH
            chunk = line[start : start + F3_SLOT_WIDTH]
            athlete_id = chunk[1:6].strip()
            if not athlete_id:
                continue
            leg = chunk[12]
            self.pending_f1["legs"].append(
                RelayLeg(
                    leg=int(leg) if leg.isdigit() else slot + 1,
                    team_athlete_id=athlete_id,
                    gender=normalize_gender(chunk[0]),
                )
            )

    # --- finishing pending records ----------------------------------------------------------

    def _flush(self) -> None:
        """Close any E1/F1 record still waiting for its follow-up lines."""
        if self.pending_e1 is not None:
            self.entries.append(IndividualEntry(**self.pending_e1))
            self.pending_e1 = None
        if self.pending_f1 is not None:
            relay, self.pending_f1 = self.pending_f1, None
            entry, f2, legs = relay["entry"], relay["f2"], relay["legs"]
            if f2 is None:
                self.relay_entries.append(RelayEntry(**entry, legs=legs))
            elif not f2["time"]:
                self.relay_entries.append(RelayEntry(**entry, legs=legs, seeding=_seeding(f2)))
            else:
                reactions = [v.time(f2[f"reaction_time_{i}"]) for i in range(1, 5)]
                self.relay_results.append(
                    RelayResult(**entry, **_swim(f2), legs=legs, reaction_times=reactions)
                )


def _event_ref(f: Dict[str, str]) -> Dict[str, Any]:
    # Diving lines put the number of dives in the distance field (and the dive order in lane).
    is_dive = discipline(f["stroke"]) == "dive"
    return {
        "event_number": v.integer(f["event_number"]),
        "event_gender": normalize_gender(f["event_gender"]),
        "distance": None if is_dive else v.integer(f["distance"]),
        "stroke": v.text(f["stroke"]),
        "low_age": v.integer(f["low_age"]),
        "high_age": v.integer(f["high_age"]),
    }


def _seed(f: Dict[str, str]) -> Dict[str, Any]:
    """Entry files put the seed in slot 2 (slot 1 is '0'); result files repeat it in both."""
    for slot in ("2", "1"):
        seed = v.time(f[f"seed_time_{slot}"])
        if seed is not None:
            return {"seed_time": seed, "seed_course": parse_course(f[f"seed_course_{slot}"])}
    return {"seed_time": None, "seed_course": None}


def _seeding(f: Dict[str, str]) -> Seeding:
    return Seeding(
        round=v.text(f["round"]), heat=v.positive_int(f["heat"]), lane=v.positive_int(f["lane"])
    )


def _swim(f: Dict[str, str]) -> Dict[str, Any]:
    return {
        "round": v.text(f["round"]),
        "time": v.time(f["time"]),
        "course": parse_course(f["course"]),
        "time_code": v.text(f["time_code"]),
        "dq_code": v.text(f["dq_code"]),
        "heat": v.positive_int(f["heat"]),
        "lane": v.positive_int(f["lane"]),
        "heat_place": v.positive_int(f["heat_place"]),
        "place": v.positive_int(f["place"]),
        "points": v.number(f["points"]),
        "swim_date": v.mmddyyyy(f["swim_date"]),
    }
