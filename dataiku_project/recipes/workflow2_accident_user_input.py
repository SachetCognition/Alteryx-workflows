"""
Dataiku Python Recipe: Accident User-Input Workflow
Replicates Alteryx workflow "Accident-user-input.yxmd"

Connection graph:
  Input(1) -> DateTime(5) -> Select(6) -> Formula(3) ->
    [Browse(4), Summarize1(7), Summarize2(9), Join(13)Left]
  UserInputMacro(12) -> Join(13)Right
  Summarize1(7) -> Browse(8)
  Summarize2(9) -> Sort(10) -> Browse(11)
  Join(13) -> Browse(14)

Input:  US_Accidents_March23.csv
Output: accident_by_day_type, accident_by_hour, accident_date_filtered
"""

import os
import sys

import numpy as np
import pandas as pd

try:
    import dataiku

    RUNNING_IN_DATAIKU = True
except ImportError:
    RUNNING_IN_DATAIKU = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Configuration ──────────────────────────────────────────────────────────
INPUT_CSV = os.environ.get(
    "INPUT_ACCIDENTS_CSV",
    os.path.join(os.path.dirname(__file__), "..", "..", "Datasets", "US_Accidents_March23.csv"),
)

# User-input macro parameters (defaults from workflow XML)
START_DATE = os.environ.get("START_DATE", "2023-01-01")
END_DATE = os.environ.get("END_DATE", "2023-01-31")


def run(
    input_path: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Execute the full Accident User-Input Workflow pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to the US_Accidents_March23.csv file.
    start_date : str | None
        Start date for user-input filter (YYYY-MM-DD).
    end_date : str | None
        End date for user-input filter (YYYY-MM-DD).

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary of output dataset names to DataFrames.
    """
    input_path = input_path or INPUT_CSV
    start_date = start_date or START_DATE
    end_date = end_date or END_DATE

    # ── Step 1: Input ──────────────────────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        df = dataiku.Dataset("US_Accidents_March23").get_dataframe()
    else:
        df = pd.read_csv(input_path, dtype=str, encoding="latin-1")

    # ── Step 2: DateTime (ToolID 5) ────────────────────────────────────────
    # Parse Start_Time string to datetime
    df["DateTime_Out"] = pd.to_datetime(df["Start_Time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    # ── Step 3: Select (ToolID 6) ──────────────────────────────────────────
    # Drop original Start_Time, rename DateTime_Out -> Start_Time
    df = df.drop(columns=["Start_Time"]).rename(columns={"DateTime_Out": "Start_Time"})

    # ── Step 4: Formula (ToolID 3) ─────────────────────────────────────────
    # Day = weekday name
    df["Day"] = df["Start_Time"].dt.strftime("%A")

    # Day_type: Weekday / Weekend / Data issue
    weekdays = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
    weekends = {"Saturday", "Sunday"}
    df["Day_type"] = np.where(
        df["Day"].isin(weekdays),
        "Weekday",
        np.where(df["Day"].isin(weekends), "Weekend", "Data issue"),
    )

    # Hour = zero-padded hour string
    df["Hour"] = df["Start_Time"].dt.strftime("%H")

    # EOM = last day of month of Start_Time (normalized to midnight)
    df["EOM"] = (df["Start_Time"] + pd.offsets.MonthEnd(0)).dt.normalize()

    # EOPM = end of previous month (day before first of current month)
    df["EOPM"] = df["Start_Time"].dt.to_period("M").dt.to_timestamp() - pd.Timedelta(days=1)

    # ── Step 5: Summarize 1 (ToolID 7) ─────────────────────────────────────
    # Count distinct IDs by Day_type
    accident_by_day_type = (
        df.groupby("Day_type")
        .agg(Accidents=("ID", "nunique"))
        .reset_index()
    )

    # ── Step 6: Summarize 2 (ToolID 9) ─────────────────────────────────────
    # Count distinct IDs by Hour
    accident_by_hour = (
        df.groupby("Hour")
        .agg(**{"Accidents Count": ("ID", "nunique")})
        .reset_index()
    )

    # ── Step 7: Sort (ToolID 10) ───────────────────────────────────────────
    # Sort by Accidents Count descending
    accident_by_hour = accident_by_hour.sort_values(
        "Accidents Count", ascending=False
    ).reset_index(drop=True)

    # ── Step 8: User-Input Macro (ToolID 12) + Join (ToolID 13) ───────────
    # Filter data to user-specified date range
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    accident_date_filtered = df[
        (df["Start_Time"] >= start_dt) & (df["Start_Time"] < end_dt)
    ].copy()
    accident_date_filtered = accident_date_filtered.reset_index(drop=True)

    # ── Write Dataiku output datasets ──────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        dataiku.Dataset("accident_by_day_type").write_with_schema(accident_by_day_type)
        dataiku.Dataset("accident_by_hour").write_with_schema(accident_by_hour)
        dataiku.Dataset("accident_date_filtered").write_with_schema(accident_date_filtered)

    return {
        "accident_by_day_type": accident_by_day_type,
        "accident_by_hour": accident_by_hour,
        "accident_date_filtered": accident_date_filtered,
    }


if __name__ == "__main__":
    outputs = run()
    print("=== accident_by_day_type ===")
    print(outputs["accident_by_day_type"].to_string(index=False))
    print("\n=== accident_by_hour (top 10) ===")
    print(outputs["accident_by_hour"].head(10).to_string(index=False))
    print(f"\n=== accident_date_filtered ({len(outputs['accident_date_filtered'])} rows) ===")
    print(outputs["accident_date_filtered"].head(5).to_string(index=False))
