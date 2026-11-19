# Deckside — Context and Plan

> Name: **Deckside** (chosen 2026-11-18; availability of domain/GitHub org not yet checked).
> Status: planning. This doc moves to the new app repo once it exists.
> Source notes: `planning/webapp_context.md`, Team Manager screenshots in `planning/screenshots/`, sample files in `data/entries/`, `data/events/` and `data/results/`.

## 1. What we're building

A web app where college swim coaches:

1. Import meet **event files** sent by a meet host.
2. Do **meet entries** in a modern UI, by event or by athlete.
3. **Export entries** to a file the host's Meet Manager can load.
4. Import **meet results** into the same meet.
5. Later: reporting and dashboards built on results history.

It replaces the email + Team Manager loop:

```
Host: create events ──► .ev3/.hyv ──► Team: do entries ──► .hy3/.cl2 ──► Host: run meet ──► results .hy3 ──► Team: load results
```

First users: Tennessee Swimming & Diving coaches plus an admin (John).

### Scope

| In v1 | Later, but leave room |
|---|---|
| College (NCAA) swimming | Age-group/club swimming |
| Swimming events | Diving (1m, 3m, platform) |
| Tennessee as the only team | Many teams, each with its own branding |
| Local Postgres | Hosted Postgres |
| Entries + results import, entries export | Reports, dashboards, analytics |

## 2. Architecture

Two repos:

| Repo | Responsibility | Has a DB? |
|---|---|---|
| **hyparse** (existing) | Read and write HyTek and SDIF files. Returns format-neutral Python objects. | No |
| **New app** | Django web app: database, ETL, identity resolution, meet matching, UI, auth, export. Depends on hyparse (see below). | Yes |

See `hyparse_changes.md` for what the library needs.

### Using hyparse from Deckside

**For now: a local, editable path dependency.** Both repos are still changing, so Deckside uses the hyparse checkout on disk. An edit in hyparse shows up in Deckside right away, with no release or reinstall. Keep the two repos side by side:

```
Repos/
  hyparse/
  deckside/
```

In `deckside/pyproject.toml`:

```toml
[project]
dependencies = [
    "hyparse",
    # ...
]

[tool.uv.sources]
hyparse = { path = "../hyparse", editable = true }
```

Then `uv sync` in `deckside/`. Don't add pandas: Deckside uses hyparse's models directly, not `hyparse[pandas]`.

**Later: pin a release.** Before Deckside runs anywhere but this machine (CI or a server), push hyparse, tag a release and switch the source to the tag:

```toml
[tool.uv.sources]
hyparse = { git = "https://github.com/jgolliher/hyparse", tag = "v0.4.0" }
```

Until then, Deckside's CI can't install hyparse, so its CI either checks out both repos or waits for the tag.

### Stack

