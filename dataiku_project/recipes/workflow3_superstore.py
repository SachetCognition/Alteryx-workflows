"""
Dataiku Python Recipe: Superstore Sales Report
Replicates Alteryx workflow "New Workflow2.yxmd"

Connection graph:
  Input(1) -> Browse(4) + AutoField(3)
  AutoField(3) -> Filter(5)
  Filter(5:True) -> Browse(6) + Summarize(7) + Sort(9)
  Summarize(7) -> Browse(8)
  Sort(9) -> Sample(10)
  Sample(10) -> Browse(11) + Summarize(13) + PlotlyChart(16) + Summarize(20)
  Summarize(13) -> Browse(14)
  Summarize(20) -> Summarize(22) + AppendFields(26:Source) + ComposerText(31)
  Summarize(22) -> AppendFields(26:Targets) + Browse(24)
  AppendFields(26) -> ComposerTable(28)
  ComposerTable(28) -> Browse(29) + ComposerRender(32)
  ComposerText(31) -> Browse(21)

Input:  Sample - Superstore.xls (sheet: Orders)
Output: superstore_filtered, superstore_total_sales, superstore_top5,
        superstore_min_sales, superstore_subcategory_sales,
        superstore_chart.html, superstore_report.pdf
"""

import os
import sys
from datetime import date

import pandas as pd

try:
    import dataiku

    RUNNING_IN_DATAIKU = True
except ImportError:
    RUNNING_IN_DATAIKU = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Configuration ──────────────────────────────────────────────────────────
INPUT_XLS = os.environ.get(
    "INPUT_SUPERSTORE_XLS",
    os.path.join(os.path.dirname(__file__), "..", "..", "Datasets", "Sample - Superstore.xls"),
)
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR",
    os.path.join(os.path.dirname(__file__), "..", "output"),
)


