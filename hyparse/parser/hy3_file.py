from typing import Dict, List, Tuple, Any, Optional
from hyparse import MeetInfo, Athlete, Team, IndividualResult, RelayResult
import pandas as pd
from copy import deepcopy


class Hy3File:
    def __init__(self, file_name: str):
        """Initializes a Hy3File object for parsing meet results.

        Args:
            file_name (str): Path to the .hy3 file.

        Example:
            >>> hy3_file = Hy3File("path/to/meet_results.hy3")
        """
        self.file_name = file_name
        self.teams = []
        self.athletes = []
        self.individual_results = []
        self.relay_results = []
        self.meet_info = None
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

        # Load and extract
        with open(self.file_name, "r") as f:
            self.file_contents = f.readlines()

        # TODO: Add function to ensure file is in correct format
        self.file_contents = [x.replace("\n", "") for x in self.file_contents]
        # Run checksum
        self._run_checksum(self.file_contents)
        self.meet_info = self._extract_meet_info(self.file_contents)
        self._extract_teams(self.file_contents)
        self._extract_athletes(self.file_contents)
        self._extract_individual_results(self.file_contents)
        self._extract_relay_results(self.file_contents)

    def _calculate_checksum(self, line: str) -> int:
        """Calculates the checksum for a given line.

        Args:
            line (str): The line from the .hy3 file (excluding the last two checksum characters).

        Returns:
            str: The calculated two-digit checksum.

        Example:
            >>> checksum = hy3_file._calculate_checksum("A102                    ")
            >>> print(checksum)
            07
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
        """Validates the checksum for each line in the file.

        Args:
            lines (List[str]): A list of lines from the .hy3 file.

        Raises:
            ValueError: If any checksum does not match the calculated value.


        Example:
            >>> hy3_file._run_checksum(hy3_file.file_contents)
        """

        for line in lines:
            calculated_checksum = self._calculate_checksum(line)
            actual_checksum = line[-2:]
            if calculated_checksum != actual_checksum:
                raise ValueError(
                    f"Checksums do not match! {calculated_checksum} != {actual_checksum} for line: {line}"
                )

    def __repr__(self):
        """Returns a string representation of the Hy3File object.

        Returns:
            str: String representation of the object.

        Example:
            >>> print(hy3_file)
            Hy3File(file_name="path/to/meet_results.hy3")
        """
        return f"Hy3File(file_name={self.file_name})"

    def _extract_meet_info(self, lines: List) -> MeetInfo:
        """Extracts meet information from the .hy3 file.

        Args:
            lines (List[str]): List of lines from the file.

        Returns:
            MeetInfo: A MeetInfo object containing the extracted meet information.


        Example:
            >>> meet_info = hy3_file._extract_meet_info(hy3_file.file_contents)
            >>> print(meet_info.meet_name)

        """
        for line in lines:
            if line.startswith("A1"):
                a1_line = line
            elif line.startswith("B1"):
                b1_line = line
            elif line.startswith("B2"):
                b2_line = line

        a1_line_id = a1_line[:2]
        b1_line_id = b1_line[:2]
        b2_line_id = b2_line[:2]
        if a1_line_id != "A1":
            raise ValueError(f"Line ID is not A1! Possible file issue.")
        if b1_line_id != "B1":
            raise ValueError(f"Line ID is not B1! Possible file issue.")
        if b2_line_id != "B2":
            raise ValueError(f"Line ID is not B2! Possible file issue.")

        return MeetInfo(
            meet_name=b1_line[2:47].strip(),
            facility_name=b1_line[47:92].strip(),
            meet_start_date=b1_line[92:100].strip(),
            meet_end_date=b1_line[100:108].strip(),
            elevation=b1_line[116:121].strip(),
            course=b2_line[98].strip(),
            result_type=a1_line[2:4].strip(),
            mm_version=a1_line[44:58].strip(),
            date_file_created=a1_line[58:68].strip(),
        )

    def _parse_team_info(self, line: str) -> Team:
        """Parses team information from a C1 line.

        Args:
            line (str): A C1 line from the .hy3 file.

        Returns:
            Team: A Team object with the parsed team information.

        Raises:
            ValueError: If the input line is not a C1 line.

        Example:
            >>> team = hy3_file._parse_team_info("C1TEAM1Team One       Team One   SC")
            >>> print(team.full_team_name)
            Team One
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
        """Extracts all team information from the .hy3 file.

        Args:
            lines (List[str]): List of lines from the file.

        Returns:
            None. Updates the `self.teams` list.

        Example:
            >>> hy3_file._extract_teams(hy3_file.file_contents)
        """
        for line in lines:
            if line.startswith("C1"):
                try:
                    team = self._parse_team_info(line)
                    self.teams.append(team)
                except ValueError as e:
                    print(f"Warning: Could not parse line: {line}. Error: {e}")

    def _parse_athlete_info(self, line: str, current_team: Team) -> Athlete:
        """Parses athlete information from a D1 line.

        Args:
            line (str): A D1 line from the .hy3 file.
            current_team (Team): The current Team object.

        Returns:
            Athlete: An Athlete object with the parsed athlete information.

        Raises:
            ValueError: If the input line is not a D1 line.

        Example:
            >>> team = Team(team_abbreviation="TEAM1")
            >>> athlete = hy3_file._parse_athlete_info(
            ...     "D1M1234  DOE       JOHN       JOHNNY1234567890   TEAM1", team
            ... )
            >>> print(athlete.first_name)
            JOHN
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
            "usas_id": line[69:85].strip(),
            "team": current_team.team_abbreviation if current_team else None,
        }
        athlete = Athlete(**athlete_data)
        return athlete

    def _extract_athletes(self, lines: list) -> List[Athlete]:
        """Extracts all athlete information from the .hy3 file.

        Args:
            lines (List[str]): List of lines from the file.

        Returns:
            None. Updates the `self.athletes` list.

        Example:
            >>> hy3_file._extract_athletes(hy3_file.file_contents)

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
        """Parses event entry information from an E1 line.

        Args:
            line (str): An E1 line from the .hy3 file.

        Returns:
            dict: A dictionary containing the parsed event entry information.

        Raises:
            ValueError: If the input line is not an E1 line.


        Example:
            >>> event_entry = hy3_file._parse_event_entry(
            ...     "E1M1234  DOE       M BG100 A 01  55.00 L 54.00 Y"
            ... )
            >>> print(event_entry["event_no"])
            01
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

    def _parse_individual_result(self, line: str) -> dict:
        """Parses individual result information from an E2 line.

        Args:
            line (str): An E2 line from the .hy3 file.

        Returns:
            dict: A dictionary containing the parsed result information.

        Raises:
            ValueError: If the input line is not an E2 line.


        Example:
            >>> result_info = hy3_file._parse_individual_result(
            ...     "E2F 53.50 L  1 04  1  1 00:00.00 01:01.00 0.65  "
            ... )
            >>> print(result_info["time"])
            53.50
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

    def _extract_individual_results(self, lines: list):
        """Extracts all individual event results from the .hy3 file.

        Args:
            lines (List[str]): List of lines from the file.

        Returns:
            None. Updates the `self.individual_results` list.

        Example:
            >>> hy3_file._extract_individual_results(hy3_file.file_contents)

        """
        for line in lines:
            if line.startswith("E1"):  # Event entry line
                current_event_entry = self._parse_event_entry(line)
            elif line.startswith("E2"):  # Result line
                result_data = self._parse_individual_result(line)
                # Combine dicts
                combined_dict = {**current_event_entry, **result_data}
                result = IndividualResult(**combined_dict)
                self.individual_results.append(result)

    def _parse_f1_line(self, line: str) -> Dict:
        """Parses relay entry information from an F1 line.

        Args:
            line (str): An F1 line from the .hy3 file.

        Returns:
            Dict: A dictionary containing the parsed relay entry information.

        Raises:
            ValueError: If the input line is not an F1 line.

        Example:
            >>> relay_entry = hy3_file._parse_f1_line(
            ... "F1TEAM1A  M                              M400 A   2:50.00  "
            ... )

        """
        if not line.startswith("F1"):
            raise ValueError("Line ID is not F1! Possible file issue.")

        return {
            "team_abbr": line[2:6].strip(),
            "relay_team": line[7],
            "gender": line[12],
            "distance": line[17:21].strip(),
            "stroke_code": line[21],
            "event_no": line[38:42].strip(),
            "seed_time": line[43:50].strip(),
        }

    def _parse_f2_line(self, line: str) -> Dict:
        """Parses relay result information from an F2 line.

        Args:
            line (str): An F2 line from the .hy3 file.

        Returns:
            Dict: A dictionary containing the parsed relay result information.

        Raises:
            ValueError: If the input line is not an F2 line.

        Example:
        >>> relay_result = hy3_file._parse_f2_line("F2F 2:40.00 L    1 03 1  1  2:30.00 2:31.55 2:32.11       0.70 0.65 0.68 0.60     1201200007")

        """
        if not line.startswith("F2"):
            raise ValueError("Line ID is not F2! Possible file issue.")

        return {
            "round": line[2].strip(),
            "time": line[3:11].strip(),
            "course": line[11],
            "time_code": line[12:15].strip(),
            "heat": line[20:24].strip(),
            "lane": line[25:27].strip(),
            "heat_place": line[26:29].strip(),
            "overall_place": line[29:33].strip(),
            "backup_time_1": line[36:44].strip(),
            "backup_time_2": line[44:52].strip(),
            "backup_time_3": line[52:60].strip(),
            "touchpad_time": line[65:73].strip(),
            "reaction_times": [
                line[83:87].strip(),
                line[87:92].strip(),
                line[92:97].strip(),
                line[97:102].strip(),
            ],
        }

    def _parse_f3_line(self, line: str) -> List:
        """Parses relay swimmer information from an F3 line.

        Args:
            line (str): An F3 line from the .hy3 file.

        Returns:
            List: A list of swimmer MM IDs participating in the relay.

        Raises:
            ValueError: If the input line is not an F3 line.


        Example:
            >>> relay_swimmers = hy3_file._parse_f3_line(
            ...     "F3M00001AAAAAAM1M00002BBBBBM1M00003CCCCCM1M00004DDDDDM1                    07"
            ... )
        """

        if not line.startswith("F3"):
            raise ValueError("Line ID is not F3! Possible file issue.")

        return {
            "relay_athletes": [
                line[3:8].strip(),
                line[16:21].strip(),
                line[29:34].strip(),
                line[42:47].strip(),
            ]
        }

    def _extract_relay_results(self, lines: List):
        """Extracts all relay results from the .hy3 file.

        Args:
            lines (List[str]): List of lines from the file.

        Returns:
            None. Updates the `self.relay_results` list.

        Example:
            >>> hy3_file._extract_relay_results(hy3_file.file_contents)
        """
        for line in lines:
            if line[:2] == "F1":
                f1_data = self._parse_f1_line(line=line)
            elif line[:2] == "F2":
                f2_data = self._parse_f2_line(line=line)
            elif line[:2] == "F3":
                f3_data = self._parse_f3_line(line=line)
                all_relay_data = {**f1_data, **f2_data, **f3_data}
                relay_result = RelayResult(**all_relay_data)
                self.relay_results.append(relay_result)

    def individual_results_to_df(self) -> pd.DataFrame:
        """Converts individual results to a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing individual results.

        Example:
            >>> individual_results_df = hy3_file.individual_results_to_df()
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
        df["meet_name"] = self.meet_info.meet_name
        df["facility_name"] = self.meet_info.facility_name
        df["meet_start_date"] = self.meet_info.meet_start_date
        df["meet_end_date"] = self.meet_info.meet_end_date
        df = df[
            [
                "meet_name",
                "facility_name",
                "meet_start_date",
                "meet_end_date",
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

    def _transform_relay_data(self, data):
        """Transforms relay data into a DataFrame-friendly format.

        Args:
            data (Dict): A dictionary containing relay race data.

        Returns:
            Dict: A transformed dictionary suitable for DataFrame creation.

        Example:
            >>> transformed_data = hy3_file._transform_relay_data(relay_result.to_dict())
        """

        data_copy = deepcopy(data)
        athletes = data_copy.pop("relay_athletes")
        reaction_times = data_copy.pop("reaction_times")

        for i, athlete in enumerate(athletes):
            data_copy[f"swimmer_{i+1}_mm_id"] = athlete

        for i, reaction_time in enumerate(reaction_times):
            data_copy[f"reaction_time_{i+1}"] = reaction_time

        return data_copy

    def relay_results_to_df(self) -> pd.DataFrame:
        """Converts relay results to a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing relay results.

        Example:
            >>> relay_results_df = hy3_file.relay_results_to_df()

        """
        athlete_dict = {athlete.mm_id: athlete for athlete in self.athletes}
        full_results = []
        for result in self.relay_results:
            inner_results = self._transform_relay_data(result.to_dict())
            inner_results["stroke"] = self.STROKE_CODES.get(
                inner_results["stroke_code"], "Unknown"
            )
            # TODO: Athlete name or USAS ID?
            full_results.append(inner_results)
        df = pd.DataFrame(full_results)
        df["meet_name"] = self.meet_info.meet_name
        df["facility_name"] = self.meet_info.facility_name
        df["meet_start_date"] = self.meet_info.meet_start_date
        df["meet_end_date"] = self.meet_info.meet_end_date
        df = df[
            [
                "meet_name",
                "facility_name",
                "meet_start_date",
                "meet_end_date",
                "gender",
                "team_abbr",
                "event_no",
                "stroke",
                "distance",
                "seed_time",
                "round",
                "time",
                "time_code",
                "course",
                "heat",
                "lane",
                "heat_place",
                "overall_place",
                "backup_time_1",
                "backup_time_2",
                # TODO: Add ability to handle more than 4 relay names
                "swimmer_1_mm_id",
                "reaction_time_1",
                "swimmer_2_mm_id",
                "reaction_time_2",
                "swimmer_3_mm_id",
                "reaction_time_3",
                "swimmer_4_mm_id",
                "reaction_time_4",
            ]
        ]
        return df
