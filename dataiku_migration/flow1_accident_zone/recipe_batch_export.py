# Dataiku Python Recipe: Batch Export by Timezone
#
# Mirrors: accident-macro.yxmc (Batch Macro)
#   - Control Parameter iterates over timezone values
#   - Action tools update Filter expression ([Zone] = "Eastern") and output file path
#   - Output Data tool writes one CSV per timezone to managed folder
#
# Reference: accident-macro.yxmc
#   - Lines 92-111: MultiFile output config (MultiFileField=Zone)
#   - Lines 248-271: Action/UpdateValue logic for Filter and File path
#   - TextInput data rows: Eastern, Central, Mountain, Pacific
#
# Input dataset:  accidents_cleansed
# Output:         CSV files in managed folder 'accident_zone_exports'

import os

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "accidents_cleansed"
    MANAGED_FOLDER = "accident_zone_exports"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
    folder = dataiku.Folder(MANAGED_FOLDER)
except ImportError:
    dataiku = None
    df = None
    folder = None

# The four timezone values from the Batch Macro's TextInput (Tool 2, lines 33-46)
TIMEZONE_VALUES = ["EASTERN", "CENTRAL", "MOUNTAIN", "PACIFIC"]


def batch_export(df: pd.DataFrame, output_dir: str = None, folder_handle=None):
    """
    Loop over unique timezone values, filter the cleansed dataset, and write
    one CSV per timezone.

    This replaces the Alteryx Batch Macro which:
        1. Receives a Control Parameter value (timezone string)
        2. Updates the Filter expression to [Zone] = "{timezone}"
        3. Updates the Output Data file path to include the timezone name
        4. Writes matching rows to that file

    Args:
        df: Cleansed accident DataFrame with uppercase 'Timezone' column.
        output_dir: Local directory path for writing CSVs (used in testing).
        folder_handle: Dataiku Folder handle for writing CSVs.

    Returns:
        dict mapping timezone name to number of rows written.
    """
    row_counts = {}

    for tz in TIMEZONE_VALUES:
        filtered = df[df["Timezone"] == tz].copy()
        filename = f"{tz}_accidents.csv"
        csv_content = filtered.to_csv(index=False)

        if folder_handle is not None:
            # Write to Dataiku managed folder
            folder_handle.upload_stream(
                filename, csv_content.encode("utf-8")
            )
        elif output_dir is not None:
            # Write to local filesystem (for testing)
            filepath = os.path.join(output_dir, filename)
            filtered.to_csv(filepath, index=False)

        row_counts[tz] = len(filtered)

    return row_counts


if dataiku is not None and df is not None:
    batch_export(df, folder_handle=folder)
