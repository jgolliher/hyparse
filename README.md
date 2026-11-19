# hyparse

[![CI](https://github.com/jgolliher/hyparse/actions/workflows/ci.yml/badge.svg)](https://github.com/jgolliher/hyparse/actions/workflows/ci.yml)
![Coverage](https://raw.githubusercontent.com/jgolliher/hyparse/badges/coverage.svg)

Read HyTek swim meet files into typed Python objects, and write `.hy3` entries files.

| Format | What it is | Who sends it | Read | Write |
|---|---|---|---|---|
| `.hy3` (type 02) | Meet entries, incl. pre-assigned heat/lane for dual meets | Team → meet host | ✅ | ✅ |
| `.hy3` (type 07) | Meet results | Meet host → teams | ✅ | — |
| `.ev3` | Event list + entry limits | Meet host → teams | ✅ | — |
| `.hyv` | Event list (simpler) | Meet host → teams | ✅ | — |
| `.cl2` (SDIF v3) | Meet entries | Team → meet host | planned | planned |

hyparse has no database code. It turns files into objects, and entry objects back into files.

## Install

```bash
pip install "hyparse @ git+https://github.com/jgolliher/hyparse"
pip install "hyparse[pandas] @ git+https://github.com/jgolliher/hyparse"   # DataFrame helpers
```

Python 3.10+.

## Usage

```python
from hyparse import read_hy3, read_ev3, read_hyv

# Results or entries (.hy3) — the file says which: hy3.kind == "results" | "entries"
hy3 = read_hy3("data/results/Meet Results-2024 Tennessee vs LSU-27Jan2024-001.hy3")
hy3.meet            # Meet(name, facility, start_date, course, ...)
hy3.teams           # [Team(code, name, lsc, contact)]
hy3.athletes        # [Athlete(team_code, team_athlete_id, names, registration_id, birth_date, ...)]
hy3.results         # [IndividualResult(event, time, heat, lane, place, reaction_time, ...)]
hy3.relay_results   # [RelayResult(..., legs=[RelayLeg(leg, team_athlete_id)], reaction_times)]
hy3.results[0].splits  # [Split(number=2, distance=50, time=24.9), ...] cumulative; relays too
hy3.relay_results[0].splits[0].leg  # relay splits also carry the leg (1-4) they fall in
hy3.issues          # problems found while parsing (empty when the file is clean)

entries = read_hy3("data/entries/TENN-SE-Entries-2023 Tennessee vs Louisville-12Oct2023-001.HY3")
entries.entries[0]        # IndividualEntry(seed_time, seed_course, exhibition, seeding=Seeding(round, heat, lane))
entries.relay_entries[0]  # RelayEntry(relay_letter, legs, seeding)

# Event files
events = read_ev3("data/events/Meet Events-2026 Tennessee Invitational-17Nov2026-002.ev3")
events.meet.entry_limits  # EntryLimits(total=9, individual=5, relay=4)
events.events[0]          # Event(number, gender, distance, stroke, is_relay, round, session, day, ...)
read_hyv("...hyv")        # same shape; no entry limits or sessions

# Write an entries file (A1 type 02): build or edit an Hy3File, then
from hyparse import write_hy3
text = write_hy3(entries, "out.hy3")  # CRLF lines, Latin-1, checksums filled in
```

Reading a Team Manager entry file and writing it back gives the same bytes (checked for both
sample files). Columns hyparse can't explain are either kept on the model (`Athlete.flag`,
`IndividualEntry.seed_flag`) or written as Team Manager always writes them; see the
`hyparse/hy3_writer.py` docstring.

Conventions:

- Times are seconds as `float` (`None` = no time). `format_time(112.42)` → `"1:52.42"`.
- Splits are cumulative. `Split.number` is Meet Manager's raw split number, whose scale varies
  between meets; `Split.distance` is derived as `event distance × number ÷ last number`.
  `time=None` means no touch was recorded.
- Dates are `datetime.date`.
- Athletes are identified within a file by `(team_code, team_athlete_id)`. Use `hy3.athlete(team, id)`.
- Genders are normalized to `F` / `M` / `X`. Stroke codes: `A` free, `B` back, `C` breast, `D` fly,
  `E` medley/IM, `F` 1m, `G` 3m, `H` platform. Diving rows have `distance=None`.
- `read_hy3(path, strict=True)` raises on the first problem instead of collecting `issues`.
  Event readers always raise `FileFormatError` (naming the line) on unexpected structure.

### DataFrames / CSV

```python
from hyparse.dataframes import results_df, relay_results_df, entries_df, splits_df
results_df(hy3).to_csv("results.csv", index=False)
splits_df(hy3)  # one row per split; join to results_df on team_code, team_athlete_id, event_number, round
```

or from the command line:

```bash
python main.py "data/results/Meet Results-2024 Tennessee vs LSU-27Jan2024-001.hy3" out/
```

## Development

```bash
uv sync --extra dev
uv run pytest
```

Tests run against the real sample files in `data/` (`results/`, `entries/`, `events/`). Format notes are in `resources/`.
