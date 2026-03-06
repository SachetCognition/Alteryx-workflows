# Dataiku Python Recipe: Consecutive Year Detection
#
# Mirrors: Ted talk Workflow.yxmd — MultiRowFormula Tool 28 (line 668)
#   - CreateField_Name: Consecutive
#   - Expression: ToNumber("Year", 'Yes', 'No')
#   - GroupByFields: main_speaker
#   - NumRows: 1 (looks at previous row)
#   - OtherRows: Empty (first row in group gets empty)
#
# Note: The original Alteryx formula has a known bug — it uses
#       ToNumber("Year", ...) which tries to convert the literal string "Year"
#       to a number rather than the field [Year]. We faithfully replicate
#       the intended logic: detect whether a speaker spoke in consecutive years.
#
# Input dataset:  ted_enriched
# Output dataset: ted_consecutive_years

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_consecutive_years"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def detect_consecutive_years(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each speaker, detect if they gave talks in consecutive years.

    The Alteryx MultiRowFormula (Tool 28) is configured to:
        - Group by main_speaker
        - Look at 1 previous row
        - Create field 'Consecutive'
        - First row in each group: empty
        - Subsequent rows: check year difference

    Implementation: Sort by [main_speaker, Year], compute year diff within
    each speaker group. If diff == 1, mark as 'Yes', otherwise 'No'.
    First row in each group is empty string.

    Args:
        df: Enriched TED DataFrame with 'main_speaker' and 'Year'.

    Returns:
        DataFrame with added 'Consecutive' column.
    """
    df = df.copy()

    # Ensure Year is numeric
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Sort by speaker then year (matches Alteryx groupby + row ordering)
    df = df.sort_values(["main_speaker", "Year"]).reset_index(drop=True)

    # Compute the year difference within each speaker group
    df["_year_diff"] = df.groupby("main_speaker")["Year"].diff()

    # Apply consecutive logic:
    # - First row per group (NaN diff): empty string
    # - diff == 1: "Yes" (consecutive)
    # - diff != 1: "No" (not consecutive)
    def classify_consecutive(diff_val):
        if pd.isna(diff_val):
            return ""
        if diff_val == 1:
            return "Yes"
        return "No"

    df["Consecutive"] = df["_year_diff"].apply(classify_consecutive)

    # Remove helper column
    df = df.drop(columns=["_year_diff"])

    return df


if dataiku is not None and df is not None:
    result = detect_consecutive_years(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
