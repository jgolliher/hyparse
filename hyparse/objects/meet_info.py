from typing import Dict, List, Tuple, Any, Optional


class MeetInfo:
    def __init__(
        self,
        meet_name: Optional[str],
        facility_name: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
        elevation: Optional[str],
        result_type: Optional[str],
        mm_version: Optional[str],
        date_file_created: Optional[str],
    ):
        """Initialize a MeetInfo object.

        Args:
            meet_name: (str, optional): The name of the meet.
            facility_name: (str, optional): The name of the facility.
            start_date: (str, optional): The start date of the meet.
            end_date: (str, optional): The end date of the meet.
            elevation: (str, optional): The elevation of the meet.
            result_type: (str, optional): The type of results.
            mm_version: (str, optional): The version of MM used.
            date_file_created: (str, optional): The date the file was created.
        """
        self.meet_name = meet_name
        self.facility_name = facility_name
        self.start_date = start_date
        self.end_date = end_date
        self.elevation = elevation
        self.result_type = result_type
        self.mm_version = mm_version
        self.date_file_created = date_file_created

    def __repr__(self):
        """String representation of MeetInfo object."""
        return f"MeetInfo(name='{self.meet_name}', start_date='{self.start_date}', mm_version='{self.mm_version}')"
