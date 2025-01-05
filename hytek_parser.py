import pandas as pd


class HyTekParser:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.file_info = {}
        self.teams = []
        self.athletes = []
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

    def load_file(self, filepath: str):
        """Loads a HyTek .hy3 file for parsing.

        Args:
            filepath: The path to the .hy3 file.
        """
        self.filepath = filepath
        with open(filepath, "r") as f:
            lines = f.readlines()
        self._parse_file_info(lines)
        self._extract_teams(lines)
        self._extract_athletes(lines)
        self._extract_athletes(lines)
        self._extract_results(lines)

    def _parse_file_info(self, lines: list):
        """Parses the A1 line from a HyTek .hy3 file and extracts file information.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.

        Returns:
            None

        Raises:
            ValueError: If the line ID is not A1.
        """
        a1_lines = [x for x in lines if x.startswith("A1")]

        if not a1_lines:
            print("Warning: No A1 line found in the file.")
            return

        line = a1_lines[0]

        line_id = line[:2]
        if line_id != "A1":
            raise ValueError("Line ID is not A1! Possible file issue.")

        self.file_info["line_id"] = line[:2].strip()
        self.file_info["result_type"] = line[2:4].strip()
        self.file_info["mm_version"] = line[44:58].strip()
        self.file_info["date_created"] = line[58:68].strip()

    def _parse_team_info(self, line: str) -> dict:
        """Parses a single C1 line from a HyTek .hy3 file and extracts team information.

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
        return {
            "line_id": line[:2].strip(),
            "team_abbreviation": line[2:7].strip(),
            "full_team_name": line[7:37].strip(),
            "team_short_name": line[37:53].strip(),
            "team_lsc": line[53:55].strip(),
        }

    def _extract_teams(self, lines: list):
        """Extracts all team information from a list of lines in a HyTek .hy3 file.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.

        Returns:
            None

        Raises:
            ValueError: If the line ID is not C1.
        """
        for line in lines:
            if line.startswith("C1"):
                try:
                    team_data = self._parse_team_info(line)
                    self.teams.append(team_data)
                except ValueError as e:
                    print(f"Warning: Could not parse line: {line}. Error: {e}")

    def _parse_athlete_info(self, line: str, current_team: dict = None) -> dict:
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
            "line_id": line[:2].strip(),
            "gender": line[2],
            "mm_id": line[3:8].strip(),
            "last_name": line[8:28].strip(),
            "first_name": line[28:48].strip(),
            "nick_name": line[48:68].strip(),
            "usas_id": line[69:86].strip(),
            "team": current_team.get("team_abbreviation") if current_team else None,
        }
        return athlete_data

    def _extract_athletes(self, lines: list):
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
                    athlete_data = self._parse_athlete_info(line, current_team)
                    self.athletes.append(athlete_data)
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
            "line_id": line[:2].strip(),
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
            "line_id": line[:2].strip(),
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
        self.results = []
        current_athlete = None
        current_event_entry = None

        for line in lines:
            if line.startswith("D1"):
                # Get athlete info
                athlete_id = line[3:8].strip()
                for athlete in self.athletes:
                    if athlete["mm_id"] == athlete_id:
                        current_athlete = athlete
                        break

            elif line.startswith("E1"):
                # New event entry
                if current_athlete is None:
                    raise ValueError(
                        "Found E1 line without a preceding D1 line for an athlete."
                    )
                current_event_entry = self._parse_event_entry(line)
                self.results.append(
                    {
                        "athlete": current_athlete,
                        "event": current_event_entry,
                        "results": [],
                    }
                )

            elif line.startswith("E2"):
                # Result for the current event entry
                if current_event_entry is None:
                    raise ValueError(
                        "Found E2 line without a preceding E1 line for an event."
                    )
                result_data = self._parse_result(line)

                # Find the correct result entry to append to
                for res in self.results:
                    if (
                        res["athlete"] == current_athlete
                        and res["event"] == current_event_entry
                    ):
                        res["results"].append(result_data)
                        break

            elif line.startswith("C1"):
                current_athlete = None  # Reset when switching to new team
                current_event_entry = None

    def results_to_dataframe(self) -> pd.DataFrame:
        """Converts the extracted results data into a Pandas DataFrame.

        Returns:
            A Pandas DataFrame where each row represents an event entry with
            associated athlete and result information.
        """
        rows = []
        for result in self.results:
            athlete = result["athlete"]
            event = result["event"]
            for r in result["results"]:
                row = {
                    "mm_id": athlete["mm_id"],
                    "usas_id": athlete["usas_id"],
                    "first_name": athlete["first_name"],
                    "last_name": athlete["last_name"],
                    "gender": athlete["gender"],
                    "team": athlete["team"],
                    "event_no": event["event_no"],
                    "stroke": self.STROKE_CODES.get(event["stroke_code"], "Unknown"),
                    "distance": event["distance"],
                    "seed_time": event["seed_time"],
                    "result_round": r["round"],
                    "result_time": r["time"],
                    "course": r["course"],
                    "heat": r["heat"],
                    "lane": r["lane"],
                    "heat_place": r["heat_place"],
                    "overall_place": r["overall_place"],
                    "backup_time_1": r["backup_time_1"],
                    "backup_time_2": r["backup_time_2"],
                    "reaction_time": r["reaction_time"],
                }
                rows.append(row)

            # Handle cases where there are no results
            if not result["results"]:
                row = {
                    "mm_id": athlete["mm_id"],
                    "usas_id": athlete["usas_id"],
                    "first_name": athlete["first_name"],
                    "last_name": athlete["last_name"],
                    "gender": athlete["gender"],
                    "team": athlete["team"],
                    "event_no": event["event_no"],
                    "stroke": self.STROKE_CODES.get(event["stroke_code"], "Unknown"),
                    "distance": event["distance"],
                    "seed_time": event["seed_time"],
                    "result_round": None,
                    "result_time": None,
                    "course": None,
                    "heat": None,
                    "lane": None,
                    "heat_place": None,
                    "overall_place": None,
                    "backup_time_1": None,
                    "backup_time_2": None,
                    "reaction_time": None,
                }
                rows.append(row)
        return pd.DataFrame(rows)
