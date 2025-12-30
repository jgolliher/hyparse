import pandas as pd
from typing import List, Optional
import math


def ss_to_display(seconds_input):
    """
    Converts swimming times in seconds to display times (mm:ss.00).

    Args:
      seconds_input: The swimming time in seconds (should be convertible to float).

    Returns:
      A string representing the display time (e.g., "1:23.45", "58.32")
      or an indicator like "Invalid" or "NaN" if conversion fails.
    """
    try:
        # Attempt conversion to float, handling potential None, strings, etc.
        seconds = float(seconds_input)
    except (ValueError, TypeError, OverflowError):
        # Handle cases where input isn't a valid number or None
        return "Invalid"  # Or return None, or the original input

    # Check for NaN
    if math.isnan(seconds):
        return "NaN"  # Or handle as needed

    # Optional: Handle non-physical times like negative values
    if seconds < 0:
        return "Invalid"

    # Perform the conversion logic
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes == 0:
        # Format seconds directly when less than a minute
        return f"{remaining_seconds:.2f}"
    else:
        # Format with minutes, ensuring seconds field is zero-padded (05.2f = width 5, 2 decimals, 0-padded)
        return f"{minutes}:{remaining_seconds:05.2f}"


def rank_times(
    df: pd.DataFrame,
    group_cols: Optional[List[str]] = None,
    rank_col: str = "seed_time_ss",  # Default to numeric seed time column
    out_col: str = "rank",  # Default output column name
):
    """
    Ranks numeric values within specified groups using standard competition ranking,
    placing null (NaN) values last.

    In standard competition ranking (method='min'):
    - Ties receive the same lowest possible rank.
    - Subsequent ranks skip based on the number of tied entries
      (e.g., ranks 1, 2, 2, 4 indicate a tie for 2nd place).

    Args:
        df (pd.DataFrame): Pandas DataFrame containing the data.
        group_cols (Optional[List[str]]): List of column names to group by
            before ranking. Defaults to ['event_no'] if None.
        rank_col (str): The column whose numeric values will be ranked.
            Defaults to 'seed_time_ss'. It's crucial this column exists
            and contains numeric data (or NaNs).
        out_col (str): Name of the new column to store the calculated ranks.
                       Defaults to 'rank'.

    Returns:
        pd.DataFrame: The original DataFrame with the new rank column added.

    Raises:
        KeyError: If any column specified in group_cols or rank_col
                  does not exist in the DataFrame.
        TypeError: If the data in rank_col is not numeric and cannot be
                   ranked by pandas.
    """
    # Set default grouping columns if none were provided
    if group_cols is None:
        group_cols = ["event_no"]

    # --- Input Validation ---
    # Check if grouping columns exist
    missing_group_cols = [col for col in group_cols if col not in df.columns]
    if missing_group_cols:
        raise KeyError(f"Grouping columns not found in DataFrame: {missing_group_cols}")

    # Check if ranking column exists
    if rank_col not in df.columns:
        raise KeyError(f"Ranking column '{rank_col}' not found in DataFrame.")

    # Validate that the ranking column is numeric (skip check for empty DataFrames)
    if len(df) > 0 and not pd.api.types.is_numeric_dtype(df[rank_col]):
        raise TypeError(
            f"Failed to rank column '{rank_col}'. Is it numeric? "
            f"Column has dtype: {df[rank_col].dtype}"
        )

    # --- Perform Ranking ---
    try:
        df[out_col] = df.groupby(group_cols, observed=True, dropna=False)[rank_col].rank(
            method="min",  # Use 'min' for standard competition ranking
            ascending=True,  # Lower values (faster times) get lower ranks (1 is best)
            na_option="bottom",  # Place NaN values at the end (highest rank number)
        )
    except TypeError as e:
        raise TypeError(
            f"Failed to rank column '{rank_col}'. Is it numeric? Original error: {e}"
        ) from e
    except Exception as e:
        # Catch other potential errors during groupby or rank
        raise RuntimeError(f"An unexpected error occurred during ranking: {e}") from e

    return df
