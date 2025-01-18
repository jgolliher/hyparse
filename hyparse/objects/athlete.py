from typing import Dict, List, Tuple, Any, Optional


class Athlete:
    """Represents an athlete from a .hy3 file.

    An Athlete object stores information about an athlete, parsed from 'D1' lines
    in a .hy3 file.  These lines represent individual athlete entries. While the
    parser creates multiple Athlete objects during extraction, this class can also
    represent a single athlete.

    Attributes:
        gender (str, optional): The athlete's gender.
        mm_id (str, optional): The athlete's MeetManager ID.
        first_name (str, optional): The athlete's first name.
        nick_name (str, optional): The athlete's nickname.
        last_name (str, optional): The athlete's last name.
        usas_id (str, optional): The athlete's USA Swimming ID (or any other ID
            provided in Team Manager).
        team (str, optional): The athlete's team name.

    Example:
        >>> athlete = Athlete(
        ...     first_name='Erika',
        ...     last_name='Brown',
        ...     usas_id='1234567',
        ...     team='TENN'
        ... )
        >>> print(athlete.first_name)
        Erika
    """

    def __init__(
        self,
        gender: Optional[str] = None,
        mm_id: Optional[str] = None,
        first_name: Optional[str] = None,
        nick_name: Optional[str] = None,
        last_name: Optional[str] = None,
        usas_id: Optional[str] = None,
        team: Optional[str] = None,
    ):
        """Initializes an Athlete object.

        Args:
            gender (str, optional): The athlete's gender.
            mm_id (str, optional): The athlete's MeetManager ID.
            first_name (str, optional): The athlete's first name.
            nick_name (str, optional): The athlete's nickname.
            last_name (str, optional): The athlete's last name.
            usas_id (str, optional): The athlete's USA Swimming ID (or any other ID
                provided in Team Manager).
            team (str, optional): The athlete's team name.

        Example:
            >>> athlete = Athlete(
            ...     first_name='Meghan',
            ...     last_name='Small',
            ...     team='TENN'
            ... )
            >>> print(athlete)
            Athlete(name='Meghan Small', team='TENN')

        """
        self.gender = gender
        self.mm_id = mm_id
        self.first_name = first_name
        self.nick_name = nick_name
        self.last_name = last_name
        self.usas_id = usas_id
        self.team = team

    def __repr__(self):
        """Returns a string representation of the Athlete object.

        Returns:
            str: A string representation of the Athlete object, including the athlete's
                name and team.

        Example:
            >>> athlete = Athlete(first_name='Tess', last_name='Cieplucha', team='TENN')
            >>> print(repr(athlete))
            Athlete(name='Tess Cieplucha', team='TENN')
        """
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"Athlete(name='{name}', team='{self.team}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the Athlete object.

        Returns:
            dict: A dictionary containing the athlete's attributes.

        Example:
            >>> athlete = Athlete(first_name='Matthew', last_name='Garcia', team='TENN')
            >>> athlete_dict = athlete.to_dict()
            >>> print(athlete_dict['first_name'])
            Matthew
        """
        return self.__dict__
