"""Format-neutral data models returned by every hyparse reader.

Times are seconds as floats (``None`` when the file has no time). Dates are ``datetime.date``.
Athletes are identified within a file by ``(team_code, team_athlete_id)``: the ID comes from
Team Manager in entry files and from Meet Manager in result files.
"""

from datetime import date, datetime
from typing import Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field

from hyparse.codes import Course, Discipline, FileKind, Gender, discipline


class _Model(BaseModel):
    model_config = ConfigDict(frozen=False, extra="forbid")


class FileInfo(_Model):
    """File descriptor (``A1`` line in .hy3)."""

    file_type: Optional[str] = None
    kind: Optional[FileKind] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    software: Optional[str] = None
    created: Optional[datetime] = None
    licensed_to: Optional[str] = None


class EntryLimits(_Model):
    """Per-athlete entry limits for a meet."""

    total: Optional[int] = None
    individual: Optional[int] = None
    relay: Optional[int] = None


class Meet(_Model):
    name: Optional[str] = None
    facility: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    age_up_date: Optional[date] = None
    course: Optional[Course] = None
    # Event-file only fields
    entry_time_cutoff: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    entry_limits: Optional[EntryLimits] = None


class Contact(_Model):
    """Team contact (``C2`` address + ``C3`` contact lines)."""

    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None


class Team(_Model):
    code: str
    name: Optional[str] = None
    short_name: Optional[str] = None
    lsc: Optional[str] = None
    team_type: Optional[str] = None  # C1: COL, AGE, HS, MAS, OTH, REC
    registration: Optional[str] = None  # C2: governing body, e.g. USS (USA Swimming)
    contact: Optional[Contact] = None


class Athlete(_Model):
    team_code: str
    team_athlete_id: str
    gender: Optional[Gender] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    preferred_name: Optional[str] = None
    middle_initial: Optional[str] = None
    registration_id: Optional[str] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    class_year: Optional[str] = None
    citizenship: Optional[str] = None
    # D1 column 111: 'X' on some athletes in Team Manager entry files. Meaning unknown; kept
    # so a file can be written back unchanged.
    flag: Optional[str] = None


class Event(_Model):
    """An event definition from an event file (.ev3 / .hyv)."""

    number: int
    gender: Optional[Gender] = None
    low_age: Optional[int] = None
    high_age: Optional[int] = None
    distance: Optional[int] = None
    stroke: Optional[str] = None
    is_relay: bool = False
    round: Optional[str] = None  # 'P' = prelims/finals, 'F' = timed final
    num_dives: Optional[int] = None
    session: Optional[int] = None
    session_order: Optional[int] = None
    day: Optional[int] = None
    start_time: Optional[str] = None
    course: Optional[Course] = None
    relay_swimmers: Optional[int] = None

    @property
    def discipline(self) -> Optional[Discipline]:
        return discipline(self.stroke)


class _EventRef(_Model):
    """Event identity carried on every entry/result line."""

    event_number: Optional[int] = None
    event_gender: Optional[Gender] = None
    distance: Optional[int] = None
    stroke: Optional[str] = None
    low_age: Optional[int] = None
    high_age: Optional[int] = None
    num_dives: Optional[int] = None  # diving: written where swims have the distance

    @property
    def discipline(self) -> Optional[Discipline]:
        return discipline(self.stroke)


class Seeding(_Model):
    """Heat/lane assigned in an entry file before the meet (dual meets)."""

    round: Optional[str] = None
    heat: Optional[int] = None
    lane: Optional[int] = None


class _SwimFields(_Model):
    round: Optional[str] = None
    time: Optional[float] = None
    course: Optional[Course] = None
    time_code: Optional[str] = None
    dq_code: Optional[str] = None
    heat: Optional[int] = None
    lane: Optional[int] = None
    heat_place: Optional[int] = None
    place: Optional[int] = None
    points: Optional[float] = None
    swim_date: Optional[date] = None


class IndividualEntry(_EventRef):
    team_code: Optional[str] = None
    team_athlete_id: str
    seed_time: Optional[float] = None
    seed_course: Optional[Course] = None
    exhibition: bool = False
    seeding: Optional[Seeding] = None
    # E1 column 91: 'C' on some Team Manager seeds, perhaps a corrected or converted time.
    # Meaning unconfirmed; kept so a file can be written back unchanged.
    seed_flag: Optional[str] = None


