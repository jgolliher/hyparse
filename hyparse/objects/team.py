"""Team data model using Pydantic."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Team(BaseModel):
    """Represents a swim team.

    Attributes:
        team_abbreviation: The team's abbreviated name (typically 3-5 characters).
        full_team_name: The team's full official name.
        team_short_name: A shorter version of the team's name.
        team_lsc: The team's Local Swimming Committee (LSC) code.
    """

    team_abbreviation: Optional[str] = Field(None, max_length=10)
    full_team_name: Optional[str] = Field(None, max_length=100)
    team_short_name: Optional[str] = Field(None, max_length=50)
    team_lsc: Optional[str] = Field(None, max_length=5)

    @field_validator("team_abbreviation", "team_lsc")
    @classmethod
    def uppercase_codes(cls, v):
        """Convert team codes to uppercase."""
        if v and isinstance(v, str):
            return v.strip().upper()
        return v

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the Team object.

        Returns:
            dict: A dictionary containing the team's attributes.
        """
        return self.model_dump()

    def __repr__(self):
        """Returns a concise string representation of the Team object."""
        return f"Team(name='{self.full_team_name}', abbrev='{self.team_abbreviation}')"

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
