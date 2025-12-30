"""HY-TEK .hy3 file format line specifications.

This module defines the field positions for each line type in the HY-TEK .hy3
file format. Each line type has specific fields at fixed character positions.

Line Types:
-----------
A1: File header - Meet management version and file creation info
B1: Meet information - Meet name, facility, dates
B2: Additional meet info - Course type
C1: Team information - Team codes and names
D1: Athlete/Swimmer information - Personal details and IDs
E1: Individual event entry - Event details and seed time
E2: Individual event result - Final time and placing
F1: Relay event entry - Team relay details and seed time
F2: Relay event result - Final time and placing
F3: Relay swimmers - Individual swimmers on relay team

Field Format:
------------
Each field specification is a tuple of (start_index, end_index) where:
- Indices are 0-based
- end_index is exclusive (Python slice notation)
- Fields are extracted using: line[start:end].strip()
"""

from typing import Dict, Tuple

# Type alias for field specifications
FieldSpec = Dict[str, Tuple[int, int]]

# Stroke code mappings
STROKE_CODES = {
    "A": "Free",
    "B": "Back",
    "C": "Breast",
    "D": "Fly",
    "E": "Medley",
    "F": "1m",  # Diving
    "G": "3m",  # Diving
    "H": "10m",  # Diving
}

# Course type codes
COURSE_CODES = {
    "Y": "SCY (Short Course Yards)",
    "S": "SCM (Short Course Meters)",
    "L": "LCM (Long Course Meters)",
}

# Round type codes
ROUND_CODES = {
    "P": "Prelims",
    "F": "Finals",
    "S": "Semifinals",
    "T": "Time Trials",
}


