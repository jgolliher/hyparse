"""Entry files (.hy3 type 02) exported by Team Manager."""

import pytest

from hyparse import read_hy3
from tests.conftest import INVITATIONAL, LOUISVILLE, entry_file, line_counts


@pytest.fixture(scope="module")
def louisville():
    return read_hy3(entry_file(LOUISVILLE))


@pytest.fixture(scope="module")
def invitational():
    return read_hy3(entry_file(INVITATIONAL))


def entries_for(hy3, athlete_id):
    return {e.event_number: e for e in hy3.entries if e.team_athlete_id == athlete_id}


def test_file_info_and_meet(louisville):
    assert louisville.kind == "entries"
    assert louisville.file_info.software == "Win-TM 8.0Gb"
    assert louisville.file_info.licensed_to == "University of Tennessee"
    assert louisville.meet.name == "2023 Tennessee vs. Louisville"
    assert str(louisville.meet.start_date) == "2023-10-12"
    assert louisville.meet.course == "L"
    assert louisville.issues == []


@pytest.mark.parametrize("meet", [LOUISVILLE, INVITATIONAL])
def test_every_entry_line_is_read(meet):
    hy3 = read_hy3(entry_file(meet))
    counts = line_counts(entry_file(meet))
    assert len(hy3.athletes) == counts["D1"]
    assert len(hy3.entries) == counts["E1"]
    assert len(hy3.relay_entries) == counts["F1"]
    assert hy3.results == [] and hy3.relay_results == []


def test_team_contact(louisville):
    contact = louisville.teams[0].contact
    assert louisville.teams[0].code == "TENN"
    assert contact.name == "Matt Kredich"
    assert contact.city == "Knoxville"
    assert contact.postal_code == "37996"
    assert contact.email == "mkredich@utk.edu"


def test_athlete_fields(invitational):
    regan = invitational.athlete("TENN", "989")
    assert (regan.last_name, regan.first_name) == ("Rathwell", "Regan")
    assert regan.registration_id == "0F064B807C5E4A"
    assert str(regan.birth_date) == "2004-02-11"
    assert (regan.age, regan.class_year, regan.citizenship) == (22, "GS", "CAN")


def test_seed_time_comes_from_second_seed_slot(invitational):
    back = entries_for(invitational, "989")[7]
    assert (back.distance, back.stroke, back.event_gender) == (200, "B", "F")
    assert (back.seed_time, back.seed_course) == (112.42, "Y")
    assert back.seeding is None


@pytest.mark.parametrize(
    "athlete_id, event_number, heat, lane",
    [("1005", 9, 2, 4), ("985", 12, 1, 4)],  # Aurnou-Rhees 100 breast, Espernberger 200 fly
)
def test_pre_seeded_heat_and_lane(louisville, athlete_id, event_number, heat, lane):
    entry = entries_for(louisville, athlete_id)[event_number]
    assert (entry.seeding.round, entry.seeding.heat, entry.seeding.lane) == ("P", heat, lane)


def test_exhibition_flag(louisville):
    entries = entries_for(louisville, "1005")
    assert entries[9].exhibition is True
    assert entries[23].exhibition is False


def test_relay_entry_legs_and_seeding(louisville):
    relay = louisville.relay_entries[0]
    assert (relay.team_code, relay.relay_letter, relay.event_number) == ("TENN", "A", 1)
    assert (relay.seed_time, relay.seed_course) == (109.66, "L")
    assert [leg.leg for leg in relay.legs] == [1, 2, 3, 4]
    assert relay.legs[0].team_athlete_id == "959"
    assert (relay.seeding.heat, relay.seeding.lane) == (1, 4)


def test_relay_without_named_swimmers(invitational):
    assert any(not r.legs for r in invitational.relay_entries)
