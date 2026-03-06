# Flow 4 — Superstore Sales Analysis and PDF Report

## Original Alteryx Workflow

**File:** `New Workflow2.yxmd`

### Alteryx Tool Chain

```
Sample - Superstore.xls (Input Tool 1, Orders sheet)
    └─→ AutoField (Tool 3): Auto-type columns
            └─→ Filter (Tool 5): Order Date 2016-01-01 to 2017-01-01
                    │
                    ├─→ Summarize (Tool 7): Sum(Sales) → Sum_Sales (total)
                    │       └─→ BrowseV2 (Tool 8)
                    │
                    ├─→ Sort (Tool 9): Sales descending
                    │       └─→ Sample (Tool 10): First 5
                    │               │
                    │               ├─→ Summarize (Tool 13): Min(Sales) → Min_Sum_Sales
                    │               │
                    │               └─→ Summarize (Tool 20): GroupBy Sub-Category, Sum(Sales)
                    │                       │
                    │                       └─→ AppendFields (Tool 26) ←── Min_Sum_Sales
                    │                               │
                    │                               ├─→ ComposerTable (Tool 22)
                    │                               │       (orange highlight on min row)
                    │                               │
                    │                               ├─→ ComposerText (Tool 25)
                    │                               │       ([Sub-Category:A][Sum_Sales:2])
                    │                               │
                    │                               └─→ ComposerRender (Tool 27)
                    │                                       (portrait PDF, 612x792pt)
                    │
                    └─→ PlotlyCharting (Tool 24): Bar chart Category vs Sales
```

---

## Dataiku Flow Diagram

```
[superstore_orders]
    └──→ recipe_date_filter_2016.py ──→ [superstore_2016]
                                              │
                                              ├──→ recipe_aggregations.py ──→ [superstore_total_sales]
                                              │                           ──→ [superstore_top5]
                                              │                           ──→ [superstore_min_sales]
                                              │                           ──→ [superstore_subcategory_sales]
                                              │
                                              ├──→ recipe_plotly_bar.py ──→ [superstore_reports/chart.html]
                                              │
                                              └──→ recipe_cross_join.py ←── [superstore_subcategory_sales]
                                                                        ←── [superstore_min_sales]
                                                      └──→ [superstore_cross_joined]
                                                              └──→ recipe_pdf_report.py ──→ [superstore_reports/report.pdf]
```

---

## Setup Steps

### Datasets

1. **superstore_orders** — Upload `Sample - Superstore.xls` (Orders sheet).
2. **superstore_2016** — Output of `recipe_date_filter_2016.py`.
3. **superstore_total_sales** — Output of `recipe_aggregations.py`.
4. **superstore_top5** — Output of `recipe_aggregations.py`.
5. **superstore_min_sales** — Output of `recipe_aggregations.py`.
6. **superstore_subcategory_sales** — Output of `recipe_aggregations.py`.
7. **superstore_cross_joined** — Output of `recipe_cross_join.py`.

### Managed Folder

- **superstore_reports** — Stores `category_sales_chart.html` and `superstore_report.pdf`.

### Recipe Wiring

| Recipe | Input(s) | Output(s) |
|---|---|---|
| `recipe_date_filter_2016.py` | `superstore_orders` | `superstore_2016` |
| `recipe_aggregations.py` | `superstore_2016` | `superstore_total_sales`, `superstore_top5`, `superstore_min_sales`, `superstore_subcategory_sales` |
| `recipe_cross_join.py` | `superstore_subcategory_sales`, `superstore_min_sales` | `superstore_cross_joined` |
| `recipe_plotly_bar.py` | `superstore_2016` | `superstore_reports` (chart HTML) |
| `recipe_pdf_report.py` | `superstore_cross_joined` | `superstore_reports` (PDF) |

---

## Business Logic Preserved

| Alteryx Step | Python Equivalent | Validation |
|---|---|---|
| Filter `Order Date` 2016 range | `pd.Timestamp` range filter | Row counts match |
| `Sum(Sales)` | `df['Sales'].sum()` | Total matches |
| Sort Sales desc + First 5 | `sort_values().head(5)` | Top 5 match |
| `Min(Sales)` from top 5 | `top5['Sales'].min()` | Min value matches |
| GroupBy Sub-Category Sum(Sales) | `groupby().sum()` | Sub-category totals match |
| AppendFields (cross-join) | `df.assign(Min_Sum_Sales=value)` | All rows get scalar |
| ComposerTable orange highlight | HTML `style="background-color: #ff8040"` | Row with min highlighted |
| ComposerText format | `f"<p><strong>{SubCat}</strong>: ${Sales}"` | Text block format matches |
| ComposerRender portrait PDF | WeasyPrint `@page { size: 612pt 792pt }` | PDF dimensions match |
