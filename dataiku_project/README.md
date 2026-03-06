# Dataiku Project - Alteryx Workflow Conversion

Python recipe scripts that replicate five Alteryx workflows, designed to run inside
[Dataiku DSS](https://www.dataiku.com/) as Python recipes or standalone with pandas.

---

## Directory Layout

```
dataiku_project/
|-- README.md                              # This file
|-- recipes/
|   |-- workflow1_accident.py              # Accident Workflow
|   |-- workflow2_accident_user_input.py   # Accident User-Input Workflow
|   |-- workflow3_superstore.py            # Superstore Sales Report
|   |-- workflow4_purchase_cleanse.py      # Purchase Registration Cleanse
|   +-- workflow5_ted_talk.py              # TED Talk Analysis
|-- utils/
|   +-- cleanse.py                         # Reusable cleanse utility (Alteryx Cleanse.yxmc)
+-- tests/
    |-- test_workflow1_accident.py
    |-- test_workflow2_accident_user_input.py
    |-- test_workflow3_superstore.py
    |-- test_workflow4_purchase_cleanse.py
    +-- test_workflow5_ted_talk.py
```

---

## Prerequisites

| Package | Required by | Install |
|---------|------------|---------|
| `pandas` | All recipes | `pip install pandas` |
| `numpy` | workflow2, workflow5 | `pip install numpy` |
| `openpyxl` / `xlrd` | workflow3 (Excel) | `pip install openpyxl xlrd` |
| `plotly` | workflow3, workflow5 (charts) | `pip install plotly` |
| `fpdf2` | workflow3 (PDF report) | `pip install fpdf2` |
| `pytest` | Test suite | `pip install pytest` |

Install everything at once:

```bash
pip install pandas numpy openpyxl xlrd plotly fpdf2 pytest
```

---

## Input Datasets

| Workflow | Dataset | Format | Notes |
|----------|---------|--------|-------|
| 1, 2 | `US_Accidents_March23.csv` | CSV (Latin-1) | ~7.7M rows, 46 columns. **Not included in repo** - download separately |
| 3 | `Sample - Superstore.xls` | Excel (sheet: Orders) | **Not included** - standard Tableau sample dataset |
| 4 | `updated1_pur_reg_2200_2300.csv` | CSV (Latin-1) | 80+ columns. **Not included** |
| 5 | `Datasets/ted_main.csv` | CSV (Latin-1) | 2,476 rows, 12 columns. **Included in repo** |

---

## Running Standalone (outside Dataiku)

Each recipe can be run as a standalone Python script. Configure input paths via
environment variables or let them default to `../../Datasets/<filename>`:

```bash
# Example: Run the TED Talk workflow
cd dataiku_project/recipes
python workflow5_ted_talk.py

# Override input path
INPUT_TED_CSV=/path/to/ted_main.csv python workflow5_ted_talk.py

# Run with custom output directory
OUTPUT_DIR=/tmp/ted_output python workflow5_ted_talk.py
```

### Environment Variables

| Variable | Default | Used by |
|----------|---------|---------|
| `INPUT_ACCIDENTS_CSV` | `../../Datasets/US_Accidents_March23.csv` | workflow1, workflow2 |
| `INPUT_SUPERSTORE_XLS` | `../../Datasets/Sample - Superstore.xls` | workflow3 |
| `INPUT_PURCHASE_CSV` | `../../Datasets/updated1_pur_reg_2200_2300.csv` | workflow4 |
| `INPUT_TED_CSV` | `../../Datasets/ted_main.csv` | workflow5 |
| `OUTPUT_DIR` | `../output` | workflow1, workflow3, workflow5 |
| `START_DATE` | `2023-01-01` | workflow2 (date filter start) |
| `END_DATE` | `2023-01-31` | workflow2 (date filter end) |

---

## Setting Up in Dataiku DSS

### 1. Create Datasets

Upload each input file as a Dataiku managed dataset matching the names used
in the recipes (e.g., `US_Accidents_March23`, `Superstore_Orders`,
`updated1_pur_reg_2200_2300`, `ted_main`).

### 2. Create Output Datasets

Create empty managed datasets for each output:

- **Workflow 1**: `accident_summary`, `accident_cleansed`
- **Workflow 2**: `accident_by_day_type`, `accident_by_hour`, `accident_date_filtered`
- **Workflow 3**: `superstore_filtered`, `superstore_total_sales`, `superstore_top5`,
  `superstore_min_sales`, `superstore_subcategory_sales`
- **Workflow 4**: `purchase_cleansed`
- **Workflow 5**: `ted_enriched`, `ted_top_viewed_per_year`, `ted_speaker_frequency`,
  `ted_monthly_frequency`, `ted_consecutive_years`, `ted_social_entrepreneurs`

### 3. Create Python Recipes

For each workflow, create a new Python recipe in Dataiku:

1. Set the appropriate input dataset(s) as recipe inputs
2. Set the output dataset(s) as recipe outputs
3. Paste the recipe code from `recipes/workflow<N>_*.py`
4. Upload `utils/cleanse.py` to the project library (`lib/python/utils/cleanse.py`)
5. Run the recipe

### 4. Install Dependencies

In Dataiku's code environment, ensure `pandas`, `numpy`, `plotly`, and `fpdf2`
are available. You can add them via **Administration > Code Envs**.

---

## Running Tests

Tests use **pytest** and generate synthetic data (no real datasets required):

```bash
cd dataiku_project
python -m pytest tests/ -v
```

Run a single workflow's tests:

```bash
python -m pytest tests/test_workflow5_ted_talk.py -v
```

---

## Workflow Mapping

| Alteryx Workflow | Python Recipe | Key Outputs |
|-----------------|--------------|-------------|
| `Accident Workflow.yxmd` | `workflow1_accident.py` | Summary by timezone, per-timezone CSVs |
| `Accident-user-input.yxmd` | `workflow2_accident_user_input.py` | Day type stats, hourly stats, date-filtered data |
| `New Workflow2.yxmd` | `workflow3_superstore.py` | Filtered sales, top 5, chart, PDF report |
| `New Workflow1.yxmd` | `workflow4_purchase_cleanse.py` | Cleansed purchase data |
| `Ted talk Workflow.yxmd` | `workflow5_ted_talk.py` | Enriched data, top talks, speaker stats, charts |
