"""Helpers that turn raw field text into typed values. Blank or unparseable text becomes None."""

from datetime import date, datetime
from typing import Optional


def text(raw: str) -> Optional[str]:
    raw = raw.strip()
    return raw or None


def integer(raw: str) -> Optional[int]:
    try:
        return int(raw.strip())
    except ValueError:
        return None


def positive_int(raw: str) -> Optional[int]:
    """Heats, lanes and places: 0 means 'not assigned'."""
    value = integer(raw)
    return value if value else None


def number(raw: str) -> Optional[float]:
    try:
        return float(raw.strip())
    except ValueError:
        return None


def time(raw: str) -> Optional[float]:
    """Seconds as a float. HyTek writes 0, 0.00 or blanks for 'no time'."""
    value = number(raw)
    return value if value else None


def mmddyyyy(raw: str) -> Optional[date]:
    """Dates in .hy3 files: MMDDYYYY."""
    return _date(raw.strip(), "%m%d%Y")


def slashed_date(raw: str) -> Optional[date]:
    """Dates in event files: MM/DD/YYYY."""
    return _date(raw.strip(), "%m/%d/%Y")


def _date(raw: str, fmt: str) -> Optional[date]:
    try:
        return datetime.strptime(raw, fmt).date()
    except ValueError:
        return None


def format_time(seconds: Optional[float]) -> str:
    """Display a time in seconds the way meet software does: 58.32, 1:52.42, 15:15.15."""
    if seconds is None:
        return "NT"
    minutes, secs = divmod(round(seconds * 100), 6000)
    secs_text = (
        f"{secs // 100:02d}.{secs % 100:02d}" if minutes else f"{secs // 100}.{secs % 100:02d}"
    )
    return f"{minutes}:{secs_text}" if minutes else secs_text
