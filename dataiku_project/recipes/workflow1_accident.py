"""
Dataiku Python Recipe: Accident Workflow
Replicates Alteryx workflow "Accident Workflow.yxmd"

Connection graph:
  Input(1) -> Summarize(2) + Browse(4)
  Summarize(2) -> Browse(3) + Filter(5)
  Filter(5) -> Formula(16)
  Formula(16) -> Cleanse(17)
  Cleanse(17) -> Browse(7) + BatchMacro(22)

Input:  US_Accidents_March23.csv
Output: accident_summary, accident_cleansed, per-timezone CSVs
"""

import os
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Dataiku compatibility: when running inside Dataiku, use dataiku APIs;
# when running standalone, fall back to plain pandas I/O.
# ---------------------------------------------------------------------------
try:
    import dataiku

    RUNNING_IN_DATAIKU = True
except ImportError:
    RUNNING_IN_DATAIKU = False

# Allow importing the shared cleanse utility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.cleanse import cleanse_dataframe  # noqa: E402


# ── Configuration ──────────────────────────────────────────────────────────
INPUT_CSV = os.environ.get(
    "INPUT_ACCIDENTS_CSV",
    os.path.join(os.path.dirname(__file__), "..", "..", "Datasets", "US_Accidents_March23.csv"),
)
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR",
    os.path.join(os.path.dirname(__file__), "..", "output"),
)


def run(input_path: str | None = None, output_dir: str | None = None) -> dict[str, pd.DataFrame]:
    """Execute the full Accident Workflow pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to the US_Accidents_March23.csv file.
    output_dir : str | None
        Directory where per-timezone CSVs will be written.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary of output dataset names to DataFrames.
    """
    input_path = input_path or INPUT_CSV
    output_dir = output_dir or OUTPUT_DIR

    # ── Step 1: Input ──────────────────────────────────────────────────────
    # Read CSV with all columns as string, Latin-1 encoding
    if RUNNING_IN_DATAIKU:
        df = dataiku.Dataset("US_Accidents_March23").get_dataframe()
    else:
        df = pd.read_csv(input_path, dtype=str, encoding="latin-1")

    # ── Step 2: Summarize (ToolID 2) ───────────────────────────────────────
    # Count distinct IDs per Timezone
    accident_summary = (
        df.groupby("Timezone")
        .agg(No_of_accidents=("ID", "nunique"))
        .reset_index()
    )

    # ── Step 3: Filter (ToolID 5) ──────────────────────────────────────────
    # Keep only rows where Timezone is not null/empty
    filtered = accident_summary[accident_summary["Timezone"].notna()].copy()
    filtered = filtered[filtered["Timezone"].str.strip() != ""].copy()

    # ── Step 4: Formula (ToolID 16) ────────────────────────────────────────
    # REGEX_Replace([Timezone], "US/", " ")
    filtered["Timezone"] = filtered["Timezone"].str.replace("US/", " ", regex=True)

    # ── Step 5: Cleanse (ToolID 17) ────────────────────────────────────────
    # Apply to Timezone column only: uppercase (Check Box 15=True, Drop Down 81=upper)
    # Check Box 84=False (no trimming), Check Box 117=False (no null removal)
    filtered = cleanse_dataframe(
        filtered,
        columns=["Timezone"],
        remove_whitespace=False,
        remove_nulls=False,
        uppercase=True,
    )

    accident_cleansed = filtered.copy()

    # ── Step 6: Batch Macro (ToolID 22) ────────────────────────────────────
    # For each distinct Timezone, write a CSV with '.' delimiter
    os.makedirs(output_dir, exist_ok=True)
    unique_timezones = accident_cleansed["Timezone"].dropna().unique()

    for tz in unique_timezones:
        tz_data = accident_cleansed[accident_cleansed["Timezone"] == tz]
        safe_name = tz.strip().replace(" ", "_").replace("/", "_")
        output_path = os.path.join(output_dir, f"{safe_name}_time.csv")
        tz_data.to_csv(
            output_path,
            sep=".",
            encoding="latin-1",
            index=False,
            lineterminator="\r\n",
        )

    # ── Write Dataiku output datasets ──────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        dataiku.Dataset("accident_summary").write_with_schema(accident_summary)
        dataiku.Dataset("accident_cleansed").write_with_schema(accident_cleansed)

    return {
        "accident_summary": accident_summary,
        "accident_cleansed": accident_cleansed,
    }


if __name__ == "__main__":
    outputs = run()
    print("=== accident_summary ===")
    print(outputs["accident_summary"].to_string(index=False))
    print(f"\n=== accident_cleansed ({len(outputs['accident_cleansed'])} rows) ===")
    print(outputs["accident_cleansed"].head(10).to_string(index=False))
    print(f"\nPer-timezone CSVs written to: {OUTPUT_DIR}")
