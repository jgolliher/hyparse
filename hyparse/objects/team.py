from typing import Dict, List, Tuple, Any, Optional


class Team:
    def __init__(
        self,
        team_abbreviation: Optional[str],
        full_team_name: Optional[str],
        team_short_name: Optional[str],
        team_lsc: Optional[str],
    ):
        """Initialize a Team object.

        Args:
            team_abbreviation (str, optional): Team abbreviation.
            full_team_name (str, optional): Full team name.
            team_short_name (str, optional): Team short name.
            team_lsc (str, optional): Team Local swimming Committee (LSC).
        """
        self.team_abbreviation = team_abbreviation
        self.full_team_name = full_team_name
        self.team_short_name = team_short_name
        self.team_lsc = team_lsc

    def __repr__(self):
        """Returns a string representation of the Team object.

        Returns:
            str: A string representation of the Team object.
        """
        return f"Team(name='{self.full_team_name}', abbrev='{self.team_abbreviation}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the Athlete object.

        Returns:
            Dict: A dictionary representation of the Athlete object.
        """
        return self.__dict__
