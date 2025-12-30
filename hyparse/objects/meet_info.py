"""Meet information data model using Pydantic."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class MeetInfo(BaseModel):
    """Represents general meet information from a .hy3 file.

    Attributes:
        meet_name: The name of the meet.
        facility_name: The name of the facility where the meet is held.
        meet_start_date: The start date of the meet (YYYYMMDD format).
        meet_end_date: The end date of the meet (YYYYMMDD format).
        elevation: The elevation of the meet location.
        course: The course type ('L'=Long Course Meters, 'S'=Short Course Meters, 'Y'=Yards).
        result_type: The type of results.
        mm_version: The version of MeetManager used.
        date_file_created: The date the .hy3 file was created (YYYYMMDD format).
    """

    meet_name: Optional[str] = None
    facility_name: Optional[str] = None
    meet_start_date: Optional[str] = None
    meet_end_date: Optional[str] = None
    elevation: Optional[str] = None
    course: Optional[Literal["L", "S", "Y"]] = None
    result_type: Optional[str] = None
    mm_version: Optional[str] = None
    date_file_created: Optional[str] = None

    @field_validator("course", mode='before')
    @classmethod
    def validate_course(cls, v):
        """Validate and normalize course type."""
        if isinstance(v, str):
            v = v.strip().upper()
            # Convert empty string to None for Optional field
            return v if v else None
        return v

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the MeetInfo object.

        Returns:
            dict: A dictionary containing the object's attributes.
        """
        return self.model_dump()

    def __repr__(self):
        """Returns a concise string representation of the MeetInfo object."""
        return (
            f"MeetInfo(name='{self.meet_name}', "
            f"start_date='{self.meet_start_date}', "
            f"mm_version='{self.mm_version}')"
        )

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace from strings
        validate_assignment=True,  # Validate on assignment
    )
