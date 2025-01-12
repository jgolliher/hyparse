from typing import Dict, List, Tuple, Any, Optional


class Athlete:
    """Athlete representation from .hy3 file.

    An Athlete object represents an athlete in a .hy3 file. The information comes from
    the `D1` lines in a .hy3 file, which represent athlete entries.The parser from this
    package creates multiple Athlete objects when extracting information, but this class
    can represent an individual athlete if needed.

    An Athlete object contains the following attributes:

    Attributes:
        gender: Athlete gender.
        mm_id: Athlete's MeetManager ID.
        first_name: Athlete first name.
        nick_name: Athlete nick name.
        last_name: Athlete last name.
        usas_id: Athlete's (assumed) USA Swimming ID.
        team: Athlete's team.
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
            gender (str, optional): Athlete gender.
            mm_id (str, optional): Athlete's MeetManager ID.
            first_name (str, optional): Athlete first name.
            nick_name (str, optional): Athlete nick name.
            last_name (str, optional): Athlete last name.
            usas_id (str, optional): Athlete's (assumed) USA Swimming ID. Can technically
                be any ID provided in Team Manager, but is usually the USA Swimming ID.
            team (str, optional): Athlete's team.
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
            str: A string representation of the Athlete object.
        """
        return f"Athlete(name='{self.first_name} {self.last_name}', team='{self.team}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the Athlete object.

        Returns:
            Dict: A dictionary representation of the Athlete object.
        """
        return self.__dict__
