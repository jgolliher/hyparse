"""Unit tests for data objects in hyparse.objects."""
import pytest
from hyparse.objects import (
    MeetInfo,
    Athlete,
    Team,
    IndividualResult,
    RelayResult
)


class TestMeetInfo:
    """Tests for MeetInfo dataclass."""

    def test_meetinfo_creation(self):
        """Test basic MeetInfo object creation."""
        meet = MeetInfo(
            meet_name="Test Championship",
            facility_name="Test Pool",
            meet_start_date="20251201",
            meet_end_date="20251203"
        )

        assert meet.meet_name == "Test Championship"
        assert meet.facility_name == "Test Pool"
        assert meet.meet_start_date == "20251201"
        assert meet.meet_end_date == "20251203"

    def test_meetinfo_optional_fields(self):
        """Test that optional fields default to None."""
        meet = MeetInfo()

        assert meet.meet_name is None
        assert meet.facility_name is None
        assert meet.elevation is None

    def test_meetinfo_to_dict(self):
        """Test conversion to dictionary."""
        meet = MeetInfo(
            meet_name="Test Meet",
            course="Y"
        )
        result = meet.to_dict()

        assert isinstance(result, dict)
        assert result['meet_name'] == "Test Meet"
        assert result['course'] == "Y"


class TestAthlete:
    """Tests for Athlete dataclass."""

    def test_athlete_creation(self):
        """Test basic Athlete object creation."""
        athlete = Athlete(
            mm_id="12345",
            first_name="John",
            last_name="Doe",
            gender="M",
            team="ABC"
        )

        assert athlete.mm_id == "12345"
        assert athlete.first_name == "John"
        assert athlete.last_name == "Doe"
        assert athlete.gender == "M"
        assert athlete.team == "ABC"

    def test_athlete_optional_fields(self):
        """Test that optional fields work correctly."""
        athlete = Athlete(mm_id="123", team="XYZ")

        assert athlete.mm_id == "123"
        assert athlete.team == "XYZ"
        assert athlete.first_name is None
        assert athlete.usas_id is None

    def test_athlete_to_dict(self):
        """Test conversion to dictionary."""
        athlete = Athlete(
            mm_id="12345",
            first_name="Jane",
            last_name="Smith"
        )
        result = athlete.to_dict()

        assert isinstance(result, dict)
        assert result['mm_id'] == "12345"
        assert result['first_name'] == "Jane"
        assert result['last_name'] == "Smith"

    def test_athlete_repr(self):
        """Test string representation."""
        athlete = Athlete(mm_id="123", first_name="Test")
        repr_str = repr(athlete)

        assert "Athlete" in repr_str
        assert "123" in repr_str


class TestTeam:
    """Tests for Team dataclass."""

    def test_team_creation(self):
        """Test basic Team object creation."""
        team = Team(
            team_abbreviation="ABC",
            full_team_name="ABC Swimming Club",
            team_short_name="ABC SC"
        )

        assert team.team_abbreviation == "ABC"
        assert team.full_team_name == "ABC Swimming Club"
        assert team.team_short_name == "ABC SC"

    def test_team_optional_fields(self):
        """Test optional fields."""
        team = Team(team_abbreviation="XYZ")

        assert team.team_abbreviation == "XYZ"
        assert team.full_team_name is None
        assert team.team_lsc is None

    def test_team_to_dict(self):
        """Test conversion to dictionary."""
        team = Team(
            team_abbreviation="TEST",
            full_team_name="Test Team"
        )
        result = team.to_dict()

        assert isinstance(result, dict)
        assert result['team_abbreviation'] == "TEST"
        assert result['full_team_name'] == "Test Team"


