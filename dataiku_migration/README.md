# Alteryx-to-Dataiku Migration Guide

This directory contains the complete migration of five Alteryx Designer workflows into
Dataiku DSS Python recipes. Each flow sub-directory maps one-to-one with an original
`.yxmd` / `.yxmc` file pair, and every recipe preserves the original business logic
exactly so that identical inputs produce identical outputs.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Dataiku Project Setup](#dataiku-project-setup)
3. [Directory Layout](#directory-layout)
4. [Flow-by-Flow Migration](#flow-by-flow-migration)
   - [Flow 1 — Accident Zone](#flow-1--accident-zone)
   - [Flow 2 — Accident User Input](#flow-2--accident-user-input)
   - [Flow 3 — TED Talk](#flow-3--ted-talk)
   - [Flow 4 — Superstore Sales](#flow-4--superstore-sales)
   - [Flow 5 — Purchase Cleansing](#flow-5--purchase-cleansing)
5. [Project Variables](#project-variables)
6. [Managed Folders](#managed-folders)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Version |
|---|---|
| Dataiku DSS | 12.x or later |
| Python (code-env) | 3.8+ |
| pandas | 1.5+ |
| plotly | 5.x |
| weasyprint | 60+ |
| pytest | 7+ (for local testing) |

Install the Python dependencies in your Dataiku code environment or locally:

```bash
pip install pandas plotly weasyprint pytest
```

---

## Dataiku Project Setup

### 1. Create a New Project

In Dataiku DSS, create a new blank project (e.g., `ALTERYX_MIGRATION`).

### 2. Upload Datasets

Upload the following source files as Dataiku **Uploaded Datasets**:

| Dataset Name | Source File | Notes |
|---|---|---|
| `US_Accidents_March23` | `US_Accidents_March23.csv` | 46 columns, ISO-8859-1 encoding |
| `ted_main` | `Datasets/ted_main.csv` | 12 columns, 2,550+ rows |
| `superstore_orders` | `Sample - Superstore.xls` (Orders sheet) | 21 columns |
| `purchase_registration` | `updated1_pur_reg_2200_2300.csv` | 98 columns, ISO-8859-1 |

### 3. Create Managed Folders

| Folder Name | Purpose |
|---|---|
| `accident_zone_exports` | Per-timezone CSV outputs from Flow 1 |
| `ted_talk_charts` | Plotly HTML/image chart outputs from Flow 3 |
| `superstore_reports` | PDF report output from Flow 4 |

### 4. Set Project Variables

Go to **Project Settings > Variables** and add:

```json
{
  "start_date": "2021-01-01",
  "end_date": "2022-01-01",
  "period_type": "MTD"
}
```

### 5. Create a Python Code Environment

Create a code environment with `pandas`, `plotly`, and `weasyprint` installed.

### 6. Build the Flow

For each flow below, create the intermediate datasets and Python recipes in the
order described. Connect them as shown in the flow diagrams within each
`flow_description.md`.

---

## Directory Layout

```
dataiku_migration/
├── README.md                              # This file
├── flow1_accident_zone/
│   ├── recipe_prepare_cleanse.py          # Filter nulls, regex replace US/, uppercase
│   ├── recipe_group_by_timezone.py        # CountDistinct ID by Timezone
│   ├── recipe_batch_export.py             # For-loop per timezone, write CSV to managed folder
│   └── flow_description.md               # Dataiku Flow diagram and setup steps
├── flow2_accident_user_input/
│   ├── recipe_parse_datetime.py           # Parse Start_Time, derive Day/Day_type/Hour/EOM/EOPM
│   ├── recipe_date_filter.py              # Filter by project variables start_date/end_date
│   ├── recipe_group_daytype.py            # CountDistinct ID by Day_type
│   ├── recipe_group_hour.py               # CountDistinct ID by Hour
│   ├── recipe_join_filtered.py            # Join filtered dates back to enriched data
│   └── flow_description.md
├── flow3_ted_talk/
│   ├── recipe_epoch_to_datetime.py        # Convert film_date epoch to datetime
│   ├── recipe_top5_views_per_year.py      # Top 5 talks by views per year
│   ├── recipe_speaker_ranking.py          # Speaker frequency + running rank + top 5
│   ├── recipe_monthly_chart.py            # Group by month + Plotly chart
│   ├── recipe_consecutive_years.py        # Consecutive-year detection per speaker
│   ├── recipe_social_entrepreneur.py      # Regex filter on speaker_occupation
│   ├── recipe_period_filter.py            # MTD/YTD/WTD filter via project variable
│   └── flow_description.md
├── flow4_superstore_sales/
│   ├── recipe_date_filter_2016.py         # Filter Orders to 2016
│   ├── recipe_aggregations.py             # Sum, Min, Sort, Top 5, Group by Sub-Category
│   ├── recipe_cross_join.py               # Cross-join sub-cat sums with min
│   ├── recipe_plotly_bar.py               # Plotly bar chart Category vs Sales
│   ├── recipe_pdf_report.py               # PDF with styled table + text
│   └── flow_description.md
├── flow5_purchase_cleansing/
│   ├── recipe_cleanse.py                  # Trim, uppercase, fill nulls for all 98 columns
│   └── flow_description.md
└── tests/
    ├── conftest.py                        # Shared fixtures
    ├── test_flow1_accident_zone.py        # AZ-01 through AZ-08
    ├── test_flow2_accident_user_input.py  # AU-01 through AU-10
    ├── test_flow3_ted_talk.py             # TT-01 through TT-10
    ├── test_flow4_superstore_sales.py     # SS-01 through SS-11
    ├── test_flow5_purchase_cleansing.py   # PC-01 through PC-06
    └── test_regression.py                 # R-01 through R-06
```

---

## Flow-by-Flow Migration

### Flow 1 — Accident Zone

**Alteryx Source:** `Accident Workflow.yxmd` + `accident-macro.yxmc`

| Step | Alteryx Tool | Dataiku Recipe | Description |
|---|---|---|---|
| 1 | Input Data (Tool 1) | Upload dataset `US_Accidents_March23` | Read CSV (46 cols) |
| 2 | Summarize (Tool 2) | `recipe_group_by_timezone.py` | CountDistinct ID grouped by Timezone |
| 3 | Filter IsNotNull (Tool 5) | `recipe_prepare_cleanse.py` | Remove rows with null Timezone |
| 4 | Formula REGEX_Replace (Tool 16) | `recipe_prepare_cleanse.py` | Strip `US/` prefix from Timezone |
| 5 | Cleanse macro (Tool 17) | `recipe_prepare_cleanse.py` | Uppercase Timezone |
| 6 | Batch Macro (`accident-macro.yxmc`) | `recipe_batch_export.py` | Loop over timezones, write per-zone CSV |

**Key mapping:** The Alteryx Batch Macro uses a Control Parameter to iterate over
timezone values `["Eastern", "Central", "Mountain", "Pacific"]`. In Dataiku, this is
replaced with a simple Python for-loop that filters and writes to a managed folder.

---

### Flow 2 — Accident User Input

**Alteryx Source:** `Accident-user-input.yxmd` + `user-input-macro.yxmc`

| Step | Alteryx Tool | Dataiku Recipe | Description |
|---|---|---|---|
| 1 | DateTime (Tool 5) | `recipe_parse_datetime.py` | Parse Start_Time string to datetime |
| 2 | Select (Tool 6) | `recipe_parse_datetime.py` | Rename DateTime_Out → Start_Time |
| 3 | Formula (Tool 3) | `recipe_parse_datetime.py` | Derive Day, Day_type, Hour, EOM, EOPM |
| 4 | Summarize by Day_type (Tool 7) | `recipe_group_daytype.py` | CountDistinct ID by Day_type |
| 5 | Summarize by Hour (Tool 9) | `recipe_group_hour.py` | CountDistinct ID by Hour |
| 6 | User-Input Macro | `recipe_date_filter.py` | Filter by start_date/end_date project vars |
| 7 | Join (Tool 12) | `recipe_join_filtered.py` | Join filtered dates back to enriched data |

**Key mapping:** The Alteryx Analytic Macro uses two Date question widgets that feed
into two chained Filter tools via Action/UpdateValueFormula. In Dataiku, this becomes
`dataiku.get_custom_variables()` to read `start_date` / `end_date` and a simple
pandas filter.

---

### Flow 3 — TED Talk

**Alteryx Source:** `Ted talk Workflow.yxmd` + `TD-input-macro.yxmc`

| Step | Alteryx Tool | Dataiku Recipe | Description |
|---|---|---|---|
| 1 | Formula epoch (Tool 4) | `recipe_epoch_to_datetime.py` | Unix epoch → datetime |
| 2 | Formula Year/Month (Tool 6) | `recipe_epoch_to_datetime.py` | Derive Year, Month, Month_name |
| 3 | Sort + Sample + Sort (Tools 8→10→11) | `recipe_top5_views_per_year.py` | Top 5 by views per year |
| 4 | Summarize + Sort + Formula + RunningTotal + Sample (Tools 15→16→17→18→20) | `recipe_speaker_ranking.py` | Speaker frequency + rank |
| 5 | Summarize + Sort + PlotlyCharting (Tools 24→25→26) | `recipe_monthly_chart.py` | Month-wise line chart |
| 6 | MultiRowFormula (Tool 28) | `recipe_consecutive_years.py` | Consecutive year detection |
| 7 | RegEx (Tool 32) | `recipe_social_entrepreneur.py` | Filter social entrepreneurs |
| 8 | TD-input-macro.yxmc | `recipe_period_filter.py` | MTD/YTD/WTD filter |

**Key mapping:** Five independent analytical branches fed from the same enriched
dataset. The Alteryx `MultiRowFormula` tool is replaced by pandas `groupby().diff()`.

---

### Flow 4 — Superstore Sales

**Alteryx Source:** `New Workflow2.yxmd`

| Step | Alteryx Tool | Dataiku Recipe | Description |
|---|---|---|---|
| 1 | Input + AutoField + Filter (Tools 1→3→5) | `recipe_date_filter_2016.py` | Read XLS, filter to 2016 |
| 2 | Summarize Sum + Sort + Sample + Summarize Min + Summarize GroupBy (Tools 7→9→10→13→20) | `recipe_aggregations.py` | Multi-step aggregation |
| 3 | AppendFields (Tool 26) | `recipe_cross_join.py` | Cross-join sub-cat sums with min |
| 4 | PlotlyCharting (Tool 24) | `recipe_plotly_bar.py` | Bar chart Category vs Sales |
| 5 | ComposerTable + ComposerText + ComposerRender (Tools 22→25→27) | `recipe_pdf_report.py` | PDF report generation |

**Key mapping:** The Alteryx `AppendFields` tool (Cartesian join) is replaced by
`df.assign()`. The `ComposerRender` pipeline is replaced by WeasyPrint HTML→PDF.

---

### Flow 5 — Purchase Cleansing

**Alteryx Source:** `New Workflow1.yxmd`

| Step | Alteryx Tool | Dataiku Recipe | Description |
|---|---|---|---|
| 1 | Input Data (Tool 1) | Upload dataset `purchase_registration` | Read CSV (98 cols, ISO-8859-1) |
| 2 | Cleanse macro (Cleanse.yxmc) | `recipe_cleanse.py` | Trim whitespace, uppercase, fill nulls |

**Key mapping:** The built-in Alteryx Cleanse macro is replaced with a pandas
apply-to-all-string-columns pattern.

---

## Project Variables

These are set in **Project Settings > Variables** and read in recipes via
`dataiku.get_custom_variables()`:

| Variable | Type | Example | Used By |
|---|---|---|---|
| `start_date` | string (YYYY-MM-DD) | `"2021-01-01"` | Flow 2 |
| `end_date` | string (YYYY-MM-DD) | `"2022-01-01"` | Flow 2 |
| `period_type` | string | `"MTD"` / `"YTD"` / `"WTD"` | Flow 3 |

---

## Managed Folders

| Folder ID | Name | Contents |
|---|---|---|
| `accident_zone_exports` | Accident Zone Exports | `EASTERN_accidents.csv`, `CENTRAL_accidents.csv`, `MOUNTAIN_accidents.csv`, `PACIFIC_accidents.csv` |
| `ted_talk_charts` | TED Talk Charts | `monthly_talks_chart.html` |
| `superstore_reports` | Superstore Reports | `superstore_report.pdf` |

---

## Testing

The `tests/` directory contains a pytest-based test suite that validates every
recipe's output against known Alteryx baseline expectations.

### Running Tests Locally

```bash
cd dataiku_migration
pip install pandas plotly weasyprint pytest
pytest tests/ -v
```

### Test Naming Convention

| Prefix | Flow | Example |
|---|---|---|
| `AZ-XX` | Flow 1 (Accident Zone) | `test_az_01_filter_null_timezone` |
| `AU-XX` | Flow 2 (Accident User Input) | `test_au_01_parse_datetime` |
| `TT-XX` | Flow 3 (TED Talk) | `test_tt_01_epoch_conversion` |
| `SS-XX` | Flow 4 (Superstore Sales) | `test_ss_01_date_filter_2016` |
| `PC-XX` | Flow 5 (Purchase Cleansing) | `test_pc_01_trim_whitespace` |
| `R-XX` | Regression | `test_r_01_flow1_end_to_end` |

### Test Fixtures

The `conftest.py` file provides shared fixtures that create small representative
DataFrames mirroring the structure of each source dataset. Tests do **not** require
the full production CSV files — they operate on synthetic data that exercises
every code path.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'dataiku'` | Running outside Dataiku DSS. The recipes include a graceful fallback; tests mock the `dataiku` module. |
| `WeasyPrint` font warnings | Install system fonts: `apt-get install fonts-liberation` |
| CSV encoding errors | Ensure `encoding='iso-8859-1'` is set on the input dataset in Dataiku. |
| `period_type` variable not found | Set the project variable in Dataiku DSS: Project Settings > Variables. |
| Timezone values don't match | The Alteryx workflow strips `US/` and uppercases. Ensure your input has the raw `US/Eastern` etc. format. |
