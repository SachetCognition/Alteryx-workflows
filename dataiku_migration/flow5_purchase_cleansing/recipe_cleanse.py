# Dataiku Python Recipe: Purchase Registration Data Cleansing
#
# Mirrors: New Workflow1.yxmd
#   - Input Data (Tool 1): Read updated1_pur_reg_2200_2300.csv
#     (98 columns, ISO-8859-1 / CodePage 28591)
#   - Cleanse Macro (Cleanse.yxmc): Built-in Alteryx cleanse macro
#     applied to all string columns:
#       * Trim whitespace (leading/trailing)
#       * Convert to uppercase
#       * Replace null/NaN with empty string
#
# Input dataset:  purchase_registration
# Output dataset: purchase_cleansed

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "purchase_registration"
    OUTPUT_DATASET = "purchase_cleansed"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def cleanse_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleansing operations to all string columns in the DataFrame.

    Mirrors the Alteryx Cleanse macro (Cleanse.yxmc) which:
        1. Strips leading and trailing whitespace from all string fields
        2. Converts all string values to uppercase
        3. Replaces null/NaN values with empty string

    This is applied to all 98 columns in the purchase registration dataset.

    Args:
        df: Raw purchase registration DataFrame (98 columns).

    Returns:
        Cleansed DataFrame with trimmed, uppercased, null-filled string columns.
    """
    df = df.copy()

    # Identify string (object) columns
    string_cols = df.select_dtypes(include=["object"]).columns.tolist()

    for col in string_cols:
        # Step 1: Replace NaN/null with empty string
        df[col] = df[col].fillna("")

        # Step 2: Convert to string type (safety), strip whitespace
        df[col] = df[col].astype(str).str.strip()

        # Step 3: Convert to uppercase
        df[col] = df[col].str.upper()

    return df


if dataiku is not None and df is not None:
    df = cleanse_dataframe(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
