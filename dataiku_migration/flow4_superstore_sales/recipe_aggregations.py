# Dataiku Python Recipe: Multi-Step Aggregations
#
# Mirrors: New Workflow2.yxmd — Tools 7, 9, 10, 13, 20
#   - Summarize (Tool 7): Sum(Sales) → Sum_Sales (total)
#   - Sort (Tool 9): Sales descending
#   - Sample (Tool 10): First 5 rows (top 5 by Sales)
#   - Summarize (Tool 13): Min(Sales) from top 5 → Min_Sum_Sales
#   - Summarize (Tool 20): GroupBy Sub-Category, Sum(Sales)
#
# Input dataset:  superstore_2016
# Output datasets: superstore_total_sales, superstore_top5,
#                  superstore_min_sales, superstore_subcategory_sales

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "superstore_2016"
    OUTPUT_TOTAL = "superstore_total_sales"
    OUTPUT_TOP5 = "superstore_top5"
    OUTPUT_MIN = "superstore_min_sales"
    OUTPUT_SUBCAT = "superstore_subcategory_sales"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def compute_total_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the total sum of Sales.

    Mirrors Alteryx Summarize (Tool 7): Sum(Sales) → Sum_Sales.

    Args:
        df: Filtered 2016 orders DataFrame.

    Returns:
        Single-row DataFrame with column 'Sum_Sales'.
    """
    total = pd.DataFrame({"Sum_Sales": [df["Sales"].sum()]})
    return total


def compute_top5(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort by Sales descending and take the top 5 rows.

    Mirrors Alteryx tools:
        Sort (Tool 9): Sales descending
        Sample (Tool 10): First 5 rows

    Args:
        df: Filtered 2016 orders DataFrame.

    Returns:
        Top 5 rows by Sales value.
    """
    result = df.sort_values("Sales", ascending=False).head(5).copy()
    return result.reset_index(drop=True)


def compute_min_sales(top5_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the minimum Sales value from the top 5 rows.

    Mirrors Alteryx Summarize (Tool 13): Min(Sales) → Min_Sum_Sales.

    Args:
        top5_df: Top 5 orders DataFrame.

    Returns:
        Single-row DataFrame with column 'Min_Sum_Sales'.
    """
    min_val = pd.DataFrame({"Min_Sum_Sales": [top5_df["Sales"].min()]})
    return min_val


def compute_subcategory_sales(top5_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group the top 5 by Sub-Category and sum Sales.

    Mirrors Alteryx Summarize (Tool 20):
        GroupBy(Sub-Category), Sum(Sales) → Sum_Sales

    Args:
        top5_df: Top 5 orders DataFrame.

    Returns:
        Aggregated DataFrame with columns ['Sub-Category', 'Sum_Sales'].
    """
    result = (
        top5_df.groupby("Sub-Category")["Sales"]
        .sum()
        .reset_index(name="Sum_Sales")
    )
    return result


if dataiku is not None and df is not None:
    # Ensure Sales is numeric
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    total_df = compute_total_sales(df)
    top5_df = compute_top5(df)
    min_df = compute_min_sales(top5_df)
    subcat_df = compute_subcategory_sales(top5_df)

    dataiku.Dataset(OUTPUT_TOTAL).write_with_schema(total_df)
    dataiku.Dataset(OUTPUT_TOP5).write_with_schema(top5_df)
    dataiku.Dataset(OUTPUT_MIN).write_with_schema(min_df)
    dataiku.Dataset(OUTPUT_SUBCAT).write_with_schema(subcat_df)
