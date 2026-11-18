"""Result files (.hy3 type 07) exported by Meet Manager."""

import pytest

from hyparse import read_hy3
from tests.conftest import DATA, RESULT_FILES, line_counts

LSU = DATA / "hy3" / "Meet Results-2024 Tennessee vs LSU-27Jan2024-001.hy3"


@pytest.mark.parametrize("path", RESULT_FILES, ids=lambda p: p.name[:40])
def test_every_result_file_parses_cleanly(path):
    hy3 = read_hy3(path, strict=True)
    counts = line_counts(path)
    assert hy3.kind == "results"
    assert len(hy3.athletes) == counts["D1"]
    assert len(hy3.results) == counts["E2"]
    assert len(hy3.relay_results) == counts["F2"]
    assert hy3.entries == [] and hy3.relay_entries == []
    for r in hy3.results + hy3.relay_results:
        assert r.event_number and r.round in ("P", "F", "S", "T")
        if r.discipline == "swim":
            assert r.distance and (r.lane is None or 1 <= r.lane <= 10)
        else:
            assert r.distance is None  # diving: the distance field holds the dive count


def test_every_result_athlete_exists():
    hy3 = read_hy3(LSU)
    for r in hy3.results:
        assert hy3.athlete(r.team_code, r.team_athlete_id) is not None


def test_individual_result_fields():
    first = read_hy3(LSU).results[0]
    assert (first.team_code, first.team_athlete_id, first.event_number) == ("LSU", "250", 5)
    assert (first.distance, first.stroke, first.event_gender) == (200, "A", "F")
    assert (first.round, first.time, first.course) == ("F", 107.18, "Y")
    assert (first.heat, first.lane, first.heat_place, first.place) == (1, 3, 5, 5)
    assert first.reaction_time == 0.73
    assert str(first.swim_date) == "2024-01-27"


def test_relay_result_fields():
    relay = read_hy3(LSU).relay_results[0]
    assert (relay.team_code, relay.relay_letter, relay.time) == ("LSU", "A", 99.58)
    assert [leg.team_athlete_id for leg in relay.legs] == ["230", "253", "219", "249"]
    assert relay.reaction_times == [0.63, 0.30, 0.29, 0.25]


def test_disqualifications_have_time_code():
    hy3 = read_hy3(DATA / "hy3" / "2022_SEC.hy3")
    dqs = [r for r in hy3.results if r.time_code == "Q"]
    assert dqs and all(r.dq_code for r in dqs)


def test_relays_with_alternate_legs():
    """NCAA results list legs 5-8 (prelim/final swap-ins) in the same F3 line."""
    legs = {
        leg.leg for path in RESULT_FILES for r in read_hy3(path).relay_results for leg in r.legs
    }
    assert legs >= {1, 2, 3, 4, 5}
