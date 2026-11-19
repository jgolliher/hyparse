import pytest

from hyparse import _values as v
from hyparse import format_time


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (None, "NT"),
        (22.92, "22.92"),
        (59.999, "1:00.00"),
        (112.42, "1:52.42"),
        (915.15, "15:15.15"),
    ],
)
def test_format_time(seconds, expected):
    assert format_time(seconds) == expected


@pytest.mark.parametrize(
    "raw, expected", [("", None), ("0", None), ("0.00", None), (" 49.60", 49.6)]
)
def test_time(raw, expected):
    assert v.time(raw) == expected


def test_dates():
    assert str(v.mmddyyyy("02112004")) == "2004-02-11"
    assert v.mmddyyyy("") is None and v.mmddyyyy("99999999") is None
    assert str(v.slashed_date("11/17/2026")) == "2026-11-17"


def test_positive_int():
    assert v.positive_int(" 0") is None and v.positive_int(" 4") == 4 and v.positive_int("") is None
