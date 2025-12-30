import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
from pydantic import ValidationError

# Assuming objects are now in hyparse.objects
from hyparse.objects import MeetInfo, Athlete, Team, IndividualResult, RelayResult
from hyparse.parser.validator import ChecksumValidator, validate_file_structure
from hyparse.parser.line_specs import LINE_SPECS
from hyparse.transformers import IndividualResultTransformer, RelayResultTransformer
from hyparse.exceptions import ChecksumError, FileFormatError

# Use module-level logger instead of configuring root logger
logger = logging.getLogger(__name__)


class Hy3File:
    """
    Parses Hy-Tek .hy3 meet result files into structured objects and DataFrames.
    Refactored for efficiency and maintainability.

    Args:
        file_name: Path to the .hy3 file to parse.
        strict_mode: If True, raises exceptions on validation errors.
                    If False (default), logs errors and continues parsing.
    """

    # --- Initialization and Parsing ---

    def __init__(self, file_name: str, strict_mode: bool = False):
        """Initializes Hy3File, reads, validates, and parses the .hy3 file.

        Args:
            file_name: Path to the .hy3 file.
            strict_mode: If True, raises exceptions on errors instead of logging.

        Raises:
            FileNotFoundError: If file doesn't exist.
            FileFormatError: If file structure is invalid (strict_mode only).
            ChecksumError: If checksums don't match (strict_mode only).
            StructuralError: If file has structural issues (strict_mode only).
        """
        self.file_name = file_name
        self.strict_mode = strict_mode
        self.teams: Dict[str, Team] = {}  # Use dict for faster lookup by abbreviation
        self.athletes: Dict[str, Athlete] = {}  # Use dict for faster lookup by mm_id
        self.individual_results: List[IndividualResult] = []
        self.relay_results: List[RelayResult] = []
        self.meet_info: Optional[MeetInfo] = None
        self.raw_lines: List[str] = []
        self.parse_errors: List[Tuple[int, str, str]] = []  # (line_num, line_content, error_msg)

        self._load_and_process_file()

    def _load_and_process_file(self):
        """Loads, cleans, validates checksums, and parses the file content."""
        try:
            with open(self.file_name, "r", encoding="latin-1") as f:  # Common encoding for hy3
                self.raw_lines = [line.rstrip("\r\n") for line in f]  # Strip trailing newlines/CR
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_name}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {self.file_name}: {e}")
            raise

        if not self.raw_lines:
            logger.warning(f"File {self.file_name} is empty.")
            if self.strict_mode:
                raise FileFormatError("File is empty")
            return

        # Validate file structure
        structure_valid, structure_errors = validate_file_structure(self.raw_lines)
        if not structure_valid:
            error_msg = f"File structure validation failed: {structure_errors}"
            logger.error(error_msg)
            if self.strict_mode:
                raise FileFormatError("; ".join(structure_errors))

        # Validate checksums
        checksums_valid, checksum_errors = ChecksumValidator.validate_lines(self.raw_lines)
        if not checksums_valid:
            # Add checksum errors to parse_errors
            self.parse_errors.extend(checksum_errors)
            logger.warning(
                f"Checksum errors found in {len(checksum_errors)} line(s). "
                + (
                    "Raising exception."
                    if self.strict_mode
                    else "Parsing will continue, but results may be inaccurate."
                )
            )
            if self.strict_mode:
                # Raise the first checksum error
                first_error = checksum_errors[0]
                line_num, line, error_msg = first_error
                # Extract expected and actual checksums from error message
                raise ChecksumError(
                    line_num=line_num,
                    expected="",  # Would need to parse from error_msg
                    actual="",  # Would need to parse from error_msg
                    line=line,
                )

        # Parse lines in a single pass
        self._parse_lines()

        logger.info(
            f"Parsed {len(self.teams)} teams, {len(self.athletes)} athletes, "
            f"{len(self.individual_results)} individual results, "
            f"{len(self.relay_results)} relay results."
        )
        if self.parse_errors:
            logger.warning(
                f"{len(self.parse_errors)} parsing errors encountered. Check `parse_errors` attribute."
            )

    def _parse_line(self, line: str, spec: dict) -> Dict[str, str]:
        """Generic helper to parse fields from a line based on a spec."""
        parsed_data = {}
        for field_name, (start, end) in spec.items():
            # Ensure indices are within line bounds
            if start < len(line):
                parsed_data[field_name] = line[start : min(end, len(line))].strip()
            else:
                parsed_data[field_name] = ""  # Field is beyond line length
        return parsed_data

    def _parse_lines(self):
        """Parses all lines from the file content in a single pass."""
        meet_info_data = {}
        current_team_abbr = None
        pending_e1_data = None
        pending_f1_f2_data = None

        for i, line in enumerate(self.raw_lines):
            if not line or len(line) < 2:
                self.parse_errors.append((i + 1, line, "Line too short or empty"))
                continue

            line_id = line[:2]
            spec = LINE_SPECS.get(line_id)

            if not spec:
                # logging.debug(f"Line {i+1}: Skipping unrecognized line ID: {line_id}")
                continue  # Skip lines we don't have specs for

            try:
                parsed_data = self._parse_line(line, spec)

                # --- Handle Different Line Types ---
                if line_id == "A1":
                    meet_info_data.update(parsed_data)
                elif line_id == "B1":
                    meet_info_data.update(parsed_data)
                elif line_id == "B2":
                    meet_info_data.update(parsed_data)
                    # B2 is typically the last part of meet info
                    self.meet_info = MeetInfo(
                        **{k: v for k, v in meet_info_data.items() if k != "line_id"}
                    )

                elif line_id == "C1":
                    team = Team(**{k: v for k, v in parsed_data.items() if k != "line_id"})
                    if team.team_abbreviation:
                        self.teams[team.team_abbreviation] = team
                        current_team_abbr = team.team_abbreviation
                    else:
                        self.parse_errors.append((i + 1, line, "Team abbreviation missing"))

                elif line_id == "D1":
                    if current_team_abbr:
                        athlete_data = {k: v for k, v in parsed_data.items() if k != "line_id"}
                        athlete_data["team"] = current_team_abbr  # Assign current team
                        athlete = Athlete(**athlete_data)
                        if athlete.mm_id:
                            self.athletes[athlete.mm_id] = athlete
                        else:
                            self.parse_errors.append((i + 1, line, "Athlete mm_id missing"))
                    else:
                        self.parse_errors.append(
                            (i + 1, line, "Athlete record found before team record")
                        )

                elif line_id == "E1":
                    pending_e1_data = {k: v for k, v in parsed_data.items() if k != "line_id"}

                elif line_id == "E2":
                    if pending_e1_data:
                        result_data = {k: v for k, v in parsed_data.items() if k != "line_id"}
                        # Combine E1 and E2 data. E2 values overwrite E1 for overlapping keys.
                        combined_data = {**pending_e1_data, **result_data}

                        # --- REMOVE THIS LINE ---
                        # combined_data['points'] = result_data.get('points') or pending_e1_data.get('points')
                        # --- END REMOVAL ---

                        try:
                            # Instantiation using the combined dictionary
                            self.individual_results.append(IndividualResult(**combined_data))
                        except (TypeError, ValidationError) as e:
                            self.parse_errors.append(
                                (
                                    i + 1,
                                    line,
                                    f"Instantiation error: {e} Data: {combined_data}",
                                )
                            )
                            logger.error(
                                f"Line {i+1}: Error creating IndividualResult: {e}. Data: {combined_data}"
                            )

                        pending_e1_data = None  # Reset for next E1
                    else:
                        self.parse_errors.append(
                            (i + 1, line, "E2 record found without preceding E1")
                        )
                        logger.warning(f"Line {i+1}: E2 record found without preceding E1: {line}")

                elif line_id == "F1":
                    pending_f1_f2_data = {k: v for k, v in parsed_data.items() if k != "line_id"}

                elif line_id == "F2":
                    # CORRECTED CHECK: Simply check if pending_f1_f2_data exists (is not None/empty)
                    if pending_f1_f2_data:
                        f2_data = {k: v for k, v in parsed_data.items() if k != "line_id"}
                        # Extract reaction times into a list
                        reaction_times = [
                            f2_data.pop("reaction_time_1", None),
                            f2_data.pop("reaction_time_2", None),
                            f2_data.pop("reaction_time_3", None),
                            f2_data.pop("reaction_time_4", None),
                        ]
                        pending_f1_f2_data.update(f2_data)
                        pending_f1_f2_data["reaction_times"] = [
                            rt for rt in reaction_times if rt is not None
                        ]
                        # Use F2's points if available, otherwise F1's (already handled by update)
                        pending_f1_f2_data["points"] = f2_data.get(
                            "points"
                        ) or pending_f1_f2_data.get("points")

                    else:
                        # This error should now only trigger if F2 appears truly without a preceding F1
                        self.parse_errors.append(
                            (i + 1, line, "F2 record found without preceding F1")
                        )
                        logger.warning(f"Line {i+1}: F2 record found without preceding F1: {line}")
                        pending_f1_f2_data = None  # Reset

                elif line_id == "F3":
                    # CORRECTED CHECK: Simply check if pending_f1_f2_data exists (is not None/empty)
                    if pending_f1_f2_data:  # Check if F1/F2 data exists
                        f3_data = {k: v for k, v in parsed_data.items() if k != "line_id"}
                        relay_athletes = [
                            f3_data.get("athlete_1_mm_id"),
                            f3_data.get("athlete_2_mm_id"),
                            f3_data.get("athlete_3_mm_id"),
                            f3_data.get("athlete_4_mm_id"),
                        ]
                        # Filter out potential empty slots if format varies
                        pending_f1_f2_data["relay_athletes"] = [
                            ath for ath in relay_athletes if ath
                        ]

                        # Finalize RelayResult object
                        try:
                            # Instantiation using the combined dictionary
                            self.relay_results.append(RelayResult(**pending_f1_f2_data))
                        except (TypeError, ValidationError) as e:
                            self.parse_errors.append(
                                (
                                    i + 1,
                                    line,
                                    f"Relay Instantiation error: {e} Data: {pending_f1_f2_data}",
                                )
                            )
                            logger.error(
                                f"Line {i+1}: Error creating RelayResult: {e}. Data: {pending_f1_f2_data}"
                            )

                        pending_f1_f2_data = None  # Reset for next F1
                    else:
                        # This error should now only trigger if F3 appears truly without preceding F1/F2
                        self.parse_errors.append(
                            (i + 1, line, "F3 record found without preceding F1/F2")
                        )
                        logger.warning(
                            f"Line {i+1}: F3 record found without preceding F1/F2: {line}"
                        )
                        pending_f1_f2_data = None  # Reset

            except Exception as e:
                self.parse_errors.append((i + 1, line, f"Parsing error: {e}"))
                # Reset pending data on error to prevent incorrect merging
                pending_e1_data = None
                pending_f1_f2_data = None

    # --- DataFrame Conversion ---

    def individual_results_to_df(self) -> pd.DataFrame:
        """Converts individual results to a Pandas DataFrame.

        Uses IndividualResultTransformer for transformation logic.

        Returns:
            DataFrame with formatted individual results.
        """
        transformer = IndividualResultTransformer(meet_info=self.meet_info)
        return transformer.transform(self.individual_results, self.athletes)

    def relay_results_to_df(self) -> pd.DataFrame:
        """Converts relay results to a Pandas DataFrame.

        Uses RelayResultTransformer for transformation logic.

        Returns:
            DataFrame with formatted relay results.
        """
        transformer = RelayResultTransformer(meet_info=self.meet_info)
        return transformer.transform(self.relay_results)

    def __repr__(self):
        """Returns a string representation of the Hy3File object."""
        return f"Hy3File(file_name='{self.file_name}', meet='{self.meet_info.meet_name if self.meet_info else 'N/A'}')"
