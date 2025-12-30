"""Athlete data model using Pydantic."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Athlete(BaseModel):
    """Represents an athlete from a .hy3 file.

    Attributes:
        mm_id: The athlete's MeetManager ID (required for matching with results).
        team: The athlete's team abbreviation.
        gender: The athlete's gender ('M', 'F', or 'X' for mixed).
        first_name: The athlete's first name.
        last_name: The athlete's last name.
        nick_name: The athlete's nickname.
        usas_id: The athlete's USA Swimming ID or other governing body ID.
    """

    mm_id: Optional[str] = Field(None, max_length=10)
    team: Optional[str] = Field(None, max_length=10)
    gender: Optional[Literal["M", "F", "X"]] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    nick_name: Optional[str] = Field(None, max_length=50)
    usas_id: Optional[str] = Field(None, max_length=20)  # Usually 14 chars but can vary

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        """Validate and normalize gender."""
        if v and isinstance(v, str):
            v = v.strip().upper()
            if v in ["M", "F", "X"]:
                return v
        return v

    @field_validator("mm_id", "team")
    @classmethod
    def strip_ids(cls, v):
        """Strip whitespace from IDs."""
        if v and isinstance(v, str):
            return v.strip()
        return v

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the Athlete object.

        Returns:
            dict: A dictionary containing the athlete's attributes.
        """
        return self.model_dump()

    def __repr__(self):
        """Returns a concise string representation of the Athlete object."""
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"Athlete(name='{name}', team='{self.team}', mm_id='{self.mm_id}')"

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
