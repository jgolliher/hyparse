from typing import Dict, List, Tuple, Any, Optional


class Team:
    """Represents a swim team.

    This class stores information about a swim team, including its
    abbreviation, full name, short name, and Local Swimming Committee (LSC).

    Attributes:
        team_abbreviation (str, optional): The team's abbreviated name.
        full_team_name (str, optional): The team's full official name.
        team_short_name (str, optional): A shorter version of the team's name.
        team_lsc (str, optional): The team's Local Swimming Committee (LSC).

    Example:
        >>> team = Team(
        ...     team_abbreviation='TENN',
        ...     full_team_name='University of Tennessee',
        ...     team_short_name='Tennessee',
        ...     team_lsc='SE'
        ... )
        >>> print(team.full_team_name)
        University of Tennessee
    """

    def __init__(
        self,
        team_abbreviation: Optional[str],
        full_team_name: Optional[str],
        team_short_name: Optional[str],
        team_lsc: Optional[str],
    ):
        """Initializes a Team object.

        Args:
            team_abbreviation (str, optional): The team's abbreviated name.
            full_team_name (str, optional): The team's full official name.
            team_short_name (str, optional): A shorter version of the team's name.
            team_lsc (str, optional): The team's Local Swimming Committee (LSC).


        Example:
            >>> team = Team(
            ...     team_abbreviation='TENN',
            ...     full_team_name='University of Tennessee',
            ...     team_lsc='SE'
            ... )
            >>> print(repr(team))
            Team(name='University of Tennessee', abbrev='TENN')
        """
        self.team_abbreviation = team_abbreviation
        self.full_team_name = full_team_name
        self.team_short_name = team_short_name
        self.team_lsc = team_lsc

    def __repr__(self):
        """Returns a string representation of the Team object.

        Returns:
            str: A string representation of the Team object, including the full team name and abbreviation.

        Example:
            >>> team = Team(full_team_name='University of Tennessee', team_abbreviation='TENN')
            >>> print(repr(team))
            Team(name='University of Tennessee', abbrev='TENN')
        """
        return f"Team(name='{self.full_team_name}', abbrev='{self.team_abbreviation}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the Team object.

        Returns:
            dict: A dictionary containing the team's attributes.

        Example:
            >>> team = Team(full_team_name='University of Tennessee', team_abbreviation='TENN')
            >>> team_dict = team.to_dict()
            >>> print(team_dict['full_team_name'])
            University of Tennessee
        """
        return self.__dict__