# Line specifications for each line type
LINE_SPECS: Dict[str, FieldSpec] = {
    "A1": {
        # File Header
        # Example: "A102                                            MM 8.0     20251201  88"
        "line_id": (0, 2),  # Always "A1"
        "result_type": (2, 4),  # "02" for meet results
        "mm_version": (44, 58),  # Meet Manager version (e.g., "MM 8.0")
        "date_file_created": (58, 68),  # YYYYMMDD format
    },
    "B1": {
        # Meet Information (Line 1)
        # Example: "B1Test Meet                     Pool Name                                      202501012025010100..."
        "line_id": (0, 2),  # Always "B1"
        "meet_name": (2, 47),  # Meet name (45 chars)
        "facility_name": (47, 92),  # Facility/pool name (45 chars)
        "meet_start_date": (92, 100),  # YYYYMMDD format
        "meet_end_date": (100, 108),  # YYYYMMDD format
        "elevation": (116, 121),  # Pool elevation (feet)
    },
    "B2": {
        # Meet Information (Line 2)
        # Example: "B2                                                                                L    ..."
        "line_id": (0, 2),  # Always "B2"
        "course": (98, 99),  # L=LCM, S=SCM, Y=SCY
    },
    "C1": {
        # Team Information
        # Example: "C1ABC  ABC Swimming Club       ABC SC            CA99"
        "line_id": (0, 2),  # Always "C1"
        "team_abbreviation": (2, 7),  # Team code (5 chars)
        "full_team_name": (7, 37),  # Full team name (30 chars)
        "team_short_name": (37, 53),  # Short team name (16 chars)
        "team_lsc": (53, 55),  # LSC code (2 chars, e.g., "CA", "NC")
    },
    "D1": {
        # Athlete/Swimmer Information
        # Example: "D1M12345Doe                 John                Nick                1234567890123499"
        "line_id": (0, 2),  # Always "D1"
        "gender": (2, 3),  # M=Male, F=Female, X=Other
        "mm_id": (3, 8),  # Meet Manager athlete ID (5 chars)
        "last_name": (8, 28),  # Last name (20 chars)
        "first_name": (28, 48),  # First name (20 chars)
        "nick_name": (48, 68),  # Nickname/preferred name (20 chars)
        "usas_id": (69, 85),  # USA Swimming ID (14-16 chars, but can vary)
    },
    "E1": {
        # Individual Event Entry
        # Example: "E1 12345       50     A                  001  50.0000                      00"
        "line_id": (0, 2),  # Always "E1"
        "mm_athlete_id": (3, 8),  # Athlete ID reference (matches D1 mm_id)
        "distance": (15, 21),  # Event distance (e.g., "50", "100", "200")
        "stroke_code": (21, 22),  # A=Free, B=Back, C=Breast, D=Fly, E=Medley
        "event_no": (38, 42),  # Event number in meet
        "seed_time": (42, 50),  # Seed time in seconds (8 chars, decimal)
        "points": (61, 68),  # Points (often empty here, populated in E2)
    },
    "E2": {
        # Individual Event Result
        # Example: "E2F  48.5000 YOT              1   4  1   1  18  48.5100  48.490000        ..."
        "line_id": (0, 2),  # Always "E2"
        "round": (2, 3),  # P=Prelims, F=Finals, S=Semis, T=Time Trial
        "time": (3, 11),  # Final time in seconds (8 chars, decimal)
        "course": (11, 12),  # L=LCM, S=SCM, Y=SCY
        "time_code": (12, 15),  # YOT, NT, DQ, NS, SCR, etc.
        "heat": (20, 24),  # Heat number (4 chars)
        "lane": (25, 27),  # Lane number (2 chars)
        "heat_place": (26, 29),  # Place in heat (3 chars, overlaps with lane)
        "overall_place": (29, 33),  # Overall place in event (4 chars)
        "points": (33, 36),  # Points scored (3 chars)
        "backup_time_1": (36, 44),  # Backup time 1 (8 chars)
        "backup_time_2": (45, 52),  # Backup time 2 (7 chars)
        "reaction_time": (83, 87),  # Reaction time off blocks (4 chars)
    },
    "F1": {
        # Relay Event Entry
        # Example: "F1ABC  A   M    200   E                  001  1:45.0000                  00"
        "line_id": (0, 2),  # Always "F1"
        "team_abbr": (2, 7),  # Team abbreviation (5 chars, matches C1)
        "relay_team": (7, 8),  # Relay team letter (A, B, C, etc.)
        "gender": (12, 13),  # M=Male, F=Female, X=Mixed
        "distance": (17, 21),  # Relay distance (e.g., "200", "400", "800")
        "stroke_code": (21, 22),  # A=Free relay, E=Medley relay
        "event_no": (38, 42),  # Event number in meet
        "seed_time": (43, 50),  # Seed time in seconds (7 chars, decimal)
        "points": (61, 68),  # Points (often empty here, populated in F2)
    },
    "F2": {
        # Relay Event Result
        # Example: "F2F  1:45.00 YOT              1   4  1   1  18  1:45.10  1:45.08  1:45.12..."
        "line_id": (0, 2),  # Always "F2"
        "round": (2, 3),  # P=Prelims, F=Finals, S=Semis, T=Time Trial
        "time": (3, 11),  # Final time in seconds (8 chars)
        "course": (11, 12),  # L=LCM, S=SCM, Y=SCY
        "time_code": (12, 15),  # YOT, NT, DQ, NS, SCR, etc.
        "heat": (20, 24),  # Heat number (4 chars)
        "lane": (25, 27),  # Lane number (2 chars)
        "heat_place": (26, 29),  # Place in heat (3 chars, overlaps with lane)
        "overall_place": (29, 33),  # Overall place in event (4 chars)
        "points": (33, 36),  # Points scored (3 chars)
        "backup_time_1": (36, 44),  # Backup time 1 (8 chars)
        "backup_time_2": (44, 52),  # Backup time 2 (8 chars)
        "backup_time_3": (52, 60),  # Backup time 3 (8 chars)
        "touchpad_time": (65, 73),  # Primary touchpad time (8 chars)
        "reaction_time_1": (83, 87),  # Reaction time for swimmer 1 (4 chars)
        "reaction_time_2": (87, 92),  # Reaction time for swimmer 2 (5 chars)
        "reaction_time_3": (92, 97),  # Reaction time for swimmer 3 (5 chars)
        "reaction_time_4": (97, 102),  # Reaction time for swimmer 4 (5 chars)
    },
    "F3": {
        # Relay Swimmers
        # Example: "F3 12345        23456        34567        45678"
        "line_id": (0, 2),  # Always "F3"
        "athlete_1_mm_id": (3, 8),  # First swimmer MM ID (5 chars)
        "athlete_2_mm_id": (16, 21),  # Second swimmer MM ID (5 chars)
        "athlete_3_mm_id": (29, 34),  # Third swimmer MM ID (5 chars)
        "athlete_4_mm_id": (42, 47),  # Fourth swimmer MM ID (5 chars)
    },
    # Additional line types could be added here:
    # G1, G2: Split times (if needed in future)
    # Z0: End of file marker (if needed)
}


def get_line_spec(line_id: str) -> FieldSpec:
    """Get the field specification for a given line ID.

    Args:
        line_id: Two-character line identifier (e.g., "A1", "B1", "E2")

    Returns:
        Dictionary mapping field names to (start, end) position tuples.

    Raises:
        KeyError: If line_id is not found in LINE_SPECS.
    """
    return LINE_SPECS[line_id]


def get_supported_line_types() -> list[str]:
    """Get list of all supported line types.

    Returns:
        List of line type identifiers (e.g., ["A1", "B1", "B2", ...])
    """
    return list(LINE_SPECS.keys())


def is_line_type_supported(line_id: str) -> bool:
    """Check if a line type is supported.

    Args:
        line_id: Two-character line identifier to check.

    Returns:
        True if line type is supported, False otherwise.
    """
    return line_id in LINE_SPECS
