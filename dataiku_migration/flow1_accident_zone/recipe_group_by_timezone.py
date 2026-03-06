# Dataiku Python Recipe: Group by Timezone
#
# Mirrors: Accident Workflow.yxmd — Summarize Tool 2 (line 93)
#   - CountDistinct(ID) grouped by Timezone → renamed No_of_accidents
#
# Input dataset:  US_Accidents_March23  (raw, before cleansing)
# Output dataset: accidents_by_timezone

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "US_Accidents_March23"
    OUTPUT_DATASET = "accidents_by_timezone"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def group_by_timezone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group accident records by Timezone and count distinct accident IDs.

    Mirrors Alteryx Summarize tool:
        SummarizeField field="ID" action="CountDistinct" rename="No_of_accidents"
        SummarizeField field="Timezone" action="GroupBy"

    Args:
        df: Accident DataFrame with 'ID' and 'Timezone' columns.

    Returns:
        Aggregated DataFrame with columns ['Timezone', 'No_of_accidents'].
    """
    result = (
        df.groupby("Timezone", dropna=False)["ID"]
        .nunique()
        .reset_index(name="No_of_accidents")
    )
    return result


if dataiku is not None and df is not None:
    result = group_by_timezone(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
