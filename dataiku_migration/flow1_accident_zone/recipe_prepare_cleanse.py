# Dataiku Python Recipe: Prepare and Cleanse Accident Data
#
# Mirrors: Accident Workflow.yxmd
#   - Filter IsNotNull(Timezone)        (Tool 5, line 167)
#   - Formula REGEX_Replace US/ prefix  (Tool 16, line 227)
#   - Cleanse macro: uppercase Timezone (Tool 17, line 257)
#
# Input dataset:  US_Accidents_March23  (46 columns, CSV)
# Output dataset: accidents_cleansed

import re

import pandas as pd

try:
    import dataiku
    from dataiku import pandasutils as pdu

    INPUT_DATASET = "US_Accidents_March23"
    OUTPUT_DATASET = "accidents_cleansed"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    # Running outside Dataiku (local dev / testing)
    dataiku = None
    df = None


def prepare_cleanse(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the three-step cleanse pipeline to the accident dataset.

    Steps:
        1. Filter out rows where Timezone is null/NaN.
        2. Strip the 'US/' prefix from Timezone using regex
           (mirrors REGEX_Replace([Timezone], "US/", " ") in Alteryx).
        3. Convert Timezone to uppercase
           (mirrors Cleanse macro with upper option).

    Args:
        df: Raw accident DataFrame with a 'Timezone' column.

    Returns:
        Cleansed DataFrame with normalised Timezone values.
    """
    # Step 1: Filter out null Timezone rows
    df = df.dropna(subset=["Timezone"]).copy()

    # Step 2: Strip 'US/' prefix — Alteryx replaces with a space, then the
    # Cleanse macro trims it. We replicate by replacing with a space first,
    # then stripping whitespace.
    df["Timezone"] = df["Timezone"].apply(
        lambda tz: re.sub(r"US/", " ", str(tz)).strip()
    )

    # Step 3: Uppercase the Timezone column
    df["Timezone"] = df["Timezone"].str.upper()

    return df


if dataiku is not None and df is not None:
    df = prepare_cleanse(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
