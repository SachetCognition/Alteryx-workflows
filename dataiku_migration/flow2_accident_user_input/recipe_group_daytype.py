# Dataiku Python Recipe: Group by Day_type
#
# Mirrors: Accident-user-input.yxmd — Summarize Tool 7 (line 180)
#   - CountDistinct(ID) grouped by Day_type → renamed Accidents
#
# Input dataset:  accidents_enriched
# Output dataset: accidents_by_daytype

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "accidents_enriched"
    OUTPUT_DATASET = "accidents_by_daytype"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def group_by_daytype(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group accident records by Day_type and count distinct accident IDs.

    Mirrors Alteryx Summarize tool (Tool 7):
        SummarizeField field="ID" action="CountDistinct" rename="Accidents"
        SummarizeField field="Day_type" action="GroupBy"

    Args:
        df: Enriched accident DataFrame with 'ID' and 'Day_type' columns.

    Returns:
        Aggregated DataFrame with columns ['Day_type', 'Accidents'].
    """
    result = (
        df.groupby("Day_type", dropna=False)["ID"]
        .nunique()
        .reset_index(name="Accidents")
    )
    return result


if dataiku is not None and df is not None:
    result = group_by_daytype(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
