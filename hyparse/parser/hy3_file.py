from typing import Dict, List, Tuple, Any, Optional
from hyparse import MeetInfo, Athlete, Team, IndividualEntry, IndividualResult
import pandas as pd


class Hy3File:
    def __init__(self, file_name: str):
        """Initialize a Hy3File object.

        Args:
            file_name (str): The path to the .hy3 file.
        """
        self.file_name = file_name
        self.teams = []
        self.athletes = []
        self.individual_results = []
        self.STROKE_CODES = {
            "A": "Free",
            "B": "Back",
            "C": "Breast",
            "D": "Fly",
            "E": "Medley",
            "F": "1m",
            "G": "3m",
            "H": "10m",
        }

    def load_and_extract(self):
        """Loads and extracts information from a .hy3 file.

        Returns:
            None
        """
        with open(self.file_name, "r") as f:
            self.file_contents = f.readlines()
        # TODO: Add function to ensure file is in correct format
        self.file_contents = [x.replace("\n", "") for x in self.file_contents]
        # Run checksum
        self._run_checksum(self.file_contents)
        self._extract_teams(self.file_contents)
        self._extract_athletes(self.file_contents)
        self._extract_results(self.file_contents)

    def _calculate_checksum(self, line: str) -> int:
        """
        Calculates the .hy3 checksum.

        Args:
            line (str): The string for which to calculate the checksum.

        Returns:
            A two-digit checksum string.
        """
        line = line[:-2]
        chars = list(line)

        ord_chars = [ord(char) for char in chars]

        odd = []
        even = []

        for i in range(len(chars)):
            if i % 2:
                odd.append(ord_chars[i])
            else:
                even.append(ord_chars[i])

        odd_sum = 0
        even_sum = 0

        for num in odd:
            odd_sum += 2 * num
        for num in even:
            even_sum += num

        sum_val = odd_sum + even_sum
        result = sum_val // 21
        sum2 = result + 205
        checksum1 = str(sum2)[-1]
        checksum2 = str(sum2)[-2]
        checksum = checksum1 + checksum2
        return checksum

    def _run_checksum(self, lines: List[str]):
        """Calculates checksum and compares to actual.

        Args:
            line (str): The string for which to calculate the checksum.

        Returns:
            None

        Raises:
            ValueError: If the checksums do not match.
        """

        for line in lines:
            calculated_checksum = self._calculate_checksum(line)
            actual_checksum = line[-2:]
            if calculated_checksum != actual_checksum:
                raise ValueError(
                    f"Checksums do not match! {calculated_checksum} != {actual_checksum} for line: {line}"
                )

    def get_teams(self) -> List[Team]:
        """Returns a list of Team objects.

        Returns:
            List[Team]: A list of Team objects.
        """
        self.load_and_extract()
        return self.teams

    def get_athletes(self) -> List[Athlete]:
        """Returns a list of Athlete objects.

        Returns:
            List[Athlete]: A list of Athlete objects.
        """
        self.load_and_extract()
        return self.athletes

    def get_individual_results(self) -> List[IndividualResult]:
        """Returns a list of IndividualResult objects.

        Returns:
            List[IndividualResult]: A list of IndividualResult objects.
        """
        self.load_and_extract()
        return self.individual_results

    def __repr__(self):
        """A string representation of the .hy3 file.

        Returns:
            str: A string representation of the .hy3 file.
        """
        return f"Hy3File(file_name={self.file_name})"

    def _parse_team_info(self, line: str) -> Team:
        """Parses a single C1 line from a .hy3 file and extracts team information.

        Args:
            line: A string representing a single line from the .hy3 file.

        Returns:
            A dictionary containing the extracted team information.

        Raises:
            ValueError: If the line ID is not C1.
        """
        line_id = line[:2]
        if line_id != "C1":
            raise ValueError("Line ID is not C1! Possible file issue.")
        team_data = {
            "team_abbreviation": line[2:7].strip(),
            "full_team_name": line[7:37].strip(),
            "team_short_name": line[37:53].strip(),
            "team_lsc": line[53:55].strip(),
        }
        team = Team(**team_data)
        return team

    def _extract_teams(self, lines: list) -> List[Team]:
        """Extracts all team information from a list of lines in a HY3 file and returns a list of Team objects.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.

        Returns:
            List[Team]: A list of Team objects.

        Raises:
            ValueError: If the line ID is not C1.
        """
        for line in lines:
            if line.startswith("C1"):
                try:
                    team = self._parse_team_info(line)
                    self.teams.append(team)
                except ValueError as e:
                    print(f"Warning: Could not parse line: {line}. Error: {e}")

    def _parse_athlete_info(self, line: str, current_team: Team) -> Athlete:
        """Parses a single D1 line from a HyTek .hy3 file and extracts athlete information.

        Args:
            line: A string representing a single line from the .hy3 file.
            current_team: The current team as a dictionary (optional).

        Returns:
            A dictionary containing the extracted athlete information.

        Raises:
            ValueError: If the line ID is not D1.
        """
        line_id = line[:2]
        if line_id != "D1":
            raise ValueError("Line ID is not D1! Possible file issue.")

        athlete_data = {
            "gender": line[2],
            "mm_id": line[3:8].strip(),
            "last_name": line[8:28].strip(),
            "first_name": line[28:48].strip(),
            "nick_name": line[48:68].strip(),
            "usas_id": line[69:86].strip(),
            "team": current_team.team_abbreviation if current_team else None,
        }
        athlete = Athlete(**athlete_data)
        return athlete

    def _extract_athletes(self, lines: list) -> List[Athlete]:
        """Extracts all athlete information from a list of lines in a HyTek .hy3 file.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.

        Returns:
            None

        Raises:
            ValueError: If the line ID is not D1.
        """
        current_team = {}
        for line in lines:

            if line.startswith("C1"):
                try:
                    current_team = self._parse_team_info(line)
                except ValueError as e:
                    print(f"Warning: Could not parse team line: {line}. Error: {e}")
            elif line.startswith("D1"):
                try:
                    athlete = self._parse_athlete_info(line, current_team)
                    self.athletes.append(athlete)
                except ValueError as e:
                    print(f"Warning: Could not parse athlete line: {line}. Error: {e}")

    def _parse_event_entry(self, line: str) -> dict:
        """Parses a single E1 line from a HyTek .hy3 file and extracts event entry information.

        Args:
            line: A string representing a single line from the .hy3 file.

        Returns:
            A dictionary containing the extracted event entry information.

        Raises:
            ValueError: If the line ID is not E1.
        """
        if not line.startswith("E1"):
            raise ValueError("Line ID is not E1! Possible file issue.")
        return {
            "mm_athlete_id": line[3:8].strip(),
            "event_no": line[38:42].strip(),
            "stroke_code": line[21].strip(),
            "distance": line[15:21].strip(),
            "seed_time": line[42:50].strip(),
        }

    def _parse_result(self, line: str) -> dict:
        """Parses a single E2 line from a HyTek .hy3 file and extracts result information.

        Args:
            line: A string representing a single line from the .hy3 file.

        Returns:
            A dictionary containing the extracted result information.

        Raises:
            ValueError: If the line ID is not E2.
        """
        if not line.startswith("E2"):
            raise ValueError("Line ID is not E2! Possible file issue.")

        return {
            "round": line[2].strip(),
            "time": line[3:11].strip(),
            "course": line[11].strip(),
            "heat": line[20:24].strip(),
            "lane": line[25:27].strip(),
            "heat_place": line[26:29].strip(),
            "overall_place": line[29:33].strip(),
            "backup_time_1": line[36:44].strip(),
            "backup_time_2": line[45:52].strip(),
            "reaction_time": line[83:87].strip(),
        }

    def _extract_results(self, lines: list):
        """
        Extracts all results (E1 and E2 lines) from a list of lines in a HyTek .hy3 file.
        Associates results with athletes and their event entries.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.

        Returns:
            None

        Raises:
            ValueError: If the line ID is not E1 or E2.
        """

        for line in lines:
            if line.startswith("E1"):  # Event entry line
                current_event_entry = self._parse_event_entry(line)
            elif line.startswith("E2"):  # Result line
                result_data = self._parse_result(line)
                # Combine dicts
                combined_dict = {**current_event_entry, **result_data}
                result = IndividualResult(**combined_dict)
                self.individual_results.append(result)

    def to_df(self) -> pd.DataFrame:
        """Turn results into Pandas DataFrame.

        Args:
            None

        Returns:
            pd.DataFrame: A DataFrame of results.
        """
        athlete_dict = {athlete.mm_id: athlete for athlete in self.athletes}
        full_results = []
        for result in self.individual_results:
            inner_results = {
                **athlete_dict[result.mm_athlete_id].to_dict(),
                **result.to_dict(),
            }
            inner_results["stroke"] = self.STROKE_CODES.get(
                inner_results["stroke_code"], "Unknown"
            )
            full_results.append(inner_results)
        df = pd.DataFrame(full_results)
        df = df[
            [
                "mm_athlete_id",
                "usas_id",
                "first_name",
                "last_name",
                "gender",
                "team",
                "event_no",
                "stroke",
                "distance",
                "seed_time",
                "round",
                "time",
                "course",
                "heat",
                "lane",
                "heat_place",
                "overall_place",
                "backup_time_1",
                "backup_time_2",
                "reaction_time",
            ]
        ]
        return df
