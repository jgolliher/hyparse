"""Code tables shared by every HyTek file format."""

from typing import Dict, Literal, Optional, cast

Course = Literal["Y", "S", "L"]
Gender = Literal["F", "M", "X"]
Discipline = Literal["swim", "dive"]
FileKind = Literal["entries", "roster", "results"]

STROKES = {
    "A": "Free",
    "B": "Back",
    "C": "Breast",
    "D": "Fly",
    "E": "Medley",
    "F": "1m Diving",
    "G": "3m Diving",
    "H": "Platform Diving",
}

DIVING_STROKES = {"F", "G", "H"}

COURSES = {
    "Y": "Short Course Yards",
    "S": "Short Course Meters",
    "L": "Long Course Meters",
}

ROUNDS = {
    "P": "Prelims",
    "F": "Finals",
    "S": "Semifinals",
    "T": "Time Trial",
}

FILE_KINDS: Dict[str, FileKind] = {
    "02": "entries",
    "03": "roster",
    "07": "results",
}


def parse_course(raw: Optional[str]) -> Optional[Course]:
    """Return Y, S or L; anything else (blank, unknown) becomes None."""
    raw = (raw or "").strip().upper()
    return cast(Course, raw) if raw in COURSES else None


def discipline(stroke: Optional[str]) -> Optional[Discipline]:
    """Return 'dive' for diving stroke codes (F/G/H), 'swim' for A-E."""
    if not stroke:
        return None
    return "dive" if stroke in DIVING_STROKES else "swim"


def normalize_gender(code: Optional[str]) -> Optional[Gender]:
    """Map the gender letters HyTek uses (F/W/G, M/B, X) to F, M or X."""
    if not code:
        return None
    code = code.upper()
    if code in ("F", "W", "G"):
        return "F"
    if code in ("M", "B"):
        return "M"
    if code == "X":
        return "X"
    return None
