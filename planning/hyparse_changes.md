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
- [x] Tests run against every file in `data/hy3` and `data/other`.

## Remaining

- [ ] **`.hy3` writer** (entries): required for dual meets because only `.hy3` carries heat/lane. Acceptance: reproduce both sample entry `.HY3` files byte-for-byte from their parsed model. Fields we don't model yet (E1 col 91 `C`, D1 col 101 `*`, D1 col 85–87, B2 bits) must round-trip, so the writer may need to keep the raw line or model those fields.
- [ ] **`.cl2` (SDIF v3) reader + writer**: A0, B1, C1, D0, D3, E0, F0, Z0. Implement from the published spec. Acceptance: reproduce both sample `.CL2` files.
- [ ] Split times (G1 lines) and DQ descriptions (H1) in results, if the app wants them.
- [ ] Tag a release the app can pin (`v0.4.0`), and consider PyPI later.

## Unknown fields worth asking about

| Where | Value | Guess |
|---|---|---|
| E1 col 91 | `C` on some entry seeds | Custom (coach-typed) seed? Or corrected time? |
| E2 col 12 | `R`, `S`, `F`, `D` (`Q` = DQ confirmed) | Scratch / no-show / false start / DNF variants |
| E2 col 15 | `X` on 47 result rows | Exhibition swim? |
| D1 col 101 | `*` | Non-US citizen marker? (seen on CAN/NZL/AUT athletes) |
| `.ev3` header 6 | `YO` / `LO` | Course + "O" (open?) |
| `.ev3` event field 4 | `1` / `2` | Number of rounds (`F` → 1, `P` → 2) |
