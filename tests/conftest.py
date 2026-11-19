from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"
RESULT_FILES = sorted((DATA / "results").glob("*.hy3"))
ENTRY_FILES = sorted((DATA / "entries").glob("*.HY3"))

LOUISVILLE = "2023 Tennessee vs Louisville-12Oct2023"
INVITATIONAL = "2026 Tennessee Invitational-17Nov2026"


def entry_file(meet: str) -> Path:
    return DATA / "entries" / f"TENN-SE-Entries-{meet}-001.HY3"


def event_file(meet: str, ext: str) -> Path:
    return DATA / "events" / f"Meet Events-{meet}-002.{ext}"


def line_counts(path: Path) -> dict:
    counts: dict = {}
    for line in path.read_text(encoding="latin-1").splitlines():
        counts[line[:2]] = counts.get(line[:2], 0) + 1
    return counts


@pytest.fixture
def write_file(tmp_path):
    def _write(lines, name="test.hy3"):
        path = tmp_path / name
        path.write_text("\n".join(lines) + "\n", encoding="latin-1")
        return path

    return _write
