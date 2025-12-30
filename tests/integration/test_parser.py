"""Integration tests for Hy3File parser."""

import pytest
import pandas as pd
from hyparse import Hy3File


@pytest.fixture
def sample_file(fixtures_dir):
    """Path to sample minimal .hy3 file."""
    return fixtures_dir / "sample_minimal.hy3"


class TestHy3FileBasicParsing:
    """Test basic file parsing functionality."""

    def test_file_loads_successfully(self, sample_file):
        """Test that a valid .hy3 file loads without crashing."""
        hy3 = Hy3File(str(sample_file))

        assert hy3 is not None
        assert hy3.file_name == str(sample_file)

    def test_nonexistent_file_raises_error(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            Hy3File("/path/to/nonexistent/file.hy3")

    def test_raw_lines_loaded(self, sample_file):
        """Test that raw lines are loaded from file."""
        hy3 = Hy3File(str(sample_file))

        assert hy3.raw_lines is not None
        assert len(hy3.raw_lines) > 0
        assert isinstance(hy3.raw_lines, list)

    def test_parse_errors_tracked(self, sample_file):
        """Test that parse errors are tracked."""
        hy3 = Hy3File(str(sample_file))

        assert hasattr(hy3, "parse_errors")
        assert isinstance(hy3.parse_errors, list)


class TestMeetInfoParsing:
    """Test parsing of meet information."""

    def test_meet_info_extracted(self, sample_file):
        """Test that meet info is extracted from B1/B2 lines."""
        hy3 = Hy3File(str(sample_file))

        assert hy3.meet_info is not None
        assert hy3.meet_info.meet_name is not None
        assert hy3.meet_info.facility_name is not None

    def test_meet_dates_parsed(self, sample_file):
        """Test that meet dates are parsed correctly."""
        hy3 = Hy3File(str(sample_file))

        assert hy3.meet_info.meet_start_date is not None
        assert hy3.meet_info.meet_end_date is not None

    def test_meet_course_parsed(self, sample_file):
        """Test that course type is parsed."""
        hy3 = Hy3File(str(sample_file))

        assert hy3.meet_info.course in ["L", "S", "Y", None]


class TestTeamParsing:
    """Test parsing of team information."""

    def test_teams_extracted(self, sample_file):
        """Test that teams are extracted from C1 lines."""
        hy3 = Hy3File(str(sample_file))

        assert isinstance(hy3.teams, dict)
        assert len(hy3.teams) > 0

    def test_team_structure(self, sample_file):
        """Test that team objects have correct structure."""
        hy3 = Hy3File(str(sample_file))

        # Get first team
        team_abbr = list(hy3.teams.keys())[0]
        team = hy3.teams[team_abbr]

        assert team.team_abbreviation == team_abbr
        assert team.full_team_name is not None

    def test_teams_stored_by_abbreviation(self, sample_file):
        """Test that teams are keyed by abbreviation."""
        hy3 = Hy3File(str(sample_file))

        for abbr, team in hy3.teams.items():
            assert team.team_abbreviation == abbr


class TestAthleteParsing:
    """Test parsing of athlete information."""

    def test_athletes_extracted(self, sample_file):
        """Test that athletes are extracted from D1 lines."""
        hy3 = Hy3File(str(sample_file))

        assert isinstance(hy3.athletes, dict)
        assert len(hy3.athletes) > 0

    def test_athlete_structure(self, sample_file):
        """Test that athlete objects have correct structure."""
        hy3 = Hy3File(str(sample_file))

        # Get first athlete
        mm_id = list(hy3.athletes.keys())[0]
        athlete = hy3.athletes[mm_id]

        assert athlete.mm_id == mm_id
        assert athlete.team is not None

    def test_athletes_stored_by_mm_id(self, sample_file):
        """Test that athletes are keyed by MM ID."""
        hy3 = Hy3File(str(sample_file))

        for mm_id, athlete in hy3.athletes.items():
            assert athlete.mm_id == mm_id


class TestIndividualResultParsing:
    """Test parsing of individual results."""

    def test_individual_results_extracted(self, sample_file):
        """Test that individual results are extracted from E1/E2 lines."""
        hy3 = Hy3File(str(sample_file))

        assert isinstance(hy3.individual_results, list)
        assert len(hy3.individual_results) > 0

    def test_individual_result_structure(self, sample_file):
        """Test that individual result objects have correct fields."""
        hy3 = Hy3File(str(sample_file))

        result = hy3.individual_results[0]

        assert result.mm_athlete_id is not None
        assert result.event_no is not None
        assert result.i_r_flag == "I"

    def test_e1_e2_merged(self, sample_file):
        """Test that E1 and E2 lines are merged correctly."""
        hy3 = Hy3File(str(sample_file))

        result = hy3.individual_results[0]

        # Should have data from both E1 (entry) and E2 (result)
        assert result.distance is not None  # From E1
        assert result.time is not None  # From E2


class TestDataFrameConversion:
    """Test conversion to pandas DataFrames."""

    def test_individual_results_to_df(self, sample_file):
        """Test conversion of individual results to DataFrame."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_individual_df_columns(self, sample_file):
        """Test that DataFrame has expected columns."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        expected_cols = [
            "mm_athlete_id",
            "event_no",
            "time",
            "first_name",
            "last_name",
            "team",
        ]

        for col in expected_cols:
            assert col in df.columns

    def test_stroke_names_mapped(self, sample_file):
        """Test that stroke codes are mapped to names."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        assert "stroke" in df.columns
        # Should have readable stroke names, not just codes
        if len(df) > 0:
            assert df["stroke"].iloc[0] in [
                "Free",
                "Back",
                "Breast",
                "Fly",
                "Medley",
                "Unknown",
            ]

    def test_athletes_merged_with_results(self, sample_file):
        """Test that athlete data is merged with results."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        # Should have athlete info merged in
        assert "first_name" in df.columns
        assert "last_name" in df.columns
        assert "gender" in df.columns

    def test_times_converted_to_numeric(self, sample_file):
        """Test that time strings are converted to numeric."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        if "time" in df.columns and len(df) > 0:
            # Time should be numeric (float) not string
            assert pd.api.types.is_numeric_dtype(df["time"])

    def test_display_times_added(self, sample_file):
        """Test that display time columns are added."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.individual_results_to_df()

        assert "display_time" in df.columns
        if len(df) > 0 and not pd.isna(df["time"].iloc[0]):
            # Display time should be formatted string
            assert isinstance(df["display_time"].iloc[0], str)


