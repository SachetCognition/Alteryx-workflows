"""
Dataiku Python Recipe: TED Talk Analysis
Replicates Alteryx workflow "Ted talk Workflow.yxmd"

Connection graph:
  Input(2) -> Browse(3) + Formula(4)
  Formula(4) -> Browse(5) + Formula(6)
  Formula(6) -> Browse(7) + Sort(8) + Summarize(15) + Summarize(24) +
                MultiRowFormula(28) + RegEx(32)
  Sort(8) -> Sample(10) -> Browse(13) + Sort(11)
  Sort(11) -> ComposerTable(12) -> Browse(14)
  Summarize(15) -> Sort(16) -> Formula(17) -> RunningTotal(18) ->
    Browse(21) + Sample(20) -> ComposerTable(22) -> Browse(23)
  Summarize(24) -> Sort(25) -> PlotlyChart(26) -> Browse(27)
  MultiRowFormula(28) -> Browse(29) + ComposerTable(30) -> Browse(31)
  RegEx(32) -> Browse(33) + ComposerTable(34) -> Browse(35)

Input:  ted_main.csv
Output: ted_enriched, ted_top_viewed_per_year, ted_speaker_frequency,
        ted_monthly_frequency, ted_consecutive_years, ted_social_entrepreneurs,
        ted_monthly_chart.html
"""

import os
import sys

import pandas as pd

try:
    import dataiku

    RUNNING_IN_DATAIKU = True
except ImportError:
    RUNNING_IN_DATAIKU = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Configuration ──────────────────────────────────────────────────────────
INPUT_CSV = os.environ.get(
    "INPUT_TED_CSV",
    os.path.join(os.path.dirname(__file__), "..", "..", "Datasets", "ted_main.csv"),
)
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR",
    os.path.join(os.path.dirname(__file__), "..", "output"),
)


