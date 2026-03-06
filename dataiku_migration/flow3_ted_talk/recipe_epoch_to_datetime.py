# Dataiku Python Recipe: Convert Epoch to DateTime and Derive Date Fields
#
# Mirrors: Ted talk Workflow.yxmd
#   - Formula (Tool 4, line 87): DateTimeAdd("1970-01-01", ToNumber([film_date]), 'second')
#   - Formula (Tool 6, lines 133-137): Derive Year, Month, Month_name
#
# Input dataset:  ted_main
# Output dataset: ted_enriched

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_main"
    OUTPUT_DATASET = "ted_enriched"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def epoch_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert film_date from Unix epoch seconds to datetime and derive
    Year, Month, and Month_name columns.

    Mirrors Alteryx Formula tools:
        Tool 4: film_date = DateTimeAdd("1970-01-01", ToNumber([film_date]), 'second')
        Tool 6: Year      = DateTimeYear([film_date])
                Month     = DateTimeMonth([film_date])
                Month_name = DateTimeFormat(DateTimeParse([film_date]), "%B")

    Args:
        df: TED talk DataFrame with 'film_date' as epoch seconds (string or int).

    Returns:
        Enriched DataFrame with film_date as datetime, plus Year, Month, Month_name.
    """
    df = df.copy()

    # Convert film_date from Unix epoch seconds to datetime
    # Mirrors: DateTimeAdd("1970-01-01", ToNumber([film_date]), 'second')
    df["film_date"] = pd.to_datetime(
        pd.to_numeric(df["film_date"], errors="coerce"), unit="s", errors="coerce"
    )

    # Derive Year (as integer, matching Alteryx DateTimeYear output)
    df["Year"] = df["film_date"].dt.year

    # Derive Month (numeric, matching Alteryx DateTimeMonth output)
    df["Month"] = df["film_date"].dt.month

    # Derive Month_name (full month name, e.g., "February")
    # Mirrors: DateTimeFormat(DateTimeParse([film_date]), "%B")
    df["Month_name"] = df["film_date"].dt.strftime("%B")

    return df


if dataiku is not None and df is not None:
    df = epoch_to_datetime(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
