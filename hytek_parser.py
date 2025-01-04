class HyTekParser:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.file_info = {}
        self.teams = []
        self.athletes = []

    def load_file(self, filepath: str):
        """Loads a HyTek .hy3 file for parsing.

        Args:
            filepath: The path to the .hy3 file.
        """
        self.filepath = filepath
        with open(filepath, "r") as f:
            lines = f.readlines()
        self.parse_file_info(lines)
        self.extract_teams(lines)
        self.extract_athletes(lines)

    def parse_file_info(self, lines: list):
        """Parses the A1 line from a HyTek .hy3 file and extracts file information."""
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

    def parse_team_info(self, line: str) -> dict:
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

    def extract_teams(self, lines: list):
        """Extracts all team information from a list of lines in a HyTek .hy3 file.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.
        """
        for line in lines:
            if line.startswith("C1"):
                try:
                    team_data = self.parse_team_info(line)
                    self.teams.append(team_data)
                except ValueError as e:
                    print(f"Warning: Could not parse line: {line}. Error: {e}")

    def parse_athlete_info(self, line: str, current_team: dict = None) -> dict:
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

    def extract_athletes(self, lines: list):
        """Extracts all athlete information from a list of lines in a HyTek .hy3 file.

        Args:
            lines: A list of strings, each representing a line from the .hy3 file.
        """
        current_team = {}  # Initialize current_team
        for line in lines:
            if line.startswith("C1"):
                try:
                    current_team = self.parse_team_info(line)
                except ValueError as e:
                    print(f"Warning: Could not parse team line: {line}. Error: {e}")
            elif line.startswith("D1"):
                try:
                    athlete_data = self.parse_athlete_info(line, current_team)
                    self.athletes.append(athlete_data)
                except ValueError as e:
                    print(f"Warning: Could not parse athlete line: {line}. Error: {e}")
