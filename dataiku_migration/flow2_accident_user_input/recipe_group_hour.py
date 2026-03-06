# Dataiku Python Recipe: Group by Hour
#
# Mirrors: Accident-user-input.yxmd — Summarize Tool 9 (line 228)
#   - CountDistinct(ID) grouped by Hour → renamed "Accidents Count"
#   - Followed by Sort descending (Tool 10)
#
# Input dataset:  accidents_enriched
# Output dataset: accidents_by_hour

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "accidents_enriched"
    OUTPUT_DATASET = "accidents_by_hour"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def group_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group accident records by Hour and count distinct accident IDs, then
    sort descending by count.

    Mirrors Alteryx tools:
        Summarize (Tool 9): CountDistinct(ID) as "Accidents Count", GroupBy(Hour)
        Sort (Tool 10): "Accidents Count" descending

    Args:
        df: Enriched accident DataFrame with 'ID' and 'Hour' columns.

    Returns:
        Aggregated DataFrame with columns ['Hour', 'Accidents Count'],
        sorted by 'Accidents Count' descending.
    """
    result = (
        df.groupby("Hour", dropna=False)["ID"]
        .nunique()
        .reset_index(name="Accidents Count")
    )
    result = result.sort_values("Accidents Count", ascending=False).reset_index(
        drop=True
    )
    return result


if dataiku is not None and df is not None:
    result = group_by_hour(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
