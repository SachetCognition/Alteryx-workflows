# Dataiku Python Recipe: Join Filtered Dates Back to Enriched Data
#
# Mirrors: Accident-user-input.yxmd — Join Tool 12
#   - Joins the date-filtered output (from user-input-macro) back to the
#     enriched dataset on Start_Time
#
# Input datasets: accidents_enriched, accidents_date_filtered
# Output dataset: accidents_joined

import pandas as pd

try:
    import dataiku

    ENRICHED_DATASET = "accidents_enriched"
    FILTERED_DATASET = "accidents_date_filtered"
    OUTPUT_DATASET = "accidents_joined"

    enriched_ds = dataiku.Dataset(ENRICHED_DATASET)
    filtered_ds = dataiku.Dataset(FILTERED_DATASET)

    df_enriched = enriched_ds.get_dataframe()
    df_filtered = filtered_ds.get_dataframe()
except ImportError:
    dataiku = None
    df_enriched = None
    df_filtered = None


def join_filtered(
    df_enriched: pd.DataFrame, df_filtered: pd.DataFrame
) -> pd.DataFrame:
    """
    Join the date-filtered dataset back to the enriched dataset on Start_Time.

    The Alteryx Join tool (Tool 12) performs an inner join on the Start_Time
    field, combining the filtered rows with the full set of enriched columns.

    Args:
        df_enriched: Full enriched accident DataFrame.
        df_filtered: Date-filtered accident DataFrame (subset of enriched).

    Returns:
        Joined DataFrame with rows present in both datasets.
    """
    # Ensure datetime types for join key
    for frame in [df_enriched, df_filtered]:
        if not pd.api.types.is_datetime64_any_dtype(frame["Start_Time"]):
            frame["Start_Time"] = pd.to_datetime(
                frame["Start_Time"], errors="coerce"
            )

    # The filtered dataset is a subset of enriched rows.
    # Inner join on Start_Time to get matching records with all enriched columns.
    # Use a suffixed merge to handle overlapping column names.
    result = pd.merge(
        df_filtered[["Start_Time"]].drop_duplicates(),
        df_enriched,
        on="Start_Time",
        how="inner",
    )

    return result


if dataiku is not None and df_enriched is not None and df_filtered is not None:
    result = join_filtered(df_enriched, df_filtered)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
