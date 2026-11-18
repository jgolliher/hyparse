import pytest

from hyparse import read_hy3
from hyparse.dataframes import entries_df, relay_results_df, results_df
from tests.conftest import DATA, LOUISVILLE, entry_file

pytest.importorskip("pandas")

LSU = DATA / "hy3" / "Meet Results-2024 Tennessee vs LSU-27Jan2024-001.hy3"


def test_results_df():
    df = results_df(read_hy3(LSU))
    row = df.iloc[0]
    assert (row.last_name, row.time_display, row.stroke_name) == ("Barnes", "1:47.18", "Free")
    assert row.meet_name == "2024 Tennessee vs. LSU"


def test_relay_results_df():
    df = relay_results_df(read_hy3(LSU))
    assert {"leg_1_athlete_id", "leg_4_reaction_time"} <= set(df.columns)


def test_entries_df():
    df = entries_df(read_hy3(entry_file(LOUISVILLE)))
    aurnou = df[(df.team_athlete_id == "1005") & (df.event_number == 9)].iloc[0]
    assert (aurnou.seed_heat, aurnou.seed_lane, aurnou.seed_display) == (2, 4, "1:14.29")
