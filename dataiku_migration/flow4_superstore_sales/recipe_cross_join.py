# Dataiku Python Recipe: Cross-Join Sub-Category Sums with Min Sales
#
# Mirrors: New Workflow2.yxmd — AppendFields Tool 26 (lines 575-599)
#   - AppendFields performs a Cartesian (cross) join
#   - Source: superstore_subcategory_sales (multiple rows)
#   - Target: superstore_min_sales (single row / scalar)
#   - Result: each sub-category row gets the Min_Sum_Sales value appended
#
# Input datasets: superstore_subcategory_sales, superstore_min_sales
# Output dataset: superstore_cross_joined

import pandas as pd

try:
    import dataiku

    SUBCAT_DATASET = "superstore_subcategory_sales"
    MIN_DATASET = "superstore_min_sales"
    OUTPUT_DATASET = "superstore_cross_joined"

    subcat_ds = dataiku.Dataset(SUBCAT_DATASET)
    min_ds = dataiku.Dataset(MIN_DATASET)

    df_subcat = subcat_ds.get_dataframe()
    df_min = min_ds.get_dataframe()
except ImportError:
    dataiku = None
    df_subcat = None
    df_min = None


def cross_join(
    df_subcategory: pd.DataFrame, df_min_sales: pd.DataFrame
) -> pd.DataFrame:
    """
    Cross-join the sub-category aggregation with the min sales scalar.

    Mirrors Alteryx AppendFields (Tool 26):
        Appends all fields from the target (min sales) to every row of
        the source (sub-category sums). Since the target is a single row,
        this effectively broadcasts the Min_Sum_Sales value.

    Args:
        df_subcategory: Sub-category sales DataFrame with ['Sub-Category', 'Sum_Sales'].
        df_min_sales: Single-row DataFrame with ['Min_Sum_Sales'].

    Returns:
        DataFrame with columns ['Sub-Category', 'Sum_Sales', 'Min_Sum_Sales'].
    """
    # Extract the scalar Min_Sum_Sales value
    min_sales_value = df_min_sales["Min_Sum_Sales"].iloc[0]

    # Assign to every row (equivalent to Cartesian join with single-row table)
    result = df_subcategory.copy()
    result["Min_Sum_Sales"] = min_sales_value

    return result


if dataiku is not None and df_subcat is not None and df_min is not None:
    result = cross_join(df_subcat, df_min)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
