"""DataFrame transformation classes for .hy3 parsed data.

This module provides classes to transform parsed swim meet data
into structured Pandas DataFrames with proper formatting and rankings.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from hyparse.objects import MeetInfo, Athlete, IndividualResult, RelayResult
from hyparse.utils import ss_to_display, rank_times

logger = logging.getLogger(__name__)


class DataFrameTransformer:
    """Base class for transforming parsed data into DataFrames."""

    # Stroke code mappings
    STROKE_CODES = {
        "A": "Free",
        "B": "Back",
        "C": "Breast",
        "D": "Fly",
        "E": "Medley",
        "F": "1m",
        "G": "3m",
        "H": "10m",
    }

    def __init__(self, meet_info: Optional[MeetInfo] = None):
        """Initialize transformer with optional meet info.

        Args:
            meet_info: MeetInfo object containing meet metadata.
        """
        self.meet_info = meet_info

    def _add_meet_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds common meet information columns to DataFrame.

        Args:
            df: DataFrame to augment with meet info.

        Returns:
            DataFrame with meet info columns added.
        """
        if self.meet_info:
            df["meet_name"] = self.meet_info.meet_name
            df["facility_name"] = self.meet_info.facility_name
            df["meet_start_date"] = self.meet_info.meet_start_date
            df["meet_end_date"] = self.meet_info.meet_end_date
        return df

    def _add_stroke_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Maps stroke codes to readable stroke names.

        Args:
            df: DataFrame with stroke_code column.

        Returns:
            DataFrame with stroke column added.
        """
        if "stroke_code" in df.columns:
            df["stroke"] = df["stroke_code"].map(self.STROKE_CODES).fillna("Unknown")
        return df

    def _format_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts time columns to numeric and adds display columns.

        Args:
            df: DataFrame with time columns.

        Returns:
            DataFrame with formatted time columns.
        """
        time_cols = ["time", "seed_time", "backup_time_1", "backup_time_2"]

        # Convert to numeric
        for col in time_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Add display columns
        if "time" in df.columns:
            df["display_time"] = df["time"].apply(ss_to_display)
        if "seed_time" in df.columns:
            df["display_seed_time"] = df["seed_time"].apply(ss_to_display)
        if "backup_time_1" in df.columns:
            df["display_backup_time_1"] = df["backup_time_1"].apply(ss_to_display)
        if "backup_time_2" in df.columns:
            df["display_backup_time_2"] = df["backup_time_2"].apply(ss_to_display)

        return df

    def _ensure_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Ensures all specified columns exist in DataFrame.

        Args:
            df: DataFrame to check.
            columns: List of column names that should exist.

        Returns:
            DataFrame with all specified columns (adds None for missing).
        """
        for col in columns:
            if col not in df.columns:
                df[col] = None
        return df

    def _reorder_columns(
        self, df: pd.DataFrame, column_order: List[str]
    ) -> pd.DataFrame:
        """Reorders DataFrame columns to match specified order.

        Args:
            df: DataFrame to reorder.
            column_order: Desired column order.

        Returns:
            DataFrame with columns in specified order (only existing columns).
        """
        existing_cols = [col for col in column_order if col in df.columns]
        return df[existing_cols]


class IndividualResultTransformer(DataFrameTransformer):
    """Transforms individual swim results into DataFrames."""

    _COLUMN_ORDER = [
        "meet_name",
        "facility_name",
        "meet_start_date",
        "meet_end_date",
        "mm_athlete_id",
        "usas_id",
        "first_name",
        "last_name",
        "gender",
        "team",
        "event_no",
        "stroke",
        "distance",
        "seed_time",
        "round",
        "time",
        "course",
        "heat",
        "lane",
        "heat_place",
        "overall_place",
        "points",
        "time_code",
        "backup_time_1",
        "backup_time_2",
        "reaction_time",
        "i_r_flag",
        "seed_rank",
        "display_time",
        "display_seed_time",
        "display_backup_time_1",
        "display_backup_time_2",
    ]

    def transform(
        self,
        results: List[IndividualResult],
        athletes: Dict[str, Athlete],
    ) -> pd.DataFrame:
        """Transforms individual results into a DataFrame.

        Args:
            results: List of IndividualResult objects.
            athletes: Dictionary mapping mm_id to Athlete objects.

        Returns:
            DataFrame with formatted individual results.
        """
        if not results:
            return pd.DataFrame(columns=self._COLUMN_ORDER)

        # Convert results to dict and create DataFrame
        results_data = [res.model_dump() for res in results]
        df_results = pd.DataFrame(results_data)

        # Prepare athlete data for merging
        if athletes:
            athlete_data = [ath.model_dump() for ath in athletes.values()]
            df_athletes = pd.DataFrame(athlete_data)[
                ["mm_id", "usas_id", "first_name", "last_name", "gender", "team"]
            ]
            df_athletes = df_athletes.rename(columns={"mm_id": "mm_athlete_id"})

            # Merge results with athlete info
            df = pd.merge(df_results, df_athletes, on="mm_athlete_id", how="left")
        else:
            df = df_results

        # Add stroke names
        df = self._add_stroke_names(df)

        # Calculate seed rankings
        df = self._calculate_seed_ranks(df)

        # Format time columns
        df = self._format_time_columns(df)

        # Add meet info
        df = self._add_meet_info(df)

        # Ensure all columns exist and reorder
        df = self._ensure_columns(df, self._COLUMN_ORDER)
        df = self._reorder_columns(df, self._COLUMN_ORDER)

        return df

    def _calculate_seed_ranks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates seed rankings within each event.

        Args:
            df: DataFrame with seed_time, event_no, and mm_athlete_id columns.

        Returns:
            DataFrame with seed_rank column added.
        """
        required_cols = ["seed_time", "event_no", "mm_athlete_id"]
        if all(col in df.columns for col in required_cols):
            # Create ranked dataframe, dropping duplicate entries
            ranked_times = rank_times(
                df=df.drop_duplicates(subset=["event_no", "mm_athlete_id"]).copy(),
                rank_col="seed_time",
                out_col="seed_rank",
            )
            # Merge back to full dataframe
            df = df.merge(
                ranked_times[["event_no", "mm_athlete_id", "seed_rank"]],
                on=["event_no", "mm_athlete_id"],
                how="left",
            )
        else:
            df["seed_rank"] = np.nan

        return df


