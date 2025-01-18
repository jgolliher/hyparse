from typing import Dict, List, Tuple, Any, Optional


class IndividualResult:
    """Represents an individual swimming result.

    Stores information about an individual result from a .hy3 file, parsed
    from 'E1' (event entry) and 'E2' (event result) lines.

    Attributes:
        mm_athlete_id (str, optional): The athlete's MeetManager ID.
        event_no (str, optional): The event number.
        distance (str, optional): The event distance.
        stroke_code (str, optional): The event stroke code.
        seed_time (str, optional): The athlete's seed time.
        round (str, optional): The round of the result (e.g., 'P' for prelims, 'F' for finals).
        time (str, optional): The result time (in seconds).
        course (str, optional): The course type (e.g., 'L' for long course meters, 'S' for short course meters, 'Y' for yards).
        heat (str, optional): The heat number.
        lane (str, optional): The lane number.
        heat_place (str, optional): The athlete's place within the heat.
        overall_place (str, optional): The athlete's overall place in the event.
        backup_time_1 (str, optional): Backup time 1.
        backup_time_2 (str, optional): Backup time 2.
        reaction_time (str, optional): The athlete's reaction time.

    Example:
        >>> result = IndividualResult(
        ...     mm_athlete_id='12345',
        ...     event_no='9',
        ...     distance='200',
        ...     stroke_code='E',
        ...     seed_time='113.01',
        ...     round='F',
        ...     time='111.62',
        ...     course='Y',
        ...     heat='3',
        ...     lane='4',
        ...     heat_place='1',
        ...     overall_place='1'
        ... )
        >>> print(result.time)
        111.62
    """

    def __init__(
        self,
        mm_athlete_id: Optional[str],
        event_no: Optional[str],
        distance: Optional[str],
        stroke_code: Optional[str],
        seed_time: Optional[str],
        round: Optional[str],
        time: Optional[str],
        course: Optional[str],
        heat: Optional[str],
        lane: Optional[str],
        heat_place: Optional[str],
        overall_place: Optional[str],
        backup_time_1: Optional[str],
        backup_time_2: Optional[str],
        reaction_time: Optional[str],
    ):
        """Initializes an IndividualResult object.

        Args:
            mm_athlete_id (str, optional): The athlete's MeetManager ID.
            event_no (str, optional): The event number.
            distance (str, optional): The event distance.
            stroke_code (str, optional): The event stroke code.
            seed_time (str, optional): The athlete's seed time.
            round (str, optional): The round of the result (e.g., 'P' for prelims, 'F' for finals, 'S' for semifinals).
            time (str, optional): The result time (in seconds).
            course (str, optional): The course type (e.g., 'L' for long course meters, 'S' for short course meters, 'Y' for yards).
            heat (str, optional): The heat number.
            lane (str, optional): The lane number.
            heat_place (str, optional): The athlete's place within the heat.
            overall_place (str, optional): The athlete's overall place in the event.
            backup_time_1 (str, optional): Backup time 1.
            backup_time_2 (str, optional): Backup time 2.
            reaction_time (str, optional): The athlete's reaction time.

        Example:
            >>> result = IndividualResult(
            ...     mm_athlete_id='12345',
            ...     event_no='1',
            ...     distance='50',
            ...     stroke_code='A',
            ...     time='20.03'
            ... )
            >>> print(repr(result))
            Result(athlete_id='12345', round='None',event_no='1', stroke_code='A')

        """
        self.mm_athlete_id = mm_athlete_id
        self.event_no = event_no
        self.distance = distance
        self.stroke_code = stroke_code
        self.seed_time = seed_time
        self.round = round
        self.time = time
        self.course = course
        self.heat = heat
        self.lane = lane
        self.heat_place = heat_place
        self.overall_place = overall_place
        self.backup_time_1 = backup_time_1
        self.backup_time_2 = backup_time_2
        self.reaction_time = reaction_time

    def __repr__(self):
        """Returns a string representation of the IndividualResult object.

        Returns:
            str: A string representation of the object.

        Example:
            >>> result = IndividualResult(mm_athlete_id='12345', event_no='1', stroke_code='A')
            >>> print(repr(result))
            Result(athlete_id='12345', round='None',event_no='1', stroke_code='A')

        """
        return f"Result(athlete_id='{self.mm_athlete_id}', round='{self.round}',event_no='{self.event_no}', stroke_code='{self.stroke_code}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the IndividualResult object.

        Returns:
            dict: A dictionary containing the object's attributes.

        Example:
            >>> result = IndividualResult(mm_athlete_id='12345', time='54.50')
            >>> result_dict = result.to_dict()
            >>> print(result_dict['time'])
            54.50
        """
        return self.__dict__