def _generate_monthly_chart(monthly: pd.DataFrame, output_dir: str) -> str | None:
    """Generate Plotly scatter chart for monthly talk frequency."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("WARNING: plotly not installed, skipping chart generation.")
        return None

    fig = go.Figure(
        data=[
            go.Scatter(
                x=monthly["Month_name"],
                y=monthly["Count"],
                mode="lines+markers",
                name="Month-wise talks",
                marker=dict(
                    color="rgb(255, 127, 14)",
                    size=6,
                ),
                line=dict(color="rgb(255, 127, 14)"),
            )
        ]
    )
    fig.update_layout(
        title=dict(text="<b>Frequency of Month-wise Talks</b>"),
        width=700,
        height=849,
    )

    os.makedirs(output_dir, exist_ok=True)
    chart_path = os.path.join(output_dir, "ted_monthly_chart.html")
    fig.write_html(chart_path)
    return chart_path


def _generate_html_table(
    df: pd.DataFrame,
    columns: list[str],
    header_font: str = "Arial",
    header_size: int = 12,
    header_text_color: str = "#000000",
    header_bg_color: str = "#dbdbdb",
    data_font: str = "Arial",
    data_size: int = 8,
) -> str:
    """Generate a styled HTML table from a DataFrame."""
    header_cells = "".join(
        f'<th style="font-family:{header_font};font-size:{header_size}pt;'
        f"color:{header_text_color};background-color:{header_bg_color};"
        f'padding:4px 8px;">{col}</th>'
        for col in columns
    )

    rows_html = []
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#ffffff" if i % 2 == 0 else "#f0f0f0"
        cells = "".join(
            f'<td style="font-family:{data_font};font-size:{data_size}pt;'
            f'background-color:{bg};padding:4px 8px;">{row.get(col, "")}</td>'
            for col in columns
        )
        rows_html.append(f"<tr>{cells}</tr>")

    return (
        '<table style="border-collapse:collapse;border:1px solid #999;">'
        f"<tr>{header_cells}</tr>"
        f"{''.join(rows_html)}"
        "</table>"
    )


def run(input_path: str | None = None, output_dir: str | None = None) -> dict[str, pd.DataFrame]:
    """Execute the full TED Talk Analysis pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to the ted_main.csv file.
    output_dir : str | None
        Directory for chart and table outputs.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary of output dataset names to DataFrames.
    """
    input_path = input_path or INPUT_CSV
    output_dir = output_dir or OUTPUT_DIR

    # ── Step 1: Input (ToolID 2) ───────────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        df = dataiku.Dataset("ted_main").get_dataframe()
    else:
        df = pd.read_csv(input_path, dtype=str, encoding="latin-1")

    # ── Step 2: Formula (ToolID 4) ─────────────────────────────────────────
    # Convert film_date from Unix epoch to datetime
    df["film_date"] = pd.to_datetime(df["film_date"].astype(float), unit="s")

    # ── Step 3: Formula (ToolID 6) ─────────────────────────────────────────
    # Derive Year, Month, Month_name
    df["Year"] = df["film_date"].dt.year
    df["Month"] = df["film_date"].dt.month
    df["Month_name"] = df["film_date"].dt.strftime("%B")

    # Convert views to numeric for proper sorting/aggregation
    df["views"] = pd.to_numeric(df["views"], errors="coerce")
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    df["languages"] = pd.to_numeric(df["languages"], errors="coerce")
    df["num_speaker"] = pd.to_numeric(df["num_speaker"], errors="coerce")

    ted_enriched = df.copy()

    # ── Branch A: Top 5 most-viewed per year ───────────────────────────────
    # Sort(8): Sort by views descending
    df_sorted_views = df.sort_values("views", ascending=False)

    # Sample(10): First 5 per Year group
    ted_top_viewed_per_year = (
        df_sorted_views.groupby("Year").head(5).copy()
    )

    # Sort(11): Sort by Year descending
    ted_top_viewed_per_year = ted_top_viewed_per_year.sort_values(
        "Year", ascending=False
    ).reset_index(drop=True)

    # ComposerTable(12): Generate HTML table
    os.makedirs(output_dir, exist_ok=True)
    top_viewed_html = _generate_html_table(
        ted_top_viewed_per_year,
        columns=["main_speaker", "views", "Year", "Month", "Month_name"],
        header_text_color="#0080c0",
        header_bg_color="#dbdbdb",
    )
    with open(os.path.join(output_dir, "ted_top_viewed_table.html"), "w") as f:
        f.write(top_viewed_html)

    # ── Branch B: Top 5 most frequent speakers ─────────────────────────────
    # Summarize(15): Count by main_speaker
    speaker_freq = df.groupby("main_speaker").size().reset_index(name="Count")

    # Sort(16): Sort by Count descending
    speaker_freq = speaker_freq.sort_values("Count", ascending=False).reset_index(drop=True)

    # Formula(17): Rank = 1 (constant)
    speaker_freq["Rank"] = 1

    # RunningTotal(18): Running sum of Rank -> RunTot_Rank
    speaker_freq["RunTot_Rank"] = range(1, len(speaker_freq) + 1)

    # Sample(20): First 5 rows
    ted_speaker_frequency = speaker_freq.head(5).copy().reset_index(drop=True)

    # ComposerTable(22): Generate HTML table
    speaker_html = _generate_html_table(
        ted_speaker_frequency,
        columns=["Count", "main_speaker", "RunTot_Rank"],
        header_font="Arial",
        header_size=12,
        header_text_color="#000000",
        header_bg_color="#0080c0",
    )
    with open(os.path.join(output_dir, "ted_speaker_freq_table.html"), "w") as f:
        f.write(speaker_html)

    # ── Branch C: Month-wise frequency scatter chart ───────────────────────
    # Summarize(24): Count by Month, Month_name
    ted_monthly_frequency = (
        df.groupby(["Month", "Month_name"]).size().reset_index(name="Count")
    )

    # Sort(25): Sort by Month ascending
    ted_monthly_frequency = ted_monthly_frequency.sort_values("Month").reset_index(drop=True)

    # PlotlyChart(26): Generate scatter chart
    _generate_monthly_chart(ted_monthly_frequency, output_dir)

    # ── Branch D: Consecutive year detection ───────────────────────────────
    # MultiRowFormula(28): Check if Year is numeric (always Yes since we derived it)
    # The Alteryx formula ToNumber("Year", 'Yes', 'No') tries to convert literal
    # string "Year" to number. Since we derived Year as int, it's always valid.
    df_consecutive = df.copy()
    df_consecutive["Consecutive"] = df_consecutive["Year"].apply(
        lambda x: "Yes" if pd.notna(x) else "No"
    )
    ted_consecutive_years = df_consecutive[
        ["main_speaker", "Year", "Consecutive"]
    ].copy()

    # ComposerTable(30): Generate HTML table
    consecutive_html = _generate_html_table(
        ted_consecutive_years,
        columns=["main_speaker", "Year", "Consecutive"],
        header_font="Arial",
        header_size=10,
        header_text_color="#ffffff",
        header_bg_color="#004080",
    )
    with open(os.path.join(output_dir, "ted_consecutive_table.html"), "w") as f:
        f.write(consecutive_html)

    # ── Branch E: Social entrepreneur filter ───────────────────────────────
    # RegEx(32): Match speaker_occupation against "social entrepreneur" (case-insensitive)
    df["comments_Matched"] = df["speaker_occupation"].str.contains(
        r"social entrepreneur", case=False, na=False
    )
    # Match method: output only matched rows
    ted_social_entrepreneurs = df[df["comments_Matched"]].copy()
    ted_social_entrepreneurs = ted_social_entrepreneurs[
        ["main_speaker", "name", "speaker_occupation", "comments_Matched"]
    ].reset_index(drop=True)

    # ComposerTable(34): Generate HTML table
    social_html = _generate_html_table(
        ted_social_entrepreneurs,
        columns=["main_speaker", "name", "speaker_occupation", "comments_Matched"],
        header_font="Arial",
        header_size=10,
        header_text_color="#ffffff",
        header_bg_color="#0080c0",
    )
    with open(os.path.join(output_dir, "ted_social_entrepreneurs_table.html"), "w") as f:
        f.write(social_html)

    # ── Write Dataiku output datasets ──────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        dataiku.Dataset("ted_enriched").write_with_schema(ted_enriched)
        dataiku.Dataset("ted_top_viewed_per_year").write_with_schema(ted_top_viewed_per_year)
        dataiku.Dataset("ted_speaker_frequency").write_with_schema(ted_speaker_frequency)
        dataiku.Dataset("ted_monthly_frequency").write_with_schema(ted_monthly_frequency)
        dataiku.Dataset("ted_consecutive_years").write_with_schema(ted_consecutive_years)
        dataiku.Dataset("ted_social_entrepreneurs").write_with_schema(ted_social_entrepreneurs)

    return {
        "ted_enriched": ted_enriched,
        "ted_top_viewed_per_year": ted_top_viewed_per_year,
        "ted_speaker_frequency": ted_speaker_frequency,
        "ted_monthly_frequency": ted_monthly_frequency,
        "ted_consecutive_years": ted_consecutive_years,
        "ted_social_entrepreneurs": ted_social_entrepreneurs,
    }


if __name__ == "__main__":
    outputs = run()
    print(f"=== ted_enriched ({len(outputs['ted_enriched'])} rows) ===")
    print(outputs["ted_enriched"].head(3).to_string(index=False))
    print(f"\n=== ted_top_viewed_per_year ({len(outputs['ted_top_viewed_per_year'])} rows) ===")
    print(
        outputs["ted_top_viewed_per_year"][["main_speaker", "views", "Year"]]
        .head(10)
        .to_string(index=False)
    )
    print("\n=== ted_speaker_frequency ===")
    print(outputs["ted_speaker_frequency"].to_string(index=False))
    print("\n=== ted_monthly_frequency ===")
    print(outputs["ted_monthly_frequency"].to_string(index=False))
    print(f"\n=== ted_social_entrepreneurs ({len(outputs['ted_social_entrepreneurs'])} rows) ===")
    print(outputs["ted_social_entrepreneurs"].head(5).to_string(index=False))
