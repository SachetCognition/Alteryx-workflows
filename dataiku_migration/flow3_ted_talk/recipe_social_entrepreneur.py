# Dataiku Python Recipe: Social Entrepreneur Filter
#
# Mirrors: Ted talk Workflow.yxmd — RegEx Tool 32 (line ~635)
#   - Pattern: .*social entrepreneur.*  (case insensitive)
#   - Applied to: speaker_occupation
#   - Creates boolean match column
#
# Input dataset:  ted_enriched
# Output dataset: ted_social_entrepreneurs

import re

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_social_entrepreneurs"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None

# Regex pattern from Alteryx RegEx tool (Tool 32)
SOCIAL_ENTREPRENEUR_PATTERN = re.compile(
    r".*social entrepreneur.*", re.IGNORECASE
)


def filter_social_entrepreneurs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter rows where speaker_occupation matches the social entrepreneur pattern,
    and add a boolean match column.

    Mirrors Alteryx RegEx tool (Tool 32):
        - Pattern: .*social entrepreneur.*
        - Case insensitive
        - Output: matched rows + boolean indicator column

    Args:
        df: Enriched TED DataFrame with 'speaker_occupation' column.

    Returns:
        Filtered DataFrame with 'comments_Matched' boolean column added.
    """
    df = df.copy()

    # Add boolean match column
    df["comments_Matched"] = df["speaker_occupation"].apply(
        lambda occ: bool(SOCIAL_ENTREPRENEUR_PATTERN.match(str(occ)))
        if pd.notna(occ)
        else False
    )

    # Filter to only matched rows
    result = df[df["comments_Matched"]].copy()

    return result


if dataiku is not None and df is not None:
    result = filter_social_entrepreneurs(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
