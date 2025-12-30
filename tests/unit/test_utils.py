"""Unit tests for utility functions in hyparse.utils."""
import pytest
import pandas as pd
import numpy as np
import math
from hyparse.utils import ss_to_display, rank_times


class TestSsToDisplay:
    """Tests for ss_to_display function."""

    def test_seconds_under_minute(self):
        """Test conversion of times under 60 seconds."""
        assert ss_to_display(45.67) == "45.67"
        assert ss_to_display(0.5) == "0.50"
        assert ss_to_display(59.99) == "59.99"

    def test_seconds_over_minute(self):
        """Test conversion of times over 60 seconds."""
        assert ss_to_display(83.45) == "1:23.45"
        assert ss_to_display(125.0) == "2:05.00"
        assert ss_to_display(60.0) == "1:00.00"

    def test_exact_minutes(self):
        """Test conversion of exact minute values."""
        assert ss_to_display(120.0) == "2:00.00"
        assert ss_to_display(180.0) == "3:00.00"

    def test_long_times(self):
        """Test conversion of very long times."""
        assert ss_to_display(600.5) == "10:00.50"
        assert ss_to_display(3661.25) == "61:01.25"

    def test_string_input(self):
        """Test that valid string inputs are converted."""
        assert ss_to_display("45.67") == "45.67"
        assert ss_to_display("83.45") == "1:23.45"

    def test_invalid_string(self):
        """Test that invalid strings return 'Invalid'."""
        assert ss_to_display("not a number") == "Invalid"
        assert ss_to_display("") == "Invalid"
        assert ss_to_display("12.34.56") == "Invalid"

    def test_none_input(self):
        """Test that None returns 'Invalid'."""
        assert ss_to_display(None) == "Invalid"

    def test_nan_input(self):
        """Test that NaN returns 'NaN'."""
        assert ss_to_display(float('nan')) == "NaN"
        assert ss_to_display(np.nan) == "NaN"

    def test_negative_values(self):
        """Test that negative values return 'Invalid'."""
        assert ss_to_display(-10.5) == "Invalid"
        assert ss_to_display(-0.01) == "Invalid"

    def test_zero(self):
        """Test that zero is handled correctly."""
        assert ss_to_display(0) == "0.00"
        assert ss_to_display(0.0) == "0.00"

    def test_very_small_values(self):
        """Test very small positive values."""
        assert ss_to_display(0.01) == "0.01"
        assert ss_to_display(0.001) == "0.00"  # Rounded to 2 decimals

    def test_formatting_precision(self):
        """Test that formatting maintains 2 decimal precision."""
        assert ss_to_display(45.678) == "45.68"  # Rounded
        assert ss_to_display(45.671) == "45.67"  # Rounded down
        assert ss_to_display(59.995) == "60.00"  # Rounded up


