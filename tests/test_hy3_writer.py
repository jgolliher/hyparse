"""Writing .hy3 entries files."""

from datetime import date, datetime

import pytest

from hyparse import (
    Athlete,
    FileInfo,
    Hy3File,
    IndividualEntry,
    Meet,
    Seeding,
    Team,
    hy3_checksum,
    read_hy3,
    write_hy3,
)
from tests.conftest import INVITATIONAL, LOUISVILLE, entry_file


@pytest.mark.parametrize("meet", [LOUISVILLE, INVITATIONAL])
def test_team_manager_files_write_back_unchanged(meet, tmp_path):
    path = entry_file(meet)
    out = tmp_path / "out.hy3"
    write_hy3(read_hy3(path), out)
    assert out.read_bytes() == path.read_bytes()


def small_file(**athlete) -> Hy3File:
    return Hy3File(
        path="",
        file_info=FileInfo(
            file_type="02",
            description="Meet Entries",
            vendor="Deckside",
            software="Deckside 1",
            created=datetime(2026, 11, 18, 9, 5),
            licensed_to="University of Tennessee",
        ),
        meet=Meet(name="Test Invite", start_date=date(2026, 12, 3), course="Y"),
        teams=[Team(code="TENN", name="University of Tennessee", team_type="COL")],
        athletes=[
            Athlete(
                team_code="TENN",
                team_athlete_id="7",
                gender="F",
                last_name="Hősz",
                first_name="Zoë",
                **athlete,
            )
        ],
        entries=[
            IndividualEntry(
                team_code="TENN",
                team_athlete_id="7",
                event_number=12,
                event_gender="F",
                distance=1650,
                stroke="A",
                seed_time=None,
                exhibition=True,
                seeding=Seeding(round="P", heat=1, lane=3),
            )
        ],
    )


def test_written_lines_are_valid_and_read_back():
    text = write_hy3(small_file(citizenship="POL"))
    lines = text.split("\r\n")
    assert lines[-1] == "" and [line[:2] for line in lines[:-1]] == [
        "A1", "B1", "B2", "C1", "C2", "C3", "D1", "E1", "E2",
    ]  # fmt: skip
    assert all(len(line) == 130 for line in lines[:-1])
    assert all(hy3_checksum(line[:-2]) == line[-2:] for line in lines[:-1])
    assert lines[0][58:75] == "11182026  9:05 AM"


def test_values_round_trip(tmp_path):
    out = tmp_path / "out.hy3"
    write_hy3(small_file(citizenship="POL"), out)
    hy3 = read_hy3(out, strict=True)
    assert hy3.kind == "entries"
    assert hy3.athletes[0].first_name == "Zoë"  # in Latin-1
    assert hy3.athletes[0].last_name == "Hosz"  # ő isn't: it loses its accent
    entry = hy3.entries[0]
    assert (entry.event_number, entry.distance, entry.stroke) == (12, 1650, "A")
    assert entry.seed_time is None  # NT
    assert entry.exhibition is True
    assert (entry.seeding.heat, entry.seeding.lane) == (1, 3)


def test_no_time_is_written_as_zero():
    e1 = next(line for line in write_hy3(small_file()).split("\r\n") if line.startswith("E1"))
    assert e1[43:60] == "      0Y    0.00Y"


def test_foreign_citizenship_is_starred():
    d1 = lambda f: next(x for x in write_hy3(f).split("\r\n") if x.startswith("D1"))  # noqa: E731
    assert d1(small_file(citizenship="POL"))[101] == "*"
    assert d1(small_file(citizenship="USA"))[101] == " "
    assert d1(small_file())[101] == " "
