# Dataiku Python Recipe: Top 5 Talks by Views per Year
#
# Mirrors: Ted talk Workflow.yxmd — Tools 8 → 10 → 11
#   - Sort (Tool 8): views descending
#   - Sample (Tool 10): First 5 rows grouped by Year
#   - Sort (Tool 11): Year descending
#
# Input dataset:  ted_enriched
# Output dataset: ted_top5_views_per_year

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_top5_views_per_year"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def top5_views_per_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each year, select the top 5 talks by views, then sort by year descending.

    Mirrors Alteryx tool chain:
        Sort (Tool 8): views descending
        Sample (Tool 10): First 5 per Year group
        Sort (Tool 11): Year descending

    Args:
        df: Enriched TED DataFrame with 'views' and 'Year' columns.

    Returns:
        DataFrame with top 5 talks per year, sorted by Year descending.
    """
    df = df.copy()

    # Ensure views is numeric for proper sorting
    df["views"] = pd.to_numeric(df["views"], errors="coerce")

    # Sort by views descending, then take top 5 per Year group
    result = (
        df.sort_values("views", ascending=False)
        .groupby("Year", group_keys=False)
        .head(5)
    )

    # Final sort by Year descending
    result = result.sort_values("Year", ascending=False).reset_index(drop=True)

    return result


if dataiku is not None and df is not None:
    result = top5_views_per_year(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
