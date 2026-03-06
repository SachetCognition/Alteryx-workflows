# Dataiku Python Recipe: Speaker Frequency and Running Rank
#
# Mirrors: Ted talk Workflow.yxmd — Tools 15 → 16 → 17 → 18 → 20
#   - Summarize (Tool 15): Count by main_speaker, GroupBy main_speaker
#   - Sort (Tool 16): Count descending
#   - Formula (Tool 17): Rank = 1 (initial value)
#   - RunningTotal (Tool 18): RunTot_Rank = cumulative sum of Rank
#   - Sample (Tool 20): First 5 rows
#
# Input dataset:  ted_enriched
# Output dataset: ted_speaker_ranking

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_speaker_ranking"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def speaker_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count talks per speaker, sort by count descending, add a running rank,
    and return the top 5.

    Mirrors Alteryx tool chain:
        Summarize (Tool 15): Count(main_speaker) as Count, GroupBy(main_speaker)
        Sort (Tool 16): Count descending
        Formula (Tool 17): Rank = 1
        RunningTotal (Tool 18): RunTot_Rank = cumsum(Rank)
        Sample (Tool 20): First 5

    Args:
        df: Enriched TED DataFrame with 'main_speaker' column.

    Returns:
        DataFrame with columns [Count, main_speaker, RunTot_Rank], top 5 speakers.
    """
    # Step 1: Summarize — count talks per speaker
    speaker_counts = (
        df.groupby("main_speaker")
        .size()
        .reset_index(name="Count")
    )

    # Step 2: Sort by Count descending
    speaker_counts = speaker_counts.sort_values(
        "Count", ascending=False
    ).reset_index(drop=True)

    # Step 3: Formula — Rank = 1 for each row
    speaker_counts["Rank"] = 1

    # Step 4: RunningTotal — cumulative sum of Rank column
    speaker_counts["RunTot_Rank"] = speaker_counts["Rank"].cumsum()

    # Step 5: Sample — first 5 rows
    result = speaker_counts.head(5).copy()

    # Select output columns matching Alteryx ComposerTable (Tool 22):
    # Count, main_speaker, RunTot_Rank
    result = result[["Count", "main_speaker", "RunTot_Rank"]].reset_index(
        drop=True
    )

    return result


if dataiku is not None and df is not None:
    result = speaker_ranking(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(result)
