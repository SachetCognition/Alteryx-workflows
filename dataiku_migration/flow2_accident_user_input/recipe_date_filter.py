# Dataiku Python Recipe: Date Range Filter
#
# Mirrors: user-input-macro.yxmc
#   - Date question (Tool 6/D6): Select Start Date
#   - Date question (Tool 8/D8): Select End Date
#   - Action (Tool 7/A7): updates Filter 3 expression → [User_input] >= StartDate
#   - Action (Tool 9/A9): updates Filter 4 expression → [User_input] < EndDate
#   - Lines 286-312: UpdateValueFormula actions on chained Filters
#
# In Dataiku, project variables replace the interactive Date question widgets.
#
# Input dataset:  accidents_enriched
# Output dataset: accidents_date_filtered

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "accidents_enriched"
    OUTPUT_DATASET = "accidents_date_filtered"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()

    # Read project variables (replaces user-input-macro date questions)
    project_vars = dataiku.get_custom_variables()
    START_DATE = project_vars.get("start_date", "2021-01-01")
    END_DATE = project_vars.get("end_date", "2022-01-01")
except ImportError:
    dataiku = None
    df = None
    START_DATE = "2021-01-01"
    END_DATE = "2022-01-01"


def date_filter(
    df: pd.DataFrame, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    Filter accident records by date range [start_date, end_date).

    Mirrors the two chained Filters in user-input-macro.yxmc:
        Filter 3: [User_input] >= StartDate
        Filter 4: [User_input] < EndDate

    Args:
        df: Enriched accident DataFrame with 'Start_Time' as datetime.
        start_date: Inclusive start date string (YYYY-MM-DD).
        end_date: Exclusive end date string (YYYY-MM-DD).

    Returns:
        Filtered DataFrame containing only rows within the date range.
    """
    df = df.copy()

    # Ensure Start_Time is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["Start_Time"]):
        df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")

    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # Apply the two-filter chain: >= start AND < end
    mask = (df["Start_Time"] >= start_dt) & (df["Start_Time"] < end_dt)
    return df[mask].copy()


if dataiku is not None and df is not None:
    df = date_filter(df, START_DATE, END_DATE)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
