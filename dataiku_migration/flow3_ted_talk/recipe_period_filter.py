# Dataiku Python Recipe: Period Filter (MTD / YTD / WTD)
#
# Mirrors: TD-input-macro.yxmc
#   - DropDown question (lines 315-318): manual values "MTD\nYTD\nWTD"
#   - Action tool updates Filter expression via UpdateValue
#   - Filter evaluates [Type] = "MTD" / "YTD" / "WTD" against date data
#
# In Dataiku, the DropDown question is replaced by a project variable 'period_type'.
# The filter logic computes date ranges relative to the current date.
#
# Input dataset:  ted_enriched
# Output dataset: ted_period_filtered

from datetime import datetime, timedelta

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_period_filtered"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()

    # Read project variable (replaces TD-input-macro DropDown)
    project_vars = dataiku.get_custom_variables()
    PERIOD_TYPE = project_vars.get("period_type", "MTD")
except ImportError:
    dataiku = None
    df = None
    PERIOD_TYPE = "MTD"


def period_filter(
    df: pd.DataFrame,
    period_type: str,
    reference_date: datetime = None,
) -> pd.DataFrame:
    """
    Filter data based on period type relative to a reference date.

    Mirrors the TD-input-macro.yxmc which provides three filter modes:
        - MTD (Month-to-Date): from first of current month to reference date
        - YTD (Year-to-Date): from first of current year to reference date
        - WTD (Week-to-Date): from Monday of current week to reference date

    Args:
        df: Enriched TED DataFrame with 'film_date' as datetime.
        period_type: One of "MTD", "YTD", "WTD".
        reference_date: The reference date (defaults to today).

    Returns:
        Filtered DataFrame containing only rows within the specified period.
    """
    df = df.copy()

    if reference_date is None:
        reference_date = datetime.now()

    # Ensure film_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["film_date"]):
        df["film_date"] = pd.to_datetime(df["film_date"], errors="coerce")

    period_type = period_type.upper().strip()

    if period_type == "MTD":
        # Month-to-Date: first of current month to reference date
        start_date = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period_type == "YTD":
        # Year-to-Date: first of current year to reference date
        start_date = reference_date.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    elif period_type == "WTD":
        # Week-to-Date: Monday of current week to reference date
        days_since_monday = reference_date.weekday()
        start_date = (reference_date - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        raise ValueError(
            f"Invalid period_type '{period_type}'. Must be 'MTD', 'YTD', or 'WTD'."
        )

    # Apply date range filter
    mask = (df["film_date"] >= pd.Timestamp(start_date)) & (
        df["film_date"] <= pd.Timestamp(reference_date)
    )
    result = df[mask].copy()

    return result


if dataiku is not None and df is not None:
    result = period_filter(df, PERIOD_TYPE)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