class Split(_Model):
    """One cumulative split (``G1`` line) of a result.

    ``number`` is the split slot as written by Meet Manager. Its scale varies between meets
    (e.g. a 200 can be written as 2/4/6/8 or 1/2/3/4), so ``distance`` is derived from it as
    ``event distance * number / last number``. ``time`` is ``None`` when no touch was recorded.
    ``leg`` is the relay leg (1-4) the split falls in; ``None`` for individual results.
    """

    number: int
    distance: Optional[int] = None
    time: Optional[float] = None
    leg: Optional[int] = None


class IndividualResult(_SwimFields, IndividualEntry):
    reaction_time: Optional[float] = None
    splits: List[Split] = Field(default_factory=list)


class RelayLeg(_Model):
    leg: int
    team_athlete_id: str
    gender: Optional[Gender] = None


class RelayEntry(_EventRef):
    team_code: str
    relay_letter: Optional[str] = None
    seed_time: Optional[float] = None
    seed_course: Optional[Course] = None
    exhibition: bool = False
    legs: List[RelayLeg] = Field(default_factory=list)
    seeding: Optional[Seeding] = None


class RelayResult(_SwimFields, RelayEntry):
    reaction_times: List[Optional[float]] = Field(default_factory=list)
    splits: List[Split] = Field(default_factory=list)


class ParseIssue(_Model):
    line_number: int
    message: str
    line: str = ""


class Hy3File(_Model):
    """Everything read from one .hy3 file (entries or results)."""

    path: str
    file_info: FileInfo
    meet: Meet
    teams: List[Team] = Field(default_factory=list)
    athletes: List[Athlete] = Field(default_factory=list)
    entries: List[IndividualEntry] = Field(default_factory=list)
    relay_entries: List[RelayEntry] = Field(default_factory=list)
    results: List[IndividualResult] = Field(default_factory=list)
    relay_results: List[RelayResult] = Field(default_factory=list)
    issues: List[ParseIssue] = Field(default_factory=list)

    @property
    def kind(self) -> Optional[str]:
        return self.file_info.kind

    def athlete(self, team_code: str, team_athlete_id: str) -> Optional[Athlete]:
        for a in self.athletes:
            if a.team_code == team_code and a.team_athlete_id == team_athlete_id:
                return a
        return None


class EventFile(_Model):
    """Everything read from one event file (.ev3 or .hyv)."""

    path: str
    format: Literal["ev3", "hyv"]
    meet: Meet
    events: List[Event] = Field(default_factory=list)


class Record(_Model):
    """One record from a records file (.rec): the time, who holds it, and when it was set.

    For a relay, ``team`` is the relay's team and ``relay_swimmers`` are the swimmers as the
    file writes them (often initial and last name, e.g. ``C. Curzan``); ``name`` is ``None``.
    """

    gender: Gender
    distance: int
    stroke: str  # A-E as in .hy3 files; on a relay, E is the medley relay
    is_relay: bool = False
    time: float
    name: Optional[str] = None
    team: Optional[str] = None
    team_abbreviation: Optional[str] = None
    relay_swimmers: List[str] = Field(default_factory=list)
    swim_date: Optional[date] = None
    # Columns 108-110: "A20" on every sample record. Meaning unknown (an age group or record
    # type?); kept so a file can be written back unchanged.
    flag: Optional[str] = None

    @property
    def event_key(self) -> Tuple[str, int, str, bool]:
        """What makes two records the same event within one file."""
        return (self.gender, self.distance, self.stroke, self.is_relay)


class RecordFile(_Model):
    """Everything read from one Meet Manager records file (.rec)."""

    path: str
    name: Optional[str] = None  # the record list, e.g. "NCAA", "American", "Pool"
    course: Optional[Course] = None
    created: Optional[date] = None
    # Header columns 35-50, e.g. "20WIN-MM038.0Gh": the program that wrote the file.
    software: Optional[str] = None
    records: List[Record] = Field(default_factory=list)

    def current(self) -> List[Record]:
        """The standing record for each event: the fastest time, in file order.

        Meet Manager files repeat rows and keep records that have since been broken; this drops
        both. Ties stay, one row per holder.
        """
        best: Dict[Tuple[str, int, str, bool], float] = {}
        for r in self.records:
            best[r.event_key] = min(r.time, best.get(r.event_key, r.time))
        out: List[Record] = []
        for r in self.records:
            if r.time == best[r.event_key] and r not in out:
                out.append(r)
        return out
