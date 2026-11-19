
**Note**: Need a different name from Team Manager...

Context Notes
* Use a local Postgres database for now; will offload to a web-based Postgres server in the future. So make it easy to change the connection type but assume that Postgres will be used.
* Start simple with meet entries and holding meet results from HyTek files. We have parsing code, in Python, to parse through `.hy3` files and extract the information. So, we'll need to design an ETL process to go from `.hy3` files into Postgres.
* Web UI
	* First step should likely be building a process to ETL meet results *and* entry files (more on entry files later). The second step will be building a web UI around digesting the data and making it easy for coaches to do entries.
	* The UI will likely grow with reporting and other dashboards for visualizing and digesting results. We won't design all of that right now but consider it as we build out the database and UI. Make it easy to add to!
	* The web UI will allow users to login. The first users will be the Tennessee Swimming & Diving coaches and myself. My thought is to think towards the future, so users should be tied to teams where each team can have a different "look" in the app. Like, Tennessee would use Tennessee Orange (Hex: FF8200) and Smokey Gray (Hex: 4B4B4B) along with the Power T logo.
	* Users will need to register via email. I'm not sure how to do passwords tbh. Storing them in the database feels... wrong. But maybe there's a package to ensure that's safe? Open to thoughts here.
	* I will need some kind of admin view to clean up duplicates in the database. One of the problems I want to solve early is the resolution of duplicate athletes. Meet result files *should* have unique identifiers (USA Swimming ID) attached to them but that may not always be the case and it's possible an athlete has two USA Swimming IDs. So the database schema needs to support multiple unique identifiers for an athlete that resolve to a canonical, internal identifier (UID?).
* Meet entries
	* For meet entries, I don't currently have an ETL process written for that. Pretty much everything that comes from HyTek is a text file with some kind of specific formatting. I can provide an example event file along with what events they are tied to in a CSV format.
	* We also need to be able to export meet entries in a format to be digested by the meet software. Again, these are just plain text files in a specific format so I can provide an entry file and a CSV for a few examples.
* The normal flow for meets is this (this basically all happens over email lol)
	1. Meet manager creates event lists and sends to teams
	2. Team loads the event file to their Team Manager and does entries
	3. Team sends the event file back to the meet manager
	4. Meet manager loads the entry list. The meet runs.
	5. Meet manager sends result file to teams
	6. Teams load results back into Team Manager
* So, I'm not sure exactly what we need to do in the database to handle that flow. But we want teams/coaches to be able to do meet entries without results and then import results for the same meet. And we don't want to create duplicate meets (or at least make it easy to resolve)
* I'll provide as many files as I can along with descriptions but always feel free to ask questions.

## .ev3 format

**File**: `Meet Events-2026 Tennessee Invitational-17Nov2026-002.ev3`

Event list format. Appears to be semi-colon separated.

The first line contains information on the meet:

| Field Name           | Example Value                    | Notes                                                         |
| -------------------- | -------------------------------- | ------------------------------------------------------------- |
| meet_name            | 2026 Tennessee Invitational      |                                                               |
| facility_name        | Allan Jones Aquatic Center       |                                                               |
| start_date           | 11/17/2026                       |                                                               |
| end_date             | 11/20/2026                       |                                                               |
| age_up_date          | 11/17/2026                       |                                                               |
| ?                    | YO                               |                                                               |
| ?                    | 0                                |                                                               |
| ?                    | 0                                |                                                               |
| ?                    | 0                                |                                                               |
| created_by           | Created by Hy-Tek's MEET MANAGER |                                                               |
| license_name         | Tennessee Aquatics               |                                                               |
| meet_manager_version | 8.0G                             |                                                               |
| create_date          | 11/02/2026                       |                                                               |
| ?                    | 3                                |                                                               |
| ?                    | 0                                |                                                               |
| entry_date           | 09/01/2026                       | Tells Team Manager the earliest date allowed for entry times. |
| ?                    | 0                                |                                                               |
| ?                    | 9                                |                                                               |
| ?                    | 5                                |                                                               |
| ?                    | 4                                |                                                               |
| ?                    | 1                                |                                                               |
| ?                    | C                                |                                                               |
| ?                    | 11/16/2026                       |                                                               |
| facility_address     | 2200 Any Holt Drive              |                                                               |
| facility_city        | Knoxville                        |                                                               |
| facility_state       | TN                               |                                                               |
| facility_zip         | 37919                            |                                                               |
| base_country         | USA                              |                                                               |
| host_lsc             | US                               |                                                               |
| ?                    | N                                |                                                               |
| ?                    | N                                |                                                               |
| ?                    | 10/15/2026                       |                                                               |
| ?                    | 92182                            |                                                               |

