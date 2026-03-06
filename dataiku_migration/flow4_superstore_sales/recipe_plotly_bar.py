# Dataiku Python Recipe: Plotly Bar Chart — Category vs Sales
#
# Mirrors: New Workflow2.yxmd — PlotlyCharting Tool 24
#   - Bar chart with Category on x-axis and Sales on y-axis
#
# Input dataset:  superstore_2016
# Output folder:  superstore_reports (chart HTML)

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "superstore_2016"
    MANAGED_FOLDER = "superstore_reports"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
    folder = dataiku.Folder(MANAGED_FOLDER)
except ImportError:
    dataiku = None
    df = None
    folder = None


def generate_bar_chart(
    df: pd.DataFrame, folder_handle=None, output_path: str = None
) -> str:
    """
    Generate a Plotly bar chart showing Sales by Category.

    Mirrors Alteryx PlotlyCharting tool configuration in New Workflow2.yxmd.

    Args:
        df: Superstore orders DataFrame with 'Category' and 'Sales' columns.
        folder_handle: Dataiku Folder handle (optional).
        output_path: Local file path for output (optional, for testing).

    Returns:
        HTML string of the chart.
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return ""

    # Ensure Sales is numeric
    df = df.copy()
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    # Aggregate Sales by Category
    cat_sales = df.groupby("Category")["Sales"].sum().reset_index()
    cat_sales = cat_sales.sort_values("Sales", ascending=False)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=cat_sales["Category"],
            y=cat_sales["Sales"],
            marker_color="steelblue",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Category vs Sales</b>"),
        xaxis=dict(title="Category"),
        yaxis=dict(title="Sales"),
        font=dict(family="sans-serif", size=12),
    )

    html_content = fig.to_html(include_plotlyjs="cdn")

    if folder_handle is not None:
        folder_handle.upload_stream(
            "category_sales_chart.html",
            html_content.encode("utf-8"),
        )
    elif output_path is not None:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    return html_content


if dataiku is not None and df is not None:
    generate_bar_chart(df, folder_handle=folder)
