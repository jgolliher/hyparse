from typing import Dict, List, Tuple, Any, Optional


class RelayResult:
    """Represents the results of a relay race.

    Stores information about a relay result parsed from 'F1', 'F2', and 'F3' lines
    in a .hy3 file.

    Attributes:
        team_abbr (str, optional): The relay team's abbreviation.
        relay_team (str, optional): Relay team designation (e.g., 'A', 'B', etc.).
        gender (str, optional): The gender of the relay team (e.g., 'M', 'F', 'X').
        event_no (str, optional): The event number.
        distance (str, optional): The relay distance.
        stroke_code (str, optional): The stroke code for the relay.
        round (str, optional): The round of the result (e.g., 'F', 'P', 'S').
        seed_time (str, optional): The relay team's seed time.
        time (str, optional): The final time for the relay.
        time_code (str, optional): Any time code associated with the result (e.g., 'DQ', 'NS').
        course (str, optional): The course type (e.g., 'L', 'S', 'Y').
        heat (str, optional): The heat number.
        lane (str, optional): The lane number.
        heat_place (str, optional): The relay's place within the heat.
        overall_place (str, optional): The relay's overall place in the event.
        backup_time_1 (str, optional): A backup recorded time.
        backup_time_2 (str, optional): A second backup recorded time.
        backup_time_3 (str, optional): A third backup recorded time.
        touchpad_time (str, optional): The time recorded by the touchpad.
        relay_athletes (List[str], optional): A list of athlete IDs participating in the relay.
        reaction_times (List[str], optional): A list of reaction times for each leg of the relay.

    Example:
        >>> relay_result = RelayResult(
        ...     team_abbr='TENN',
        ...     relay_team='A',
        ...     gender='M',
        ...     event_no='42',
        ...     distance='400',
        ...     stroke_code='A',
        ...     time='164.13',
        ...     relay_athletes=['123', '456', '789', '012'],
        ...     reaction_times=['0.25', '0.28', '0.22', '0.24']
        ... )
        >>> print(relay_result.time)
        164.13
    """

    def __init__(
        self,
        team_abbr: Optional[str] = None,
        relay_team: Optional[str] = None,
        gender: Optional[str] = None,
        event_no: Optional[str] = None,
        distance: Optional[str] = None,
        stroke_code: Optional[str] = None,
        round: Optional[str] = None,
        seed_time: Optional[str] = None,
        time: Optional[str] = None,
        time_code: Optional[str] = None,
        course: Optional[str] = None,
        heat: Optional[str] = None,
        lane: Optional[str] = None,
        heat_place: Optional[str] = None,
        overall_place: Optional[str] = None,
        backup_time_1: Optional[str] = None,
        backup_time_2: Optional[str] = None,
        backup_time_3: Optional[str] = None,
        touchpad_time: Optional[str] = None,
        relay_athletes: Optional[List] = None,
        reaction_times: Optional[List] = None,
    ):
        """Initializes a RelayResult object.

        Args:
            team_abbr (str, optional): The relay team's abbreviation.
            relay_team (str, optional): Relay team designation (e.g., 'A', 'B', etc.).
            gender (str, optional): The gender of the relay team.
            event_no (str, optional): The event number.
            distance (str, optional): The relay distance.
            stroke_code (str, optional): The stroke code for the relay.
            round (str, optional): The round of the result.
            seed_time (str, optional): The relay team's seed time.
            time (str, optional): The final time for the relay.
            time_code (str, optional): Any time code associated with the result.
            course (str, optional): The course type.
            heat (str, optional): The heat number.
            lane (str, optional): The lane number.
            heat_place (str, optional): The relay's place within the heat.
            overall_place (str, optional): The relay's overall place in the event.
            backup_time_1 (str, optional): A backup recorded time.
            backup_time_2 (str, optional): A second backup recorded time.
            backup_time_3 (str, optional): A third backup recorded time.
            touchpad_time (str, optional): The time recorded by the touchpad.
            relay_athletes (List[str], optional): A list of athlete IDs participating in the relay.
            reaction_times (List[str], optional): A list of reaction times for each leg of the relay.

        Example:
            >>> relay_result = RelayResult(team_abbr='TENN', event_no='2', distance='200', stroke_code='B')
            >>> print(repr(relay_result))
            RelayResult(team='TENN', relay='None',distance='200', stroke_code='B')
        """
        self.team_abbr = team_abbr
        self.relay_team = relay_team
        self.gender = gender
        self.event_no = event_no
        self.distance = distance
        self.stroke_code = stroke_code
        self.round = round
        self.seed_time = seed_time
        self.time = time
        self.time_code = time_code
        self.course = course
        self.heat = heat
        self.lane = lane
        self.heat_place = heat_place
        self.overall_place = overall_place
        self.backup_time_1 = backup_time_1
        self.backup_time_2 = backup_time_2
        self.backup_time_3 = backup_time_3
        self.touchpad_time = touchpad_time
        self.relay_athletes = relay_athletes
        self.reaction_times = reaction_times

    def __repr__(self):
        """Returns a string representation of the RelayResult object.

        Returns:
            str: A string representation of the object.

        Example:
            >>> relay_result = RelayResult(team_abbr='TENN', relay_team='B', distance='100', stroke_code='C')
            >>> print(repr(relay_result))
            RelayResult(team='TEN', relay='B',distance='100', stroke_code='C')
        """
        return f"RelayResult(team='{self.team_abbr}', relay='{self.relay_team}',distance='{self.distance}', stroke_code='{self.stroke_code}')"

    def to_dict(self):
        """Returns a dictionary representation of the RelayResult object.

        Returns:
            dict: A dictionary containing the object's attributes.

        Example:
            >>> relay_result = RelayResult(team_abbr='TENN', time='150.75')
            >>> relay_result_dict = relay_result.to_dict()
            >>> print(relay_result_dict['time'])
            150.75
        """
        return self.__dict__
