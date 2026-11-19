"""Event files (.ev3 and .hyv) a meet host sends to teams."""

import pytest

from hyparse import FileFormatError, read_ev3, read_hyv
from tests.conftest import INVITATIONAL, LOUISVILLE, event_file


def test_ev3_meet_header():
    meet = read_ev3(event_file(INVITATIONAL, "ev3")).meet
    assert meet.name == "2026 Tennessee Invitational"
    assert meet.facility == "Allan Jones Aquatic Center"
    assert (str(meet.start_date), str(meet.end_date)) == ("2026-11-17", "2026-11-20")
    assert meet.course == "Y"
    assert str(meet.entry_time_cutoff) == "2026-09-01"
    assert (meet.city, meet.state, meet.postal_code) == ("Knoxville", "TN", "37919")


@pytest.mark.parametrize(
    "meet, limits",
    [(LOUISVILLE, (5, 3, 2)), (INVITATIONAL, (9, 5, 4))],
)
def test_ev3_entry_limits(meet, limits):
    """Louisville is a dual meet with 3 individual / 2 relay events per athlete."""
    got = read_ev3(event_file(meet, "ev3")).meet.entry_limits
    assert (got.total, got.individual, got.relay) == limits


def test_ev3_events():
    events = {e.number: e for e in read_ev3(event_file(INVITATIONAL, "ev3")).events}
    assert len(events) == 42
    mile = events[1]
    assert (mile.gender, mile.distance, mile.stroke, mile.is_relay) == ("F", 1650, "A", False)
    assert (mile.round, mile.session, mile.day, mile.start_time) == ("F", 1, 1, "05:00PM")
    relay = events[3]
    assert (relay.is_relay, relay.stroke, relay.relay_swimmers) == (True, "E", 4)
    dive = events[16]
    assert (dive.stroke, dive.discipline, dive.distance, dive.num_dives) == ("F", "dive", None, 6)
    assert events[7].round == "P"


@pytest.mark.parametrize("meet", [LOUISVILLE, INVITATIONAL])
def test_hyv_matches_ev3(meet):
    ev3 = read_ev3(event_file(meet, "ev3"))
    hyv = read_hyv(event_file(meet, "hyv"))
    keys = ("number", "gender", "low_age", "high_age", "distance", "stroke", "is_relay", "round")
    assert [[getattr(e, k) for k in keys] for e in hyv.events] == [
        [getattr(e, k) for k in keys] for e in ev3.events
    ]
    assert (hyv.meet.name, hyv.meet.start_date, hyv.meet.course) == (
        ev3.meet.name,
        ev3.meet.start_date,
        ev3.meet.course,
    )
    assert hyv.meet.entry_limits is None


def test_wrong_field_count_names_the_line(write_file):
    lines = event_file(INVITATIONAL, "ev3").read_text(encoding="latin-1").splitlines()
    lines[3] = lines[3].replace(";", ";;", 1)
    with pytest.raises(FileFormatError, match="Line 4: Expected 30"):
        read_ev3(write_file(lines, "bad.ev3"))


def test_unknown_event_type(write_file):
    lines = event_file(INVITATIONAL, "hyv").read_text(encoding="latin-1").splitlines()
    lines[1] = lines[1].replace(";I;", ";Z;")
    with pytest.raises(FileFormatError, match="Line 2"):
        read_hyv(write_file(lines, "bad.hyv"))
