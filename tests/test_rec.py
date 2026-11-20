"""Meet Manager records files (.rec)."""

from datetime import date

import pytest

from hyparse import FileFormatError, Record, RecordFile, format_time, read_rec, write_rec
from hyparse.rec import float_to_mbf, mbf_to_float
from tests.conftest import RECORD_FILES, records_file


@pytest.mark.parametrize(
    "name, list_name, course, rows",
    [
        ("AMER-y", "American", "Y", 62),
        ("NCAA-y", "NCAA", "Y", 63),
        ("USO-y", "US Open", "Y", 63),
        ("AJIAC-y", "Pool", "Y", 63),
        ("TNINV-y", "Meet", "Y", 63),
        ("WORLD-l", "World", "L", 40),
    ],
)
def test_header(name, list_name, course, rows):
    recs = read_rec(records_file(name))
    assert (recs.name, recs.course, len(recs.records)) == (list_name, course, rows)
    assert recs.created == date(2026, 11, 20)
    assert recs.software == "20WIN-MM038.0Gh"


def test_individual_record():
    ledecky = read_rec(records_file("AMER-y")).records[0]
    assert (ledecky.gender, ledecky.distance, ledecky.stroke, ledecky.is_relay) == (
        "F", 1650, "A", False,
    )  # fmt: skip
    assert format_time(ledecky.time) == "15:01.41"
    assert (ledecky.name, ledecky.team, ledecky.team_abbreviation) == (
        "Katie Ledecky", "Gator Swim Club", "Gator",
    )  # fmt: skip
    assert ledecky.swim_date == date(2023, 3, 12)
    assert ledecky.relay_swimmers == []


def test_relay_record():
    relay = read_rec(records_file("AMER-y")).records[2]
    assert (relay.gender, relay.distance, relay.stroke, relay.is_relay) == ("F", 200, "E", True)
    assert (relay.name, relay.team, relay.time) == (None, "Virginia", 91.10)
    assert relay.relay_swimmers == ["C. Curzan", "A. Walsh", "G. Walsh", "M. Parker"]


def test_long_course_world_records():
    recs = {
        (r.gender, r.distance, r.stroke): r for r in read_rec(records_file("WORLD-l")).current()
    }
    assert format_time(recs[("F", 400, "A")].time) == "3:55.38"
    assert recs[("M", 200, "E")].name == "Ryan Lochte"
    assert recs[("M", 200, "E")].swim_date == date(2011, 7, 28)


@pytest.mark.parametrize("path", RECORD_FILES, ids=lambda p: p.name)
def test_write_reproduces_file(path):
    """Meet Manager's file, read and written back, gives the same bytes."""
    assert write_rec(read_rec(path)) == path.read_bytes()


def test_current_drops_repeats_and_broken_records():
    pool = read_rec(records_file("AJIAC-y"))
    current = pool.current()
    assert len(current) == len({r.event_key for r in pool.records}) == 36
    back = [r for r in current if r.event_key == ("M", 100, "B", False)]
    assert [(r.name, r.time) for r in back] == [("Hubert Kos", 43.86)]  # not Thorman's 44.07


def test_current_keeps_ties():
    swim = dict(gender="M", distance=50, stroke="A", time=18.12)
    recs = RecordFile(
        path="",
        records=[Record(name="A", **swim), Record(name="B", **swim), Record(name="A", **swim)],
    )
    assert [r.name for r in recs.current()] == ["A", "B"]


def test_write_new_file(tmp_path):
    recs = RecordFile(
        path="",
        name="Tennessee",
        course="Y",
        created=date(2026, 11, 20),
        records=[
            Record(gender="F", distance=50, stroke="A", time=20.87, name="Camille Spink",
                   team="Tennessee", swim_date=date(2026, 2, 20)),
            Record(gender="F", distance=200, stroke="A", is_relay=True, time=84.76,
                   team="Tennessee", swim_date=date(2026, 11, 6),
                   relay_swimmers=["C. Crush", "C. Spink", "J. Crooks", "L. Tigert"]),
        ],
    )  # fmt: skip
    path = tmp_path / "TENN-y.rec"
    data = write_rec(recs, path)
    assert len(data) == 3 * 120 and path.read_bytes() == data
    back = read_rec(path)
    assert (back.name, back.course, back.created) == ("Tennessee", "Y", date(2026, 11, 20))
    spink, relay = back.records
    assert (spink.name, spink.team, spink.team_abbreviation, spink.time) == (
        "Camille Spink", "Tennessee", "Tenne", 20.87,
    )  # fmt: skip
    assert spink.flag == "A20"
    assert (relay.team, relay.time, relay.relay_swimmers[2]) == ("Tennessee", 84.76, "J. Crooks")


@pytest.mark.parametrize("seconds", [17.82, 40.42, 91.10, 901.41, 0.01, 3599.99])
def test_mbf_round_trip(seconds):
    assert round(mbf_to_float(float_to_mbf(seconds)), 2) == seconds


def test_mbf_known_bytes():
    assert round(mbf_to_float(bytes.fromhex("3d5a618a")), 2) == 901.41
    assert float_to_mbf(0) == b"\0\0\0\0" and mbf_to_float(b"\0\0\0\0") == 0.0


def test_not_a_records_file(tmp_path):
    path = tmp_path / "bad.rec"
    path.write_bytes(b"XYZ".ljust(120))
    with pytest.raises(FileFormatError, match="REC"):
        read_rec(path)


def test_truncated_file(tmp_path):
    path = tmp_path / "short.rec"
    path.write_bytes(records_file("NCAA-y").read_bytes()[:-10])
    with pytest.raises(FileFormatError, match="multiple of 120"):
        read_rec(path)


def test_unknown_stroke(tmp_path):
    data = bytearray(records_file("NCAA-y").read_bytes())
    data[121] = ord("7")
    path = tmp_path / "odd.rec"
    path.write_bytes(bytes(data))
    with pytest.raises(FileFormatError, match="Line 2: Unknown stroke code '7'"):
        read_rec(path)
