"""
Reusable cleanse utility that replicates Alteryx Cleanse macro (Cleanse.yxmc) behavior.

Alteryx Cleanse macro settings mapped:
  - Check Box (84)=True  -> Remove leading/trailing whitespace
  - Check Box (117)=True -> Remove null/empty rows
  - Check Box (15)=True  -> Modify case
  - Drop Down (81)=upper -> Uppercase
"""

import pandas as pd


def cleanse_dataframe(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    remove_whitespace: bool = False,
    remove_nulls: bool = False,
    uppercase: bool = False,
) -> pd.DataFrame:
    """Apply Alteryx-style cleanse operations to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to cleanse.
    columns : list[str] | None
        Columns to apply cleanse operations on. If ``None``, all columns
        are processed.
    remove_whitespace : bool
        Strip leading/trailing whitespace from string columns
        (Alteryx Check Box 84).
    remove_nulls : bool
        Drop rows where **all** specified columns are null or empty string
        (Alteryx Check Box 117).
    uppercase : bool
        Convert string columns to UPPERCASE (Alteryx Check Box 15 +
        Drop Down 81 = upper).

    Returns
    -------
    pd.DataFrame
        Cleansed copy of the input DataFrame.
    """
    result = df.copy()

    if columns is None:
        columns = list(result.columns)

    # Identify which of the selected columns are string (object) dtype
    str_cols = [c for c in columns if c in result.columns and result[c].dtype == object]

    # 1. Remove leading/trailing whitespace (Check Box 84)
    if remove_whitespace:
        for col in str_cols:
            result[col] = result[col].str.strip()

    # 2. Remove null/empty rows (Check Box 117)
    #    Drop rows where ALL specified columns are null or empty string
    if remove_nulls:
        mask = pd.DataFrame()
        for col in columns:
            if col in result.columns:
                if result[col].dtype == object:
                    mask[col] = result[col].isna() | (result[col].str.strip() == "")
                else:
                    mask[col] = result[col].isna()
        if not mask.empty:
            all_null = mask.all(axis=1)
            result = result[~all_null].reset_index(drop=True)

    # 3. Modify case -> uppercase (Check Box 15 + Drop Down 81)
    if uppercase:
        # Re-evaluate str_cols after potential whitespace stripping
        str_cols = [
            c for c in columns if c in result.columns and result[c].dtype == object
        ]
        for col in str_cols:
            result[col] = result[col].str.upper()

    return result
