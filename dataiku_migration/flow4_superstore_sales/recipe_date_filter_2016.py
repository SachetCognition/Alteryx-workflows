# Dataiku Python Recipe: Filter Orders to 2016
#
# Mirrors: New Workflow2.yxmd
#   - Input Data (Tool 1): Read Sample - Superstore.xls, Orders sheet
#   - AutoField (Tool 3): Auto-type fields
#   - Filter (Tool 5, lines 135-166): Order Date between 2016-01-01 and 2017-01-01
#
# Input dataset:  superstore_orders
# Output dataset: superstore_2016

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "superstore_orders"
    OUTPUT_DATASET = "superstore_2016"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def date_filter_2016(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter orders to the year 2016.

    Mirrors Alteryx Filter tool (Tool 5):
        ToDate([Order Date]) >= "2016-01-01" AND
        ToDate([Order Date]) <= "2017-01-01"

    Args:
        df: Superstore orders DataFrame with 'Order Date' column.

    Returns:
        Filtered DataFrame containing only 2016 orders.
    """
    df = df.copy()

    # Ensure Order Date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    # Apply date range filter matching Alteryx: >= 2016-01-01 AND <= 2017-01-01
    start_date = pd.Timestamp("2016-01-01")
    end_date = pd.Timestamp("2017-01-01")

    mask = (df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)
    return df[mask].copy()


if dataiku is not None and df is not None:
    df = date_filter_2016(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
