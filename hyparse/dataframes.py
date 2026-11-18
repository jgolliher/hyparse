"""Optional pandas helpers: flat tables of a parsed .hy3 file for analysis or CSV export.

Requires ``pip install hyparse[pandas]``.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from hyparse._values import format_time
from hyparse.codes import STROKES
from hyparse.models import Athlete, Hy3File

if TYPE_CHECKING:
    import pandas as pd


def _pandas():
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover
        raise ImportError("DataFrame helpers need pandas: pip install hyparse[pandas]") from exc
    return pd


def _with_athlete(hy3: Hy3File, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_key: Dict[Tuple[Any, Any], Athlete] = {
        (a.team_code, a.team_athlete_id): a for a in hy3.athletes
    }
    for r in records:
        a = by_key.get((r.get("team_code"), r.get("team_athlete_id")))
        r["last_name"] = a.last_name if a else None
        r["first_name"] = a.first_name if a else None
        r["registration_id"] = a.registration_id if a else None
    return records


def _decorate(hy3: Hy3File, records: List[Dict[str, Any]]) -> "pd.DataFrame":
    for r in records:
        r["meet_name"] = hy3.meet.name
        r["meet_start_date"] = hy3.meet.start_date
        r["stroke_name"] = STROKES.get(r.get("stroke") or "")
        r["seed_display"] = format_time(r.get("seed_time"))
        if "time" in r:
            r["time_display"] = format_time(r.get("time"))
    df: "pd.DataFrame" = _pandas().DataFrame(records)
    return df


def results_df(hy3: Hy3File) -> "pd.DataFrame":
    rows = _with_athlete(hy3, [r.model_dump() for r in hy3.results])
    return _decorate(hy3, rows)


def entries_df(hy3: Hy3File) -> "pd.DataFrame":
    rows = []
    for e in hy3.entries:
        row = e.model_dump(exclude={"seeding"})
        seeding = e.seeding
        row["seed_round"] = seeding.round if seeding else None
        row["seed_heat"] = seeding.heat if seeding else None
        row["seed_lane"] = seeding.lane if seeding else None
        rows.append(row)
    return _decorate(hy3, _with_athlete(hy3, rows))


def relay_results_df(hy3: Hy3File) -> "pd.DataFrame":
    rows = []
    for r in hy3.relay_results:
        row = r.model_dump(exclude={"legs", "reaction_times"})
        for leg in r.legs:
            row[f"leg_{leg.leg}_athlete_id"] = leg.team_athlete_id
        for i, reaction in enumerate(r.reaction_times, start=1):
            row[f"leg_{i}_reaction_time"] = reaction
        rows.append(row)
    return _decorate(hy3, rows)
