"""Relay result data model using Pydantic."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RelayResult(BaseModel):
    """Represents the results of a relay race.

    Attributes:
        team_abbr: The relay team's abbreviation.
        relay_team: Relay team designation ('A', 'B', 'C', etc.).
        gender: Gender ('M'=Male, 'F'=Female, 'X'=Mixed).
        event_no: Event number.
        distance: Relay distance (e.g., '200', '400', '800').
        stroke_code: Stroke code ('A'=Free, 'E'=Medley).
        round: Round ('P'=Prelim, 'F'=Final, 'S'=Semi-final, 'T'=Time Trial).
        seed_time: Seed time (in seconds as string).
        time: Final time (in seconds as string).
        time_code: Time code (e.g., 'DQ', 'NS', 'SCR').
        course: Course type ('L'=LCM, 'S'=SCM, 'Y'=Yards).
        heat: Heat number.
        lane: Lane number.
        heat_place: Place within the heat.
        overall_place: Overall place in the event.
        points: Points scored.
        backup_time_1: Backup time 1 (in seconds as string).
        backup_time_2: Backup time 2 (in seconds as string).
        backup_time_3: Backup time 3 (in seconds as string).
        touchpad_time: Touchpad time (in seconds as string).
        relay_athletes: List of athlete MM IDs (typically 4 for standard relays).
        reaction_times: List of reaction times for each swimmer.
        i_r_flag: Denotes if Individual ('I') or Relay ('R').
    """

    team_abbr: Optional[str] = None
    relay_team: Optional[str] = None
    gender: Optional[Literal["M", "F", "X"]] = None
    event_no: Optional[str] = None
    distance: Optional[str] = None
    stroke_code: Optional[Literal["A", "E"]] = None  # Relays are typically Free or Medley
    round: Optional[Literal["P", "F", "S", "T"]] = None
    seed_time: Optional[str] = None
    time: Optional[str] = None
    time_code: Optional[str] = None
    course: Optional[Literal["L", "S", "Y"]] = None
    heat: Optional[str] = None
    lane: Optional[str] = None
    heat_place: Optional[str] = None
    overall_place: Optional[str] = None
    points: Optional[str] = None
    backup_time_1: Optional[str] = None
    backup_time_2: Optional[str] = None
    backup_time_3: Optional[str] = None
    touchpad_time: Optional[str] = None
    relay_athletes: List[Optional[str]] = Field(default_factory=list)
    reaction_times: List[Optional[str]] = Field(default_factory=list)
    i_r_flag: str = "R"

    @field_validator("stroke_code", "round", "course", "gender")
    @classmethod
    def uppercase_codes(cls, v):
        """Convert codes to uppercase and handle empty strings."""
        if v and isinstance(v, str):
            v = v.strip().upper()
            # Convert empty string to None for Optional fields
            return v if v else None
        return v

    @field_validator("relay_team")
    @classmethod
    def uppercase_relay_team(cls, v):
        """Convert relay team to uppercase and handle empty strings."""
        if v and isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the RelayResult object.

        Returns:
            dict: A dictionary containing the object's attributes.
        """
        return self.model_dump()

    def __repr__(self):
        """Returns a concise string representation of the RelayResult object."""
        return (
            f"RelayResult(team='{self.team_abbr}', relay='{self.relay_team}', "
            f"distance='{self.distance}', stroke_code='{self.stroke_code}', "
            f"time='{self.time}')"
        )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