Subsequent lines contain events. I'll provide a few examples but note that because this is just for one meet, it's possible there's some slight variation we at the very least need to catch and error so we can resolve our process in the future.

Line 2 (i.e., the first event).
`1;1;F;1;I;W;0;109;1650;A;0;;;N;0;;;;;;;1;1;1;05:00PM;Y;0;0;0;0*>`. Confused on the first two numbers since here they are always the same and appear to just be the event number...

| Field              | Value  | Notes                                                                                                                                                    |
| ------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| event_number       | 1      | Unsure what the difference is between the first and second field?                                                                                        |
| event_number (?)   | 1      | Unsure what the difference is between the first and second field?                                                                                        |
| round              | F      | P = Prelims; F = Finals                                                                                                                                  |
| ?                  | 1      | Unsure                                                                                                                                                   |
| gender             | W      |                                                                                                                                                          |
| low_age            | 0      | Used for age-group swimming. 0-109 is considered "Open/Senior"                                                                                           |
| high_age           | 109    | Used for age-group swimming. 0-109 is considered "Open/Senior"                                                                                           |
| distance           | 1650   | Distance of swim                                                                                                                                         |
| stroke_code        | A      | In HyTek:<br>A = Freestyle<br>B = Backstroke<br>C = Breaststroke<br>D = Butterfly<br>E = Medley<br>F = 1m Diving<br>G = 3m Diving<br>H = Platform Diving |
| num_dives          | 0      | Number of dives, if the event is diving                                                                                                                  |
| session_number     | 1      | The session number the event is taking place in                                                                                                          |
| session_order      | 1      | The order in the session the event is taking lace in                                                                                                     |
| day                | 1      | The day of the meet the session and event is taking place in                                                                                             |
| session_start_time | 5:00PM | What local time the session starts in                                                                                                                    |
| course             | Y      | Y = Yards, S = SCM, L = LCM                                                                                                                              |
| ?                  | 0      |                                                                                                                                                          |
| ?                  | 0      |                                                                                                                                                          |
| ?                  | 0      |                                                                                                                                                          |
| num_relay_swimmers | 4      | Number of swimmers in the relay                                                                                                                          |

## .hy3 format

This file is what teams/coaches send back to the meet manager. It contains their entries they plan to swim.

The format is similar to the meet results format but doesn't contain results. So, might be beneficial to look at that ETL process. Like the result file, this is a fixed-width text file where each line starts with a two letter code (e.g., `A1`).

A1: Information on the file type
B1: Meet information
B2: ?
C1: Team information
C2: Head coach information
C3: ?
D1: Athlete entry
E1: Athlete event entry

D1 example:

`D1F  989Rathwell            Regan                                    0F064B807C5E4A     02112004 22GS*          CAN             22`

`D1M 1051Nunziata            Gabe                                    T80D5915517E74B     02022007 19SO                           51
`
`D1F 1078Buff                Mia                 Mia                 A9A9A9D3ED8604E     03032008 18FR                           00`

| field_name      | Value          | Notes                                                                               |
| --------------- | -------------- | ----------------------------------------------------------------------------------- |
| gender          | F              | D1M, the F is the gender                                                            |
| tm_athlete_id   | 1078           | Athlete ID within the Team Manager database. Specific to the team's software.       |
| last_name       | Buff           | Athlete last name                                                                   |
| first_name      | Mia            | Athlete first name                                                                  |
| preferred_name  | Mia            | Athlete preferred name                                                              |
| middle_initial  | A              | Right before the beginning of their unique identifier/registration ID               |
| registration_id | 9A9A9D3ED8604E | Usually this is the USA Swimming ID for the swimmer and is their unique identifier. |
| dob             | 03032008       | MMDDYYYY                                                                            |
| age             | 18             | Age of the swimmer                                                                  |
| year            | FR             | Class year                                                                          |

I think the lines are literally the same as the result file format but obviously double check that lol
