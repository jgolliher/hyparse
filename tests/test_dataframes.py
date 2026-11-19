import pytest

from hyparse import read_hy3
from hyparse.dataframes import entries_df, relay_results_df, results_df, splits_df
from tests.conftest import DATA, LOUISVILLE, entry_file

pytest.importorskip("pandas")

LSU = DATA / "results" / "Meet Results-2024 Tennessee vs LSU-27Jan2024-001.hy3"


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


def test_splits_df_joins_back_to_results():
    hy3 = read_hy3(LSU)
    splits = splits_df(hy3)
    assert len(splits) == sum(len(r.splits) for r in hy3.results + hy3.relay_results)
    assert "splits" not in results_df(hy3).columns
    key = ["team_code", "team_athlete_id", "event_number", "round"]
    individual = splits[splits.kind == "individual"].merge(results_df(hy3), on=key)
    assert len(individual) == (splits.kind == "individual").sum()
    first = individual.iloc[0]
    assert (first.last_name, first.split_distance, first.split_time) == ("Barnes", 50, 24.90)


def test_splits_df_relay_legs():
    hy3 = read_hy3(LSU)
    first = hy3.relay_results[0]
    df = splits_df(hy3)
    key = ["team_code", "relay_letter", "event_number", "round"]
    rows = df[(df[key] == [getattr(first, k) for k in key]).all(axis=1)]
    assert list(rows.leg_athlete_id) == ["230", "230", "253", "253", "219", "219", "249", "249"]
