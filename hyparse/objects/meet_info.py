from typing import Dict, List, Tuple, Any, Optional


class MeetInfo:
    """Meet information representation from .hy3 file.

    General meet information from a .hy3 file.

    Attributes:
        meet_name: (str, optional): The name of the meet.
        facility_name (str, optional): The name of the facility.
        meet_start_date (str, optional): The start date of the meet.
        meet_end_date (str, optional): The end date of the meet.
        elevation (str, optional): The elevation of the meet.
        result_type (str, optional): The type of results.
        mm_version (str, optional): The version of MM used.
        date_file_created (str, optional): The date the file was created.

    """

    def __init__(
        self,
        meet_name: Optional[str],
        facility_name: Optional[str],
        meet_start_date: Optional[str],
        meet_end_date: Optional[str],
        elevation: Optional[str],
        course: Optional[str],
        result_type: Optional[str],
        mm_version: Optional[str],
        date_file_created: Optional[str],
    ):
        """Initialize a MeetInfo object.

        Args:
            meet_name (str, optional): The name of the meet.
            facility_name (str, optional): The name of the facility.
            meet_start_date (str, optional): The start date of the meet.
            meet_end_date (str, optional): The end date of the meet.
            elevation: (str, optional): The elevation of the meet.
            course (str, optional): The course of the meet (L=LCM, S=SCM, Y=Yards)
            result_type (str, optional): The type of results.
            mm_version (str, optional): The version of MM used.
            date_file_created (str, optional): The date the file was created.
        """
        self.meet_name = meet_name
        self.facility_name = facility_name
        self.meet_start_date = meet_start_date
        self.meet_end_date = meet_end_date
        self.elevation = elevation
        self.course = course
        self.result_type = result_type
        self.mm_version = mm_version
        self.date_file_created = date_file_created

    def __repr__(self):
        """String representation of MeetInfo object."""
        return f"MeetInfo(name='{self.meet_name}', start_date='{self.meet_start_date}', mm_version='{self.mm_version}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the MeetInfo object.

        Returns:
            Dict: A dictionary representation of the Athlete object.
        """
        return self.__dict__