class TestRelayResultParsing:
    """Test parsing of relay results."""

    def test_relay_results_list_exists(self, sample_file):
        """Test that relay results list exists (even if empty)."""
        hy3 = Hy3File(str(sample_file))

        assert hasattr(hy3, "relay_results")
        assert isinstance(hy3.relay_results, list)

    def test_relay_results_to_df(self, sample_file):
        """Test conversion of relay results to DataFrame."""
        hy3 = Hy3File(str(sample_file))
        df = hy3.relay_results_to_df()

        assert isinstance(df, pd.DataFrame)
        # May be empty if no relay results in sample file


class TestParserRobustness:
    """Test parser robustness and error handling."""

    def test_parser_continues_after_errors(self, sample_file):
        """Test that parser continues parsing after errors."""
        hy3 = Hy3File(str(sample_file))

        # Even with errors, should have parsed some data
        assert hy3.meet_info is not None or len(hy3.teams) > 0

    def test_empty_file_handling(self, tmp_path):
        """Test handling of empty file."""
        empty_file = tmp_path / "empty.hy3"
        empty_file.write_text("")

        hy3 = Hy3File(str(empty_file))

        # Should not crash
        assert len(hy3.raw_lines) == 0

    def test_malformed_line_handling(self, tmp_path):
        """Test handling of malformed lines."""
        malformed_file = tmp_path / "malformed.hy3"
        malformed_file.write_text(
            "INVALID LINE\nB1Test                                                                                                                                                   00\n"
        )

        hy3 = Hy3File(str(malformed_file))

        # Should not crash, may have parse errors
        assert isinstance(hy3.parse_errors, list)


class TestReprMethod:
    """Test __repr__ methods."""

    def test_hy3file_repr(self, sample_file):
        """Test Hy3File string representation."""
        hy3 = Hy3File(str(sample_file))
        repr_str = repr(hy3)

        assert "Hy3File" in repr_str
        assert str(sample_file) in repr_str
