from typing import Dict, List, Tuple, Any, Optional


class IndividualEntry:
    def __init__(
        self,
        line_id: Optional[str],
        mm_id: Optional[str],
        event_no: Optional[str],
        distance: Optional[str],
        stroke_code: Optional[str],
        seed_time: Optional[str],
    ):
        """Initialize an IndividualEntry object.

        Args:
            line_id (str, optional): LineID from .hy3 file.
            #TODO: Check this is correct..
            athlete_id (str, optional): AthleteID from Meet Manager
            event_no (str, optional): Event number.
            distance (str, optional): Event distance.
            stroke_code (str, optional): Event stroke code.
            seed_time (str, optional): Athlete's seed (entry) time.
        """
        self.line_id = line_id
        self.mm_id = mm_id
        self.event_no = event_no
        self.distance = distance
        self.stroke_code = stroke_code
        self.seed_time = seed_time

    def __repr__(self):
        return f"EventEntry(athlete_id='{self.athlete_id}', event_no='{self.event_no}', stroke_code='{self.stroke_code}')"
