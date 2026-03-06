# Dataiku Python Recipe: Monthly Talk Frequency Chart
#
# Mirrors: Ted talk Workflow.yxmd — Tools 24 → 25 → 26
#   - Summarize (Tool 24): Count(main_speaker) by Month, Month_name
#   - Sort (Tool 25): Month ascending
#   - PlotlyCharting (Tool 26): scatter + lines+markers chart
#       - x = Month_name, y = Count
#       - title = "Frequency of Month-wise Talks"
#       - marker color = rgb(255, 127, 14)
#       - width=700, height=849
#
# Input dataset:  ted_enriched
# Output dataset: ted_monthly_counts  (tabular)
# Output folder:  ted_talk_charts     (chart HTML file)

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "ted_enriched"
    OUTPUT_DATASET = "ted_monthly_counts"
    MANAGED_FOLDER = "ted_talk_charts"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
    folder = dataiku.Folder(MANAGED_FOLDER)
except ImportError:
    dataiku = None
    df = None
    folder = None


def monthly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group talks by Month and Month_name, count occurrences, and sort by Month.

    Mirrors Alteryx tools:
        Summarize (Tool 24): Count(main_speaker), GroupBy(Month), GroupBy(Month_name)
        Sort (Tool 25): Month ascending

    Args:
        df: Enriched TED DataFrame with 'main_speaker', 'Month', 'Month_name'.

    Returns:
        DataFrame with columns [Month, Month_name, Count], sorted by Month.
    """
    counts = (
        df.groupby(["Month", "Month_name"])
        .size()
        .reset_index(name="Count")
    )
    counts = counts.sort_values("Month", ascending=True).reset_index(drop=True)
    return counts


def generate_chart(counts_df: pd.DataFrame, folder_handle=None, output_path: str = None):
    """
    Generate a Plotly scatter+line chart mirroring Tool 26 configuration.

    Chart configuration (from Ted talk Workflow.yxmd, Tool 26):
        - type: scatter
        - mode: lines+markers
        - xsrc: Month_name
        - ysrc: Count
        - name: Month-wise talks
        - marker color: rgb(255, 127, 14)
        - marker size: 6
        - line width: 1
        - title: "<b>Frequency of Month-wise Talks</b>"
        - width: 700, height: 849
        - showlegend: false

    Args:
        counts_df: Monthly counts DataFrame.
        folder_handle: Dataiku Folder handle (optional).
        output_path: Local file path for output (optional, for testing).
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return  # Plotly not available; skip chart generation

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=counts_df["Month_name"],
            y=counts_df["Count"],
            mode="lines+markers",
            name="Month-wise talks",
            line=dict(width=1),
            marker=dict(
                size=6,
                color="rgb(255, 127, 14)",
                line=dict(width=0),
            ),
            hoverinfo="x+y",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Frequency of Month-wise Talks</b>"),
        font=dict(family="sans-serif", size=12),
        autosize=False,
        width=700,
        height=849,
        showlegend=False,
        hovermode="closest",
        xaxis=dict(
            title=dict(text="Month_name"),
            tickfont=dict(size=12),
            type="category",
            tickangle=0,
        ),
        yaxis=dict(
            title=dict(text="Count"),
            type="linear",
        ),
        margin=dict(pad=0, t=100, b=80, l=80, r=80),
    )

    html_content = fig.to_html(include_plotlyjs="cdn")

    if folder_handle is not None:
        folder_handle.upload_stream(
            "monthly_talks_chart.html",
            html_content.encode("utf-8"),
        )
    elif output_path is not None:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)


if dataiku is not None and df is not None:
    counts_df = monthly_counts(df)

    # Write tabular output
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(counts_df)

    # Write chart to managed folder
    generate_chart(counts_df, folder_handle=folder)
