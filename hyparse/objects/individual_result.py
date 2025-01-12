from typing import Dict, List, Tuple, Any, Optional


class IndividualResult:
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
            mm_athlete_id (str, optional): Athlete ID from Meet Manager.
            event_no (str, optional): Event number.
            distance (str, optional): Event distance.
            stroke_code (str, optional): Event stroke code.
            seed_time (str, optional): Athlete's seed (entry) time.
            round (str, optional): Result round (P=Prelim, F=Final) #TODO: Semis?
            time (str, optional): Result time (in seconds)
            course (str, optional): Result course (L=LCM, S=SCM, Y=Yards)
            heat (str, optional): Result heat.
            lane (str, optional): Result lane.
            heat_place (str, optional): Result heat place.
            overall_place (str, optional): Result overall place.
            backup_time_1 (str, optional): Result backup time 1.
            backup_time_2 (str, optional): Result backup time 2.
            reaction_time (str, optional): Result reaction time.
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
            str: A string representation of the IndividualResult object.
        """
        return f"Result(athlete_id='{self.mm_athlete_id}', round='{self.round}',event_no='{self.event_no}', stroke_code='{self.stroke_code}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the Athlete object.

        Returns:
            Dict: A dictionary representation of the Athlete object.
        """
        return self.__dict__