def _generate_plotly_chart(top5: pd.DataFrame, output_dir: str) -> str | None:
    """Generate Plotly bar chart from top5 data. Returns path to HTML file."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("WARNING: plotly not installed, skipping chart generation.")
        return None

    color_scale = [
        [0, "#dcdcdc"],
        [0.333, "#f5c39d"],
        [0.667, "#f5a069"],
        [1, "#b20a1c"],
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=top5["Category"],
                y=top5["Sales"],
                marker=dict(
                    color=top5["Sales"],
                    colorscale=color_scale,
                    cmin=8400,
                    cmax=17500,
                    showscale=True,
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="<b>Sales data Report</b>",
            font=dict(color="blue"),
        ),
        width=500,
        height=849,
    )

    os.makedirs(output_dir, exist_ok=True)
    chart_path = os.path.join(output_dir, "superstore_chart.html")
    fig.write_html(chart_path)
    return chart_path


def _generate_pdf_report(
    subcategory_sales: pd.DataFrame,
    min_sum_sales: float,
    output_dir: str,
) -> str | None:
    """Generate styled PDF report from subcategory sales data."""
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "superstore_report.pdf")

    # Build HTML table with conditional formatting
    rows_html = []
    for _, row in subcategory_sales.iterrows():
        bg = ' style="background-color: #ff8040;"' if row["Sum_Sales"] == min_sum_sales else ""
        rows_html.append(
            f"<tr{bg}>"
            f"<td>{min_sum_sales:.2f}</td>"
            f"<td>{row['Sum_Sales']:.2f}</td>"
            f"<td>{row['Sub-Category']}</td>"
            f"</tr>"
        )

    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 36px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #999; padding: 6px 10px; text-align: left; }}
  th {{ background-color: #4472C4; color: white; }}
</style>
</head>
<body>
<h2>Superstore Sales Report</h2>
<table>
  <tr><th>Min_Sum_Sales</th><th>Sum_Sales</th><th>Sub-Category</th></tr>
  {"".join(rows_html)}
</table>
<h3>Sub-Category Sales Summary</h3>
{"".join(f'<p>{r["Sub-Category"]:<20s} {r["Sum_Sales"]:.2f}</p>' for _, r in subcategory_sales.iterrows())}
</body>
</html>"""

    # Build a simpler text-based report for the ComposerText section
    text_lines = []
    for _, row in subcategory_sales.iterrows():
        text_lines.append(f"{row['Sub-Category']:<20s} {row['Sum_Sales']:.2f}")

    try:
        from fpdf import FPDF

        pdf = FPDF(orientation="P", unit="pt", format="Letter")
        pdf.add_page()
        pdf.set_margins(36, 36, 36)

        # Title
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 20, "Superstore Sales Report", ln=True, align="C")
        pdf.ln(10)

        # Table header
        pdf.set_font("Arial", "B", 10)
        col_widths = [120, 100, 150]
        headers = ["Min_Sum_Sales", "Sum_Sales", "Sub-Category"]
        pdf.set_fill_color(68, 114, 196)
        pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 18, header, border=1, fill=True, align="C")
        pdf.ln()

        # Table rows
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        for _, row in subcategory_sales.iterrows():
            if row["Sum_Sales"] == min_sum_sales:
                pdf.set_fill_color(255, 128, 64)
                fill = True
            else:
                pdf.set_fill_color(255, 255, 255)
                fill = True
            pdf.cell(col_widths[0], 16, f"{min_sum_sales:.2f}", border=1, fill=fill, align="R")
            pdf.cell(col_widths[1], 16, f"{row['Sum_Sales']:.2f}", border=1, fill=fill, align="R")
            pdf.cell(col_widths[2], 16, str(row["Sub-Category"]), border=1, fill=fill)
            pdf.ln()

        pdf.ln(15)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 16, "Sub-Category Sales Summary", ln=True)
        pdf.set_font("Arial", "", 9)
        for line in text_lines:
            pdf.cell(0, 14, line, ln=True)

        pdf.output(pdf_path)
        return pdf_path

    except ImportError:
        # Fallback: save as HTML
        html_path = os.path.join(output_dir, "superstore_report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("WARNING: fpdf2 not installed, saved report as HTML instead of PDF.")
        return html_path


def run(input_path: str | None = None, output_dir: str | None = None) -> dict[str, pd.DataFrame]:
    """Execute the full Superstore Sales Report pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to the Sample - Superstore.xls file.
    output_dir : str | None
        Directory where chart and report will be written.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary of output dataset names to DataFrames.
    """
    input_path = input_path or INPUT_XLS
    output_dir = output_dir or OUTPUT_DIR

    # ── Step 1: Input ──────────────────────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        df = dataiku.Dataset("Superstore_Orders").get_dataframe()
    else:
        df = pd.read_excel(input_path, sheet_name="Orders")

    # ── Step 2: AutoField (ToolID 3) ───────────────────────────────────────
    # Optimize field sizes - no-op in pandas

    # ── Step 3: Filter (ToolID 5) ──────────────────────────────────────────
    # Order Date between 2016-01-01 and 2017-01-01 (inclusive)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    superstore_filtered = df[
        (df["Order Date"].dt.date >= date(2016, 1, 1))
        & (df["Order Date"].dt.date <= date(2017, 1, 1))
    ].copy()
    superstore_filtered = superstore_filtered.reset_index(drop=True)

    # ── Step 4: Summarize (ToolID 7) ───────────────────────────────────────
    # Grand total of Sales
    total_sales_value = superstore_filtered["Sales"].astype(float).sum()
    superstore_total_sales = pd.DataFrame({"Sum_Sales": [total_sales_value]})

    # ── Step 5: Sort (ToolID 9) ────────────────────────────────────────────
    # Sort by Sales descending
    superstore_filtered["Sales"] = superstore_filtered["Sales"].astype(float)
    filtered_sorted = superstore_filtered.sort_values("Sales", ascending=False).reset_index(
        drop=True
    )

    # ── Step 6: Sample (ToolID 10) ─────────────────────────────────────────
    # First 5 rows
    superstore_top5 = filtered_sorted.head(5).copy().reset_index(drop=True)

    # ── Step 7: Summarize (ToolID 13) ──────────────────────────────────────
    # Min Sales from top5
    min_sales_value = superstore_top5["Sales"].min()
    superstore_min_sales = pd.DataFrame({"Min_Sales": [min_sales_value]})

    # ── Step 8: Plotly Chart (ToolID 16) ───────────────────────────────────
    _generate_plotly_chart(superstore_top5, output_dir)

    # ── Step 9: Summarize (ToolID 20) ──────────────────────────────────────
    # GroupBy Sub-Category, Sum Sales - computed on top5
    subcategory_sales = (
        superstore_top5.groupby("Sub-Category")
        .agg(Sum_Sales=("Sales", "sum"))
        .reset_index()
    )

    # ── Step 10: Summarize (ToolID 22) ─────────────────────────────────────
    # Min of Sum_Sales from subcategory_sales
    min_sum_sales_value = subcategory_sales["Sum_Sales"].min()

    # ── Step 11: AppendFields / Cross Join (ToolID 26) ─────────────────────
    subcategory_sales["Min_Sum_Sales"] = min_sum_sales_value

    # ── Step 12-14: ComposerTable + ComposerText + ComposerRender ──────────
    _generate_pdf_report(subcategory_sales, min_sum_sales_value, output_dir)

    # ── Write Dataiku output datasets ──────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        dataiku.Dataset("superstore_filtered").write_with_schema(superstore_filtered)
        dataiku.Dataset("superstore_total_sales").write_with_schema(superstore_total_sales)
        dataiku.Dataset("superstore_top5").write_with_schema(superstore_top5)
        dataiku.Dataset("superstore_min_sales").write_with_schema(superstore_min_sales)
        dataiku.Dataset("superstore_subcategory_sales").write_with_schema(subcategory_sales)

    return {
        "superstore_filtered": superstore_filtered,
        "superstore_total_sales": superstore_total_sales,
        "superstore_top5": superstore_top5,
        "superstore_min_sales": superstore_min_sales,
        "superstore_subcategory_sales": subcategory_sales,
    }


if __name__ == "__main__":
    outputs = run()
    print("=== superstore_total_sales ===")
    print(outputs["superstore_total_sales"].to_string(index=False))
    print(f"\n=== superstore_filtered ({len(outputs['superstore_filtered'])} rows) ===")
    print("\n=== superstore_top5 ===")
    print(outputs["superstore_top5"][["Category", "Sub-Category", "Sales"]].to_string(index=False))
    print("\n=== superstore_min_sales ===")
    print(outputs["superstore_min_sales"].to_string(index=False))
    print("\n=== superstore_subcategory_sales ===")
    print(outputs["superstore_subcategory_sales"].to_string(index=False))
