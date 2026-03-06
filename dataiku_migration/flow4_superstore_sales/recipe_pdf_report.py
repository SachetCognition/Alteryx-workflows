# Dataiku Python Recipe: PDF Report Generation
#
# Mirrors: New Workflow2.yxmd — ComposerTable + ComposerText + ComposerRender
#   - ComposerTable (Tool 22, lines 623-637): Styled table with conditional
#     orange (#ff8040) background on the row where Sum_Sales == Min_Sum_Sales
#   - ComposerText (lines 676-702): Text block listing each Sub-Category
#     and its Sum_Sales: "[Sub-Category:A][Sum_Sales:2]"
#   - ComposerRender (line 719): portrait, 612x792pt page → PDF output
#
# Input dataset:  superstore_cross_joined
# Output folder:  superstore_reports (PDF file)

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "superstore_cross_joined"
    MANAGED_FOLDER = "superstore_reports"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
    folder = dataiku.Folder(MANAGED_FOLDER)
except ImportError:
    dataiku = None
    df = None
    folder = None


def build_styled_table_html(df: pd.DataFrame) -> str:
    """
    Build an HTML table with conditional orange highlighting on the row
    where Sum_Sales equals Min_Sum_Sales.

    Mirrors ComposerTable style rule (lines 623-637):
        If Sum_Sales == Min_Sum_Sales → background-color: #ff8040

    Args:
        df: Cross-joined DataFrame with ['Sub-Category', 'Sum_Sales', 'Min_Sum_Sales'].

    Returns:
        HTML string of the styled table.
    """
    rows_html = []
    for _, row in df.iterrows():
        is_min = row["Sum_Sales"] == row["Min_Sum_Sales"]
        bg_style = ' style="background-color: #ff8040;"' if is_min else ""
        rows_html.append(
            f"<tr{bg_style}>"
            f"<td>{row['Sub-Category']}</td>"
            f"<td>{row['Sum_Sales']:.2f}</td>"
            f"<td>{row['Min_Sum_Sales']:.2f}</td>"
            f"</tr>"
        )

    table_html = (
        "<table border='1' cellpadding='4' cellspacing='0' "
        "style='border-collapse: collapse; font-family: Arial; font-size: 10pt;'>\n"
        "<thead style='background-color: #dbdbdb; color: #0080c0; font-size: 12pt;'>\n"
        "<tr><th>Sub-Category</th><th>Sum_Sales</th><th>Min_Sum_Sales</th></tr>\n"
        "</thead>\n<tbody>\n"
        + "\n".join(rows_html)
        + "\n</tbody>\n</table>"
    )
    return table_html


def build_text_block(df: pd.DataFrame) -> str:
    """
    Build a text block listing each Sub-Category and its Sum_Sales.

    Mirrors ComposerText (lines 676-702):
        Format: [Sub-Category:A][Sum_Sales:2]

    Args:
        df: Cross-joined DataFrame.

    Returns:
        HTML string of the text block.
    """
    lines = []
    for _, row in df.iterrows():
        lines.append(
            f"<p><strong>{row['Sub-Category']}</strong>: "
            f"${row['Sum_Sales']:,.2f}</p>"
        )
    return "\n".join(lines)


def generate_bar_chart_image(df: pd.DataFrame) -> str:
    """
    Generate a base64-encoded bar chart image for embedding in PDF.

    Args:
        df: Cross-joined DataFrame with Sales by Category.

    Returns:
        Base64-encoded PNG image as data URI, or empty string if plotly unavailable.
    """
    try:
        import plotly.graph_objects as go
        import base64
    except ImportError:
        return ""

    # We only have sub-category data here; create a simple bar chart
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Sub-Category"],
            y=df["Sum_Sales"],
            marker_color="steelblue",
        )
    )
    fig.update_layout(
        title="Category vs Sales",
        xaxis_title="Sub-Category",
        yaxis_title="Sales",
        width=550,
        height=400,
    )

    try:
        img_bytes = fig.to_image(format="png")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        # kaleido not available; try SVG fallback
        try:
            svg_str = fig.to_image(format="svg").decode("utf-8")
            b64_svg = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64_svg}"
        except Exception:
            return ""


def generate_pdf_report(
    df: pd.DataFrame, folder_handle=None, output_path: str = None
):
    """
    Generate a PDF report containing:
        1. Bar chart (embedded if possible)
        2. Styled HTML table with conditional orange highlight
        3. Text block listing Sub-Category and Sum_Sales

    Mirrors ComposerRender (line 719): portrait, 612x792pt page.

    Args:
        df: Cross-joined DataFrame.
        folder_handle: Dataiku Folder handle (optional).
        output_path: Local file path for output (optional, for testing).
    """
    # Build HTML components
    table_html = build_styled_table_html(df)
    text_block = build_text_block(df)
    chart_img = generate_bar_chart_image(df)

    chart_section = ""
    if chart_img:
        chart_section = f'<img src="{chart_img}" alt="Category vs Sales Chart" />'
    else:
        chart_section = "<p><em>[Chart requires plotly + kaleido]</em></p>"

    # Assemble full HTML document
    # Page size: 612x792pt (US Letter portrait) per ComposerRender config
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: 612pt 792pt;
        margin: 36pt;
    }}
    body {{
        font-family: Arial, sans-serif;
        font-size: 10pt;
        color: #000000;
    }}
    h1 {{
        color: #0080c0;
        font-size: 16pt;
    }}
    h2 {{
        color: #333;
        font-size: 12pt;
        margin-top: 20pt;
    }}
</style>
</head>
<body>
    <h1>Superstore Sales Report — 2016</h1>

    <h2>Sales by Category</h2>
    {chart_section}

    <h2>Sub-Category Sales Summary</h2>
    {table_html}

    <h2>Sales Details</h2>
    {text_block}
</body>
</html>"""

    # Convert HTML to PDF using WeasyPrint
    try:
        from weasyprint import HTML as WeasyHTML

        pdf_bytes = WeasyHTML(string=html_doc).write_pdf()
    except ImportError:
        # WeasyPrint not available; write HTML instead
        pdf_bytes = html_doc.encode("utf-8")
        if folder_handle is not None:
            folder_handle.upload_stream(
                "superstore_report.html", pdf_bytes
            )
        elif output_path is not None:
            html_path = output_path.replace(".pdf", ".html")
            with open(html_path, "wb") as f:
                f.write(pdf_bytes)
        return

    if folder_handle is not None:
        folder_handle.upload_stream(
            "superstore_report.pdf", pdf_bytes
        )
    elif output_path is not None:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)


if dataiku is not None and df is not None:
    generate_pdf_report(df, folder_handle=folder)
