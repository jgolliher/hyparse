# No changes needed if using dataclasses, imports remain the same
from .meet_info import MeetInfo
from .athlete import Athlete
from .individual_result import IndividualResult
from .relay_result import RelayResult
from .team import Team

__all__ = ["MeetInfo", "Athlete", "Team", "IndividualResult", "RelayResult"]
