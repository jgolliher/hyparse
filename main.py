from hyparse import Hy3File

file_name = "data/Meet Results-2024 Tennessee Invitational-19Nov2024-001.hy3"

file = Hy3File(file_name=file_name)
file.load_and_extract()

# Extract individual results to Pandas DataFrame
file.to_df()

# Extract all Athelte objects (returns List[Athlete])
file.athletes

# Extract all Team objects (returns List[Team])
file.teams

# Extract all IndividaulResult objects (returns List[IndividualResult])
file.individual_results