class TestRankTimes:
    """Tests for rank_times function."""

    def test_basic_ranking(self):
        """Test basic ranking within a single event."""
        df = pd.DataFrame({
            'event_no': [1, 1, 1, 1],
            'seed_time': [50.5, 48.2, 52.1, 49.0]
        })
        result = rank_times(df, rank_col='seed_time', out_col='rank')

        assert 'rank' in result.columns
        assert list(result['rank']) == [3.0, 1.0, 4.0, 2.0]

    def test_ranking_with_ties(self):
        """Test ranking when there are tied values."""
        df = pd.DataFrame({
            'event_no': [1, 1, 1, 1],
            'seed_time': [50.0, 48.0, 50.0, 49.0]
        })
        result = rank_times(df, rank_col='seed_time', out_col='rank')

        # Ranks should be: 48.0=1, 49.0=2, 50.0=3, 50.0=3 (both get rank 3)
        assert result['rank'].tolist() == [3.0, 1.0, 3.0, 2.0]

    def test_ranking_multiple_events(self):
        """Test ranking across multiple events (grouped)."""
        df = pd.DataFrame({
            'event_no': [1, 1, 2, 2],
            'seed_time': [50.0, 48.0, 45.0, 47.0]
        })
        result = rank_times(df, rank_col='seed_time', out_col='rank')

        # Event 1: 48.0=1, 50.0=2
        # Event 2: 45.0=1, 47.0=2
        assert result.loc[result['event_no'] == 1, 'rank'].tolist() == [2.0, 1.0]
        assert result.loc[result['event_no'] == 2, 'rank'].tolist() == [1.0, 2.0]

    def test_nan_values_ranked_last(self):
        """Test that NaN values are ranked last."""
        df = pd.DataFrame({
            'event_no': [1, 1, 1, 1],
            'seed_time': [50.0, np.nan, 48.0, np.nan]
        })
        result = rank_times(df, rank_col='seed_time', out_col='rank')

        # 48.0=1, 50.0=2, NaN=3, NaN=3 (both NaN get same rank at bottom)
        assert result['rank'].tolist()[0] == 2.0  # 50.0
        assert math.isnan(result['rank'].tolist()[1])  # NaN ranked as NaN
        assert result['rank'].tolist()[2] == 1.0  # 48.0

    def test_custom_group_columns(self):
        """Test ranking with custom grouping columns."""
        df = pd.DataFrame({
            'event_no': [1, 1, 1, 1],
            'gender': ['M', 'M', 'F', 'F'],
            'seed_time': [50.0, 48.0, 52.0, 51.0]
        })
        result = rank_times(
            df,
            group_cols=['event_no', 'gender'],
            rank_col='seed_time',
            out_col='rank'
        )

        # Males: 48.0=1, 50.0=2
        # Females: 51.0=1, 52.0=2
        male_ranks = result.loc[result['gender'] == 'M', 'rank'].tolist()
        female_ranks = result.loc[result['gender'] == 'F', 'rank'].tolist()

        assert male_ranks == [2.0, 1.0]
        assert female_ranks == [2.0, 1.0]

    def test_missing_rank_column_raises_error(self):
        """Test that missing rank column raises KeyError."""
        df = pd.DataFrame({
            'event_no': [1, 1],
            'other_col': [50.0, 48.0]
        })

        with pytest.raises(KeyError, match="Ranking column 'seed_time' not found"):
            rank_times(df, rank_col='seed_time')

    def test_missing_group_column_raises_error(self):
        """Test that missing group column raises KeyError."""
        df = pd.DataFrame({
            'other_col': [1, 1],
            'seed_time': [50.0, 48.0]
        })

        with pytest.raises(KeyError, match="Grouping columns not found"):
            rank_times(df, group_cols=['event_no'], rank_col='seed_time')

    def test_non_numeric_column_raises_error(self):
        """Test that non-numeric rank column raises TypeError."""
        df = pd.DataFrame({
            'event_no': [1, 1],
            'seed_time': ['fast', 'slow']  # Non-numeric
        })

        with pytest.raises(TypeError, match="Failed to rank column"):
            rank_times(df, rank_col='seed_time')

    def test_default_parameters(self):
        """Test that default parameters work correctly."""
        df = pd.DataFrame({
            'event_no': [1, 1, 2, 2],
            'seed_time_ss': [50.0, 48.0, 45.0, 47.0]
        })
        # Using defaults: group_cols=['event_no'], rank_col='seed_time_ss', out_col='rank'
        result = rank_times(df)

        assert 'rank' in result.columns
        assert len(result) == 4

    def test_empty_dataframe(self):
        """Test ranking on an empty DataFrame."""
        df = pd.DataFrame(columns=['event_no', 'seed_time'])
        result = rank_times(df, rank_col='seed_time')

        assert 'rank' in result.columns
        assert len(result) == 0

    def test_single_row(self):
        """Test ranking with a single row."""
        df = pd.DataFrame({
            'event_no': [1],
            'seed_time': [50.0]
        })
        result = rank_times(df, rank_col='seed_time')

        assert result['rank'].tolist() == [1.0]

    def test_ascending_order(self):
        """Test that lower values get lower (better) ranks."""
        df = pd.DataFrame({
            'event_no': [1, 1, 1],
            'seed_time': [100.0, 50.0, 75.0]
        })
        result = rank_times(df, rank_col='seed_time')

        # 50.0 should be rank 1 (fastest/lowest)
        # 75.0 should be rank 2
        # 100.0 should be rank 3 (slowest/highest)
        assert result['rank'].tolist() == [3.0, 1.0, 2.0]