class RelayResultTransformer(DataFrameTransformer):
    """Transforms relay swim results into DataFrames."""

    _BASE_COLUMN_ORDER = [
        "meet_name",
        "facility_name",
        "meet_start_date",
        "meet_end_date",
        "gender",
        "team_abbr",
        "relay_team",
        "event_no",
        "stroke",
        "distance",
        "seed_time",
        "round",
        "time",
        "time_code",
        "course",
        "heat",
        "lane",
        "heat_place",
        "overall_place",
        "points",
        "backup_time_1",
        "backup_time_2",
        "backup_time_3",
        "touchpad_time",
        "i_r_flag",
    ]

    def transform(self, results: List[RelayResult]) -> pd.DataFrame:
        """Transforms relay results into a DataFrame.

        Args:
            results: List of RelayResult objects.

        Returns:
            DataFrame with formatted relay results.
        """
        if not results:
            # Return empty DataFrame with swimmer columns
            dynamic_cols = self._get_dynamic_columns(max_swimmers=4)
            all_cols = self._BASE_COLUMN_ORDER + dynamic_cols + ["seed_rank"]
            return pd.DataFrame(columns=all_cols)

        # Transform relay results to flat dictionaries
        transformed_results = [self._transform_relay(res) for res in results]
        df = pd.DataFrame(transformed_results)

        # Add stroke names
        df = self._add_stroke_names(df)

        # Calculate seed rankings
        df = self._calculate_seed_ranks(df)

        # Format time columns
        df = self._format_time_columns(df)

        # Add meet info
        df = self._add_meet_info(df)

        # Build final column order with dynamic columns
        dynamic_cols = self._get_dynamic_columns_from_df(df)
        final_cols = (
            self._BASE_COLUMN_ORDER
            + dynamic_cols
            + ["seed_rank", "display_time", "display_seed_time"]
        )

        # Ensure all columns exist and reorder
        df = self._ensure_columns(df, final_cols)
        df = self._reorder_columns(df, final_cols)

        return df

    def _transform_relay(self, relay_result: RelayResult) -> Dict:
        """Transforms a RelayResult object into a flat dictionary.

        Args:
            relay_result: RelayResult object to transform.

        Returns:
            Flattened dictionary suitable for DataFrame row.
        """
        data = relay_result.model_dump()
        athletes = data.pop("relay_athletes", [])
        reactions = data.pop("reaction_times", [])

        # Add swimmer and reaction time columns
        max_legs = 4  # Standard relay has 4 swimmers
        for i in range(max_legs):
            data[f"swimmer_{i+1}_mm_id"] = athletes[i] if i < len(athletes) else None
            data[f"reaction_time_{i+1}"] = reactions[i] if i < len(reactions) else None

        return data

    def _calculate_seed_ranks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates seed rankings within each relay event.

        Args:
            df: DataFrame with seed_time, event_no, team_abbr, relay_team columns.

        Returns:
            DataFrame with seed_rank column added.
        """
        required_cols = ["seed_time", "event_no", "team_abbr", "relay_team"]
        if all(col in df.columns for col in required_cols):
            # Create ranked dataframe, dropping duplicate entries
            ranked_times = rank_times(
                df=df.drop_duplicates(
                    subset=["event_no", "team_abbr", "relay_team"]
                ).copy(),
                rank_col="seed_time",
                out_col="seed_rank",
            )
            # Merge back to full dataframe
            df = df.merge(
                ranked_times[["event_no", "team_abbr", "relay_team", "seed_rank"]],
                on=["event_no", "team_abbr", "relay_team"],
                how="left",
            )
        else:
            df["seed_rank"] = np.nan

        return df

    def _get_dynamic_columns(self, max_swimmers: int = 4) -> List[str]:
        """Generates dynamic column names for swimmers and reaction times.

        Args:
            max_swimmers: Maximum number of swimmers per relay.

        Returns:
            List of column names.
        """
        cols = []
        for i in range(1, max_swimmers + 1):
            cols.append(f"swimmer_{i}_mm_id")
            cols.append(f"reaction_time_{i}")
        return cols

    def _get_dynamic_columns_from_df(self, df: pd.DataFrame) -> List[str]:
        """Extracts existing dynamic columns from DataFrame.

        Args:
            df: DataFrame to check.

        Returns:
            List of existing swimmer/reaction columns in order.
        """
        cols = []
        all_cols = set(df.columns)
        for i in range(1, 5):  # Check up to 4 swimmers
            swimmer_col = f"swimmer_{i}_mm_id"
            reaction_col = f"reaction_time_{i}"
            if swimmer_col in all_cols:
                cols.append(swimmer_col)
            if reaction_col in all_cols:
                cols.append(reaction_col)
        return cols
