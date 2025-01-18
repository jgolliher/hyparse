from typing import Dict, List, Tuple, Any, Optional


class MeetInfo:
    """Represents general meet information from a .hy3 file.

    Attributes:
        meet_name (str, optional): The name of the meet.
        facility_name (str, optional): The name of the facility where the meet is held.
        meet_start_date (str, optional): The start date of the meet.
        meet_end_date (str, optional): The end date of the meet.
        elevation (str, optional): The elevation of the meet location.
        course (str, optional): The course type for the meet (e.g., 'L' for long course meters, 'S' for short course meters, 'Y' for yards).
        result_type (str, optional): The type of results.
        mm_version (str, optional): The version of MeetManager used to create the .hy3 file.
        date_file_created (str, optional): The date the .hy3 file was created.

    Example:
        >>> meet_info = MeetInfo(
        ...     meet_name='2020 SEC Swimming & Diving Championships',
        ...     facility_name='James E. Martin Aquatics Center',
        ...     meet_start_date='2020-02-18',
        ...     meet_end_date='2020-02-23',
        ...     course='Y',
        ...     mm_version = '7.0',
        ...     date_file_created='2020-02-23'
        ... )
        >>> print(meet_info.meet_name)
        2020 SEC Swimming & Diving Championships

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
        """Initializes a MeetInfo object.

        Args:
            meet_name (str, optional): The name of the meet.
            facility_name (str, optional): The name of the facility where the meet is held.
            meet_start_date (str, optional): The start date of the meet.
            meet_end_date (str, optional): The end date of the meet.
            elevation (str, optional): The elevation of the meet location.
            course (str, optional): The course type for the meet (e.g., 'L' for long course meters, 'S' for short course meters, 'Y' for yards).
            result_type (str, optional): The type of results.
            mm_version (str, optional): The version of MeetManager used to create the .hy3 file.
            date_file_created (str, optional): The date the .hy3 file was created.

        Example:
            >>> meet_info = MeetInfo(
            ...     meet_name='2024 Tennessee Invitational',
            ...     meet_start_date='2024-11-19',
            ...     meet_end_date='2024-11-22',
            ...     mm_version='8.0'
            ... )
            >>> print(repr(meet_info))
            MeetInfo(name='2024 Tennessee Invitational', start_date='2024-11-19', mm_version='8.0')
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
        """Returns a string representation of the MeetInfo object.

        Returns:
            str: A string representation of the object.

        Example:
            >>> meet_info = MeetInfo(meet_name='2024 Tennessee Invitational', meet_start_date='2024-11-19', mm_version='8.0')
            >>> print(repr(meet_info))
            MeetInfo(name='2024 Tennessee Invitational', start_date='2024-11-19', mm_version='8.0')
        """
        return f"MeetInfo(name='{self.meet_name}', start_date='{self.meet_start_date}', mm_version='{self.mm_version}')"

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the MeetInfo object.

        Returns:
            dict: A dictionary containing the object's attributes.

        Example:
            >>> meet_info = MeetInfo(meet_name='2024 Tennessee Invitational', meet_start_date='2024-11-19')
            >>> meet_info_dict = meet_info.to_dict()
            >>> print(meet_info_dict['meet_name'])
            2024 Tennessee Invitational
        """
        return self.__dict__
