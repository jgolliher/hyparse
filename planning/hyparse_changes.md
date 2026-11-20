# hyparse — Changes Needed for Deckside

hyparse stays a standalone, database-free library that **reads and writes** HyTek and SDIF files. The app (see `app_plan.md`) owns everything database-related.

## Done (2026-11-18, v0.4.0 rewrite)

- [x] Rewrote the package around one format-neutral model (`hyparse/models.py`): `Meet`, `Team` + `Contact`, `Athlete`, `Event`, `IndividualEntry`, `IndividualResult`, `RelayEntry`, `RelayResult`, `RelayLeg`, `Seeding`, `EntryLimits`. Typed values: times in seconds (`float`), `date`s, ints, bools.
- [x] `read_hy3()` reads **entries and results**; `Hy3File.kind` comes from the A1 file type (02 entries, 07 results).
- [x] Column specs re-derived from every sample file and checked against `resources/` notes (`hyparse/hy3.py`).
- [x] Entry files: seed time is in **slot 2** (cols 52–58, course 59); slot 1 is `0`. The old parser read slot 1, so it would have shown no seed for entry files.
- [x] Pre-seeded heat/lane: E2/F2 with a **blank time** become `entry.seeding` (round, heat, lane), not results.
- [x] Exhibition flag (`X`, col 83) on E1/F1.
- [x] C2 (contact name/address) and C3 (email) lines.
- [x] F3 reads all 8 slots and the explicit leg number. NCAA results do use legs 5+.
- [x] E2/F2 heat (20–22) and lane (23–25) fixed. The old spec cut 2-digit lanes.
- [x] Diving rows: `stroke` F/G/H → `discipline == "dive"`, `distance=None` (that field holds the dive count; `lane` holds dive order).
- [x] `mm_id` / `mm_athlete_id` → `team_athlete_id`, scoped by `team_code`.
- [x] **`.ev3` reader** incl. entry limits (header fields 19–21 = total / individual / relay, confirmed on both samples).
- [x] **`.hyv` reader**. Stroke digits 1–5 = A–E, 6 = diving with the board in the distance field (1 → 1m, 3 → 3m, 2 → platform). Its events match the `.ev3` exactly for both sample meets.
- [x] Checksum is known and verified on every sample line (`hy3_checksum`). Strict mode raises; default collects `issues`.
- [x] pandas is now optional (`hyparse[pandas]`, `hyparse.dataframes`). Python 3.10+.
- [x] Tests run against every file in `data/`.

## Done (2026-11-20, records files)

- [x] **`.rec` reader + writer** (`hyparse/rec.py`): Meet Manager records files. Fixed 120-byte rows with no line breaks; a header row (list name, course, file date) then one row per record. Times are 4-byte Microsoft Binary Format singles. Writing any of the six samples back gives the same bytes.
- [x] `RecordFile.current()`: Meet Manager repeats rows and keeps broken records, so this returns the fastest per event (ties kept).
- [x] `*.rec` marked binary in `.gitattributes`: the time bytes can contain CR/LF.

## Remaining

- [x] **`.hy3` writer** (entries), `write_hy3()` in `hyparse/hy3_writer.py`. Both sample entry files are reproduced byte for byte from their parsed model. New model fields to make that possible: `Team.team_type` (C1 119–121, `COL`), `Team.registration` (C2 108–111, `USS`), `Athlete.flag` (D1 111, `X`, meaning unknown), `IndividualEntry.seed_flag` (E1 91, `C`, maybe corrected/converted), and `num_dives` on entries and results (the dive count in the distance column). Derived or constant on write: D1 101 `*` (citizenship set and not USA), B2 fee/`O`, the E1/F1 fee and seed slot 1, F1 col 11–12, F3 slot `F`. Not yet checked: that Meet Manager imports a file hyparse wrote from scratch.
- [ ] **`.cl2` (SDIF v3) reader + writer**: A0, B1, C1, D0, D3, E0, F0, Z0. Implement from the published spec. Acceptance: reproduce both sample `.CL2` files.
- [x] Split times (G1 lines): `IndividualResult.splits` / `RelayResult.splits`, `splits_df`.
- [ ] DQ descriptions (H1) in results, if the app wants them.
- [ ] Tag a release the app can pin (`v0.4.0`), and consider PyPI later. Not urgent: Deckside starts with a local editable path dependency on this checkout (see `app_plan.md` §2). Needed before Deckside's CI or a deploy.

## Unknown fields worth asking about

| Where | Value | Guess |
|---|---|---|
| E1 col 91 | `C` on some entry seeds | Custom (coach-typed) seed? Or corrected time? |
| E2 col 12 | `R`, `S`, `F`, `D` (`Q` = DQ confirmed) | Scratch / no-show / false start / DNF variants |
| E2 col 15 | `X` on 47 result rows | Exhibition swim? |
| D1 col 101 | `*` | Non-US citizen marker? (seen on CAN/NZL/AUT athletes) |
| `.rec` record cols 108-110 | `A20` on every row | Age group or record type? Needs a file with age-group records |
| `.rec` header cols 35-50 | `20WIN-MM038.0Gh` | Program and version that wrote the file |
| `.ev3` header 6 | `YO` / `LO` | Course + "O" (open?) |
| `.ev3` event field 4 | `1` / `2` | Number of rounds (`F` → 1, `P` → 2) |
