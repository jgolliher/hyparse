"""Individual result data model using Pydantic."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class IndividualResult(BaseModel):
    """Represents an individual swimming result.

    Attributes:
        mm_athlete_id: The athlete's MeetManager ID.
        event_no: The event number.
        distance: The event distance (e.g., '50', '100', '200').
        stroke_code: The event stroke code ('A'=Free, 'B'=Back, 'C'=Breast, 'D'=Fly, 'E'=IM).
        seed_time: The athlete's seed time (in seconds as string).
        round: The round ('P'=Prelim, 'F'=Final, 'S'=Semi-final, 'T'=Time Trial).
        time: The result time (in seconds as string).
        course: The course type ('L'=LCM, 'S'=SCM, 'Y'=Yards).
        heat: The heat number.
        lane: The lane number.
        heat_place: Place within the heat.
        overall_place: Overall place in the event.
        points: Points scored.
        time_code: Time code (e.g., 'DQ'=Disqualified, 'NS'=No Show, 'SCR'=Scratch).
        backup_time_1: Backup time 1 (in seconds as string).
        backup_time_2: Backup time 2 (in seconds as string).
        reaction_time: Reaction time (in seconds as string).
        i_r_flag: Denotes if Individual ('I') or Relay ('R').
    """

    mm_athlete_id: Optional[str] = None
    event_no: Optional[str] = None
    distance: Optional[str] = None
    stroke_code: Optional[Literal["A", "B", "C", "D", "E"]] = None
    seed_time: Optional[str] = None
    round: Optional[Literal["P", "F", "S", "T"]] = None
    time: Optional[str] = None
    course: Optional[Literal["L", "S", "Y"]] = None
    heat: Optional[str] = None
    lane: Optional[str] = None
    heat_place: Optional[str] = None
    overall_place: Optional[str] = None
    points: Optional[str] = None
    time_code: Optional[str] = None
    backup_time_1: Optional[str] = None
    backup_time_2: Optional[str] = None
    reaction_time: Optional[str] = None
    i_r_flag: str = "I"

    @field_validator("stroke_code", "round", "course", mode='before')
    @classmethod
    def uppercase_codes(cls, v):
        """Convert codes to uppercase and handle empty strings."""
        if isinstance(v, str):
            v = v.strip().upper()
            # Convert empty string to None for Optional fields
            return v if v else None
        return v

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the IndividualResult object.

        Returns:
            dict: A dictionary containing the object's attributes.
        """
        return self.model_dump()

    def __repr__(self):
        """Returns a concise string representation of the IndividualResult object."""
        return (
            f"IndividualResult(athlete_id='{self.mm_athlete_id}', "
            f"round='{self.round}', event_no='{self.event_no}', "
            f"stroke_code='{self.stroke_code}', time='{self.time}')"
        )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
