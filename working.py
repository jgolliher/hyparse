################
# Libraries
################

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

################
# Read file
################
file_name = "data/Meet Results-2023 Tennessee Invitational-15Nov2023-001.hy3"

with open("data/Meet Results-2023 Tennessee Invitational-15Nov2023-001.hy3") as file:
    lines = [line.rstrip() for line in file]


################
# Database Connection
################

# Create engine
engine = create_engine("postgresql+psycopg2://postgres:JWillGoll2020!@localhost:5432")

# Insert into File
pd.DataFrame([file_name], columns=["file_name"]).to_sql(
    name="hy3_file", con=engine, if_exists="append", schema="swimming", index=False
)


raw_lines = pd.DataFrame(lines, columns=["raw_line_content"])

raw_lines["raw_line_content"].str[:2]

raw_lines.to_sql(
    name="hy3_raw_lines", con=engine, if_exists="append", schema="swimming", index=False
)


line = pd.read_sql(
    "SELECT * FROM swimming.hy3_raw_lines WHERE raw_line_id = 316", con=engine
)

line = line["raw_line_content"].iloc[0]

# Pandas preserves fixed width
test = pd.DataFrame(lines, columns=["RawLine"])
test["RawLine"].iloc[1][47:92]

len(lines[10])
data = pd.read_excel("data/hyparse.xlsx")

################
# Connect to db
################


################
# A1 Line (File information)
################

# Define what line type this is
lines[0][:2]  # line_type
lines[0][
    2:4
]  # If line_type is A1, tells the file_type (02 = Meet Entries, 07 = Results from MM to TM)
lines[0][44:58]  # HyTek version

# This does not seem like a great method
exec(
    data["VariableName"].loc[data["LineCode"] == "A1"].iloc[0]
    + " = lines[0]"
    + data["Code"].loc[data["LineCode"] == "A1"].iloc[0]
)

lines[0][128:130]


def parse_file_info(data: list) -> dict:
    line = data[0]
    line_id = line[:2]
    if line_id != "A1":
        raise ValueError("Line ID is not A1! Possible file issue.")
    return {
        "line_id": line[:2].strip(),
        "result_type": line[2:4].strip(),
        "mm_version": line[44:58].strip(),
        "date_created": line[58:68].strip(),
    }


################
# B1 Line (meet information)
################

lines[1][:2]  # line_type
lines[1][2:47]  # Meet name
lines[1][47:92]  # Facility name
lines[1][92:100]  # Meet start date
lines[1][100:108]  # Meet end date
lines[1][108:116]  # Age up date
lines[1][116:121]  # Elevation
lines[1][128:130]  # Checksum

lines[2]


def parse_meet_info(data: list) -> dict:
    b1_line = data[1]
    b1_line_id = b1_line[:2]
    b2_line = data[2]
    b2_line_id = b2_line[:2]
    if b1_line_id != "B1":
        raise ValueError("Line ID is not B1! Possible file issue.")
    if b2_line_id != "B2":
        raise ValueError("Line ID is not B2! Possible file issue.")
    return {
        "line_id": b1_line[:2].strip(),
        "meet_name": b1_line[2:47].strip(),
        "facility_name": b1_line[47:92].strip(),
        "meet_start_date": b1_line[92:100].strip(),
        "meet_end_date": b1_line[100:108].strip(),
        "age_up_date": b1_line[108:116].strip(),
        "elevation": b1_line[116:121].strip(),
        "course": b2_line[98].strip(),
    }


parse_meet_info(data=lines)

################
# B2 Line (meet information)
################

lines[2][:2]  # line_type
lines[2][2:92]  # Meet name
lines[2][92:]  # Meet type... not sure what it all is
lines[2][98]  # Course
lines[2][128:130]  # Checksum


################
# C1 Line (team information)
################

lines[3][:2]  # line_type
lines[3][2:7]  # Team abbreviation
lines[3][7:37]  # Full team name
lines[3][37:53]  # Team short
lines[3][53:55]  # LSC

[line for line in lines if line[:2] == "C1"]


def parse_team_info(line: str) -> dict:
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


parse_team_info(lines)

################
# C2 Line (team address information)
################

lines[394][:2]  # line_type
lines[394][2:]

################
# D1 Line (swimmer entry)
################

line[:2]
line[88:97]

lines[4][:2]  # line_type
lines[4][2]  # gender
lines[4][3:8]  # swimmer id from MM
lines[4][8:28]  # swimmer last name
lines[4][28:48]  # swimmer first name
lines[4][48:68]  # swimmer nick name
lines[4][69:86]  # usas id
lines[4][86:88]  # swimmer id from team database
lines[4][88:97]  # dob
lines[4][97:99]  # age
lines[4][99:104]  # school class
lines[4][128:130]  # checksum


def parse_swimmer_info(data: list) -> dict:
    line = data[4]
    line_id = line[:2]
    if line_id != "D1":
        raise ValueError("Line ID is not D1! Possible file issue.")
    return {
        "line_id": line[:2].strip(),
        "gender": line[2],
        "mm_id": line[3:8].strip(),
        "last_name": line[8:28].strip(),
        "first_name": line[28:48].strip(),
        "nick_name": line[48:68].strip(),
        "usas_id": line[69:86].strip(),
    }


################
# E1 Line (event entry) (needs work)
################

"""
One of the challenges here is getting back to swimmer information.
One option is to go through all of the lines and "split" the data into
chunks by swimmer
"""

line = 318

lines[line][:2]  # line_type
lines[line][2]  # gender
lines[line][3:8]  # swimmer id from MM
lines[line][8:13]  # first five digits of the last name
lines[line][13]  # gender1 (?)
lines[line][14]  # gender2 -- #M=Mens, B=Boys, W=Womens, G=Girls
lines[line][15:21]  # distance
lines[line][21]  # Stroke (A=Free, B=Back, C=Breast, D=Fly, E=Medley, F=1m, G=3m, ?=10m)
lines[line][38:42]  # Event number
lines[line][42:50]  # Conversion Seed Time 1
lines[line][50]  # Conversion Seed Course (L = LCM, S = SCM, Y = Yards)
lines[line][52:59]  # Seed Time 1
lines[line][59]  # Seed Course 1

################
# E2 Line (individual event results)
################

line = 319

lines[line][:2]  # line_type
lines[line][2]  # Result type (F=Final, P=Prelim)
lines[line][3:11]  # Time
lines[line][11]  # Course (L=LCM, S=SCM, Y=Yards)
# TODO: Work this out
lines[line][12:14]  # Time code
lines[line][20:24]  # Heat
lines[line][25:27]  # Lane
lines[line][26:29]  # Heat place
lines[line][29:33]  # Overall place
# TODO: Figure out which number is which
lines[line][36:44]  # Time1
lines[line][45:52]  # Time2
lines[line][83:]  # Reaction time
lines[line][128:130]  # Checksum

################
# G1 Line (splits)
################

# TODO: Figure out how to parse multiple splits
"""
Might be able to use regex: \d{1,2}\s*[0-9]*\.[0-9]{2} will find splits
"""

line = 3214

lines[line][:2]  # line_type
lines[line][2]  # Result type (F=Final, P=Prelim)
lines[line][3:5]  # Length
lines[line][6:13]  # Split time
############################################

from hytek_parser import HyTekParser

file_name = "data/Meet Results-2023 Tennessee Invitational-15Nov2023-001.hy3"

# Example Usage
parser = HyTekParser()
parser.load_file(file_name)
parser.file_info
parser.athletes
print(parser.teams)
parser.teams