- **Python + Django.** The parser and ETL are already Python, and Django ships auth, an admin site, migrations and an ORM.
- **Postgres.** Connection comes only from a `DATABASE_URL` environment variable (`dj-database-url`), so moving to hosted Postgres is a config change.
- **UI:** server-rendered Django templates + **HTMX**. If the entries grid or relay builder needs heavy client-side interaction, add a small JS component (Alpine or React) for that screen only, rather than a separate SPA.
- **Auth:** `django-allauth` for email registration, verification and password reset. Passwords are stored as salted **argon2** hashes (Django's password hashers), never in plain text. A managed auth provider is the alternative if we ever want SSO.
- **Charts (later):** a JS charting library inside templates.
- **Tooling:** `uv`, `pytest`, `ruff`/`black`, GitHub Actions (match hyparse).

## 3. Domain model

Sketch only. Names and columns will change while building.

### Organizations and people

| Table | Purpose / key columns |
|---|---|
| `organization_type` / enum | `college`, `club` |
| `governing_body` | NCAA, a conference, a USA Swimming LSC. Generic, not a `conference` column. |
| `team` | name, abbreviation, organization type, governing bodies, **theme** (primary/secondary colour, logo). Tennessee: `#FF8200` / `#4B4B4B`, Power T. |
| `season` | Team-scoped, with start/end dates (college and club calendars differ). |
| `user` | Django user, email login. |
| `team_membership` | user ↔ team, with a role (`admin`, `coach`, `viewer`). |
| `athlete` | Internal canonical ID, best-known first/last/preferred name, date of birth, gender. Nothing source-specific. |
| `athlete_identifier` | Many per athlete: `(type, value, team?)`. Types: `usas_id`, `team_manager_id` (unique only within a team), `ncaa_id`, later others. |
| `roster_membership` | athlete ↔ team ↔ season, with class year (college only; blank for club). Handles transfers. |

### Meets

| Table | Purpose / key columns |
|---|---|
| `facility` | name, address, city, state, zip, country. |
| `meet` | name, facility, start/end dates, **age-up date**, course, entry-time cutoff date, meet type (dual, invitational, championship), host. |
| `meet_session` | session number, day, start time. |
| `event` | meet, event number, session + order, gender, **low/high age** (0–109 = open), distance, stroke code, **discipline** (`swim`/`dive`), individual vs relay, relay swimmer count, round (prelim/final/timed final). |
| `meet_team` | Teams in a meet (for dual meets: the opponent). |

### Entries

| Table | Purpose / key columns |
|---|---|
| `entry` | event, athlete, team, **seed time + course**, seed source (`best_time` / `custom` / `converted`), the result the seed came from, flags **exhibition / alternate / bonus**, **heat / lane** (nullable; dual meets), status (draft/exported). |
| `relay_entry` | event, team, relay letter (A, B, C…), seed, exhibition, heat/lane. |
| `relay_leg` | relay entry, leg 1–4, plus alternate slots 5–8, athlete. |

### Results

| Table | Purpose / key columns |
|---|---|
| `result` | event, athlete, round, time + course, time code (DQ, NS, SCR…), heat, lane, place, points, reaction time. Links to its `entry` when one exists. |
| `relay_result` / `relay_result_leg` | Same idea for relays. Leg splits and reaction times. |
| `split` | Later (G lines in hy3). |
| `dive_result` | Later. Separate table so `result` never needs a nullable "score" column. |

### Import tracking

| Table | Purpose |
|---|---|
| `source_file` | Every uploaded file stored raw: filename, format, **SHA-256 hash**, uploader, timestamp. Re-uploading the same hash is a no-op. |
| `import_run` | One parse/load attempt: status, counts, warnings, errors. |
| `review_item` | Things a human must decide: uncertain meet match, possible duplicate athlete. |
| `merge_log` | Every athlete/meet merge, with enough detail to undo it. |

## 4. Key design problems

### 4.1 One meet across its lifecycle

A meet is created by whichever file shows up first: usually the event file, sometimes a results file for a meet we never entered.

On every import:

1. Look for an existing meet matching **name + start date + course** (normalized; facility as a tiebreaker).
2. Confident match → attach to it.
3. Weak or multiple matches → stop and create a `review_item` ("Same meet as *2026 Tennessee Invitational, 11/17/2026*?"). **Never silently create a duplicate.**
4. Events match on event number + gender + distance + stroke + round. Mismatches (e.g., a revised event file) are listed for review.
5. Results attach to entries where possible, which gives seed-vs-final, scratches and "entered but didn't swim" for free.

### 4.2 Athlete identity

On import, resolve each athlete in order:

1. Exact match on a strong identifier (`usas_id`, or `team_manager_id` within the same team).
2. First/last name + date of birth + team.
3. Otherwise create a new athlete and flag it as a **possible duplicate** in the review queue.

Admin merge: move all identifiers, roster rows, entries and results to the surviving athlete, and write a `merge_log` row so it can be undone.

Known wrinkle: the same swimmer's registration ID is **14 characters in `.hy3`** (`0F064B807C5E4A`) but **12 in `.cl2`** (`0F064B807C5E`). Decide which form is canonical, or normalize to the 12-character prefix for matching.

### 4.3 Seed times

- **Best time** = fastest result in the event's course, on or after the meet's entry-time cutoff date (`.ev3` field "entry date").
- If none, optionally use a **converted** time from another course (flag it, as Team Manager does).
- Coaches can override with a **custom** time.
- Show where the seed came from (date + meet), matching what coaches see in Team Manager today.

## 5. Entries UI

From the Team Manager screenshots, coaches need:

- **By event:** pick an event, tick athletes; see best time, where it came from, exhibition/alternate/bonus, heat/lane.
- **By athlete:** pick an athlete, tick events; see current entry counts (individual and relay).
- **Relays:** A/B/C relays, legs 1–4 + alternates 5–8, a "find best relay" helper (optionally using non-lead-off splits), relay heat/lane.
- **Filters:** gender, class year, group, "only athletes already in the meet", time standards.

Proposed design: **one entries matrix** with athletes as rows and events as columns. A cell click toggles the entry and shows the seed. Row totals warn when an athlete is over the event limit. A side panel handles flags, custom seeds and heat/lane. Relays get their own builder panel. "By event" and "by athlete" become filtered views of the same matrix.

Rules to support: max individual events per athlete, max relays, max total, bonus events not counting toward limits.

**Where limits come from:** the `.ev3` header, fields 19–21 = **total / individual / relay** (confirmed: Louisville dual meet `5;3;2`, Invitational `9;5;4`). `.hyv` has no limits. Store limits on the `meet`, prefill them from the `.ev3` when present, and let a coach edit them. Limits are **warnings**, not hard blocks.

## 6. Tenancy, auth and theming

- Every query is scoped to the user's current team. One user can belong to several teams.
- Team theme (colours + logo) is loaded per request and applied through CSS variables.
- Roles: site admin (dedupe, merges, all teams), team admin, coach, viewer.
- Email registration with verification. Invites from a team admin, so random sign-ups can't join a team.

## 7. ETL pipeline

```
upload ─► store raw (hash) ─► hyparse parse ─► staging objects ─► match meet ─► resolve athletes ─► load ─► report
                                                                       │                │
                                                                       └── review_item ◄┘
```

- Idempotent: the same file hash never loads twice. A re-import of a changed file goes through matching again.
- Diving events are **skipped with a warning**, not an error, until diving is in scope.
- Unknown line types or field values → warning recorded on the `import_run`, never a crash. Unexpected structure (the `.ev3` "slight variation" concern) → clear error naming the line.
- Runs in-process at first; move to a task queue (Celery/RQ/Django tasks) when files get large.

## 8. Export

Meet Manager accepts either format, but they don't carry the same data:

- **Heat/lane only travels in `.hy3`.** In the Tennessee vs Louisville dual-meet entries, `.hy3` has an `E2`/`F2` line after each pre-seeded entry with round, heat and lane (e.g. `E2P                   2  4` = prelim, heat 2, lane 4) and no time. The matching `.cl2` from Team Manager has no heat/lane anywhere.
- So: **`.hy3` export is required for dual meets**, and `.cl2` is fine for invitationals.
- `.hy3` lines end with a 2-digit checksum; the algorithm is known and verified against every sample line (`hyparse.hy3_checksum`). `.cl2` has a published spec, but its trailing per-record characters (`N21`, `N98`) still need checking.
- Build order: `.hy3` writer first (covers every meet type), `.cl2` second.
- Acceptance tests: export the sample entries and diff against both pairs of files in `data/entries/` (Invitational 2026 and Louisville 2023).

## 9. File format catalog

| Format | Example | Direction | Contents | hyparse status |
|---|---|---|---|---|
| `.ev3` | `Meet Events-2026 Tennessee Invitational-…-002.ev3` | Host → team | Meet header + events, `;`-separated, lines end `*>` | Read ✅ |
| `.hyv` | `Meet Events-…-002.hyv` | Host → team | Simpler event list, `;`-separated. Team Manager loads either this or `.ev3`, so support both. | Read ✅ |
| `.hy3` entries | `TENN-SE-Entries-…-001.HY3` | Team → host | Fixed width; A1, B1, B2, C1–C3, D1, E1, F1, F3, plus **E2/F2 with heat/lane and no time** when pre-seeded (dual meets) | Read ✅ (write planned) |
| `.cl2` (SDIF v3) | `TENN-SE-Entries-…-001.CL2` | Team → host | Fixed width; A0, B1, C1, D0, D3, E0, F0, Z0 | Not supported |
| `.hy3` results | `data/results/*.hy3` | Host → team | Entries lines + E2/F2 results (+ G splits, not parsed yet) | Read ✅ |

`.ev3` field notes (corrections to `webapp_context.md`):
- Field 5 is `I`/`R` (individual/relay). Gender is field 6.
- Field 4 seems to follow the round (`F` → 1, `P` → 2).
- For diving, distance is `0` and the board is the stroke code (F = 1m, G = 3m, H = platform). The field after the stroke code is the number of dives.
- The last field is the relay swimmer count (4 on relays, 0 otherwise).

## 10. Leaving room for later

**Club swimming:** organization type and governing body are generic; seasons are their own table; class year lives on roster membership; events keep age bands and ages are computed from date of birth + the meet's age-up date.

**Diving:** `event.discipline`, stroke codes F/G/H already mapped, separate `dive_result` table, importer skips dives with a warning.

**Reporting:** results are normalized (one row per swim with course and time code), so dashboards can query them directly. Add read-only reporting views/materialized views later instead of changing core tables.

## 11. Phases

| Phase | Goal | Done when |
|---|---|---|
| 0. hyparse update | Library reads entries, events and SDIF | Parses every file in `data/` into the neutral model; tests pass |
| 1. App skeleton | Django project, Postgres via `DATABASE_URL`, auth, teams, theming | A Tennessee coach can register by invite, log in and see the orange/grey theme |
| 2. Results ETL | Load `.hy3` results with athlete resolution and meet matching | All `data/results` files load; re-import is a no-op; duplicates land in the review queue |
| 3. Admin cleanup | Review queue + athlete/meet merge with undo | Admin can merge two athletes and undo it |
| 4. Events import + entries UI | Load `.ev3`/`.hyv`, entries matrix, relay builder, seeds | A coach can enter the 2026 Tennessee Invitational in the app |
| 5. Entries export | `.hy3` (then `.cl2`) export, including heat/lane | Export matches both sample entry pairs closely enough that Meet Manager accepts it |
| 6. Results ↔ entries | Results import attaches to the entered meet | Importing the meet's results links to the existing entries, no duplicate meet |
| 7. Reporting | First dashboards | TBD |

## 12. Open questions

1. ~~**Name**~~ → **Deckside**. Other ideas considered (none checked for existing swim products, domains or trademarks yet):
   - **Seedline**: seed times + lane lines; about entries but not limited to them.
   - **Deckside** ✅ chosen.
   - **Taper**: every swimmer knows the word; short. Probably taken somewhere.
   - **Startblock** / **Blocks**: where every swim begins.
   - **Lane Nine**: a nod to the outside lane; quirky.
   - **Splitwater**: splits + water; leans toward results/analytics.
2. ~~Which event file do teams load?~~ Either `.ev3` or `.hyv`; support both.
3. ~~Where do heat/lane live?~~ `.hy3` E2/F2 lines only; not in `.cl2`. See §8.
4. Canonical registration ID form (14 vs 12 characters).
5. ~~Confirm the `.ev3` entry-limit fields~~ Confirmed: fields 19–21 = total / individual / relay.
6. Is there a roster source of truth (e.g., a Team Manager export) to seed athletes from?
7. Who resolves duplicates: only the site admin, or team admins too?
8. Should the app ever **create** event files (for meets Tennessee hosts), or only import them?
9. Do we keep every version of a meet's files (revised event files, re-sent results)? Current plan: yes, raw + hash.
10. Remaining unknown `.ev3` / `.hy3` fields (B2, the `?` columns).