class TestIndividualResult:
    """Tests for IndividualResult dataclass."""

    def test_individual_result_creation(self):
        """Test basic IndividualResult object creation."""
        result = IndividualResult(
            mm_athlete_id="12345",
            event_no="001",
            distance="50",
            stroke_code="A",
            time="25.50",
            overall_place="1"
        )

        assert result.mm_athlete_id == "12345"
        assert result.event_no == "001"
        assert result.distance == "50"
        assert result.stroke_code == "A"
        assert result.time == "25.50"
        assert result.overall_place == "1"

    def test_individual_result_default_flag(self):
        """Test that i_r_flag defaults to 'I'."""
        result = IndividualResult()

        assert result.i_r_flag == "I"

    def test_individual_result_all_fields(self):
        """Test creation with all fields."""
        result = IndividualResult(
            mm_athlete_id="12345",
            event_no="001",
            distance="100",
            stroke_code="B",
            seed_time="60.00",
            round="F",
            time="59.50",
            course="Y",
            heat="3",
            lane="4",
            heat_place="1",
            overall_place="2",
            points="18",
            time_code="OT",
            backup_time_1="59.51",
            backup_time_2="59.49",
            reaction_time="0.65"
        )

        assert result.mm_athlete_id == "12345"
        assert result.stroke_code == "B"
        assert result.seed_time == "60.00"
        assert result.reaction_time == "0.65"

    def test_individual_result_to_dict(self):
        """Test conversion to dictionary."""
        result = IndividualResult(
            mm_athlete_id="123",
            event_no="5",
            time="30.00"
        )
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict['mm_athlete_id'] == "123"
        assert result_dict['event_no'] == "5"
        assert result_dict['time'] == "30.00"


class TestRelayResult:
    """Tests for RelayResult dataclass."""

    def test_relay_result_creation(self):
        """Test basic RelayResult object creation."""
        result = RelayResult(
            team_abbr="ABC",
            relay_team="A",
            event_no="002",
            distance="200",
            stroke_code="E",
            time="100.50"
        )

        assert result.team_abbr == "ABC"
        assert result.relay_team == "A"
        assert result.event_no == "002"
        assert result.distance == "200"
        assert result.stroke_code == "E"
        assert result.time == "100.50"

    def test_relay_result_default_flag(self):
        """Test that i_r_flag defaults to 'R'."""
        result = RelayResult()

        assert result.i_r_flag == "R"

    def test_relay_result_with_athletes(self):
        """Test relay with athlete IDs."""
        result = RelayResult(
            team_abbr="XYZ",
            relay_athletes=["101", "102", "103", "104"]
        )

        assert len(result.relay_athletes) == 4
        assert result.relay_athletes[0] == "101"
        assert result.relay_athletes[3] == "104"

    def test_relay_result_with_reaction_times(self):
        """Test relay with reaction times."""
        result = RelayResult(
            team_abbr="ABC",
            reaction_times=["0.65", "0.71", "0.68", "0.73"]
        )

        assert len(result.reaction_times) == 4
        assert result.reaction_times[0] == "0.65"

    def test_relay_result_empty_lists_default(self):
        """Test that lists default to empty, not None."""
        result = RelayResult()

        assert result.relay_athletes == []
        assert result.reaction_times == []
        assert isinstance(result.relay_athletes, list)
        assert isinstance(result.reaction_times, list)

    def test_relay_result_to_dict(self):
        """Test conversion to dictionary."""
        result = RelayResult(
            team_abbr="TEST",
            relay_team="B",
            relay_athletes=["1", "2", "3", "4"]
        )
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict['team_abbr'] == "TEST"
        assert result_dict['relay_team'] == "B"
        assert len(result_dict['relay_athletes']) == 4

    def test_relay_result_partial_athletes(self):
        """Test relay with fewer than 4 athletes."""
        result = RelayResult(
            team_abbr="ABC",
            relay_athletes=["101", "102"]  # Only 2 athletes
        )

        assert len(result.relay_athletes) == 2
        # This is valid - not all relays must have exactly 4 swimmers


class TestObjectInteroperability:
    """Tests for how objects work together."""

    def test_objects_are_independent(self):
        """Test that object instances are independent."""
        athlete1 = Athlete(mm_id="123")
        athlete2 = Athlete(mm_id="456")

        assert athlete1.mm_id != athlete2.mm_id
        athlete1.first_name = "John"
        assert athlete2.first_name is None

    def test_result_references_athlete_by_id(self):
        """Test that results reference athletes by ID string."""
        athlete = Athlete(mm_id="12345", first_name="Test")
        result = IndividualResult(mm_athlete_id="12345")

        # They should share the same ID value
        assert result.mm_athlete_id == athlete.mm_id

    def test_relay_references_team_by_abbr(self):
        """Test that relays reference teams by abbreviation."""
        team = Team(team_abbreviation="ABC")
        relay = RelayResult(team_abbr="ABC")

        assert relay.team_abbr == team.team_abbreviation
