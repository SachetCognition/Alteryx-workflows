# Flow 3 — TED Talk Analysis

## Original Alteryx Workflow

**File:** `Ted talk Workflow.yxmd` + `TD-input-macro.yxmc`

### Alteryx Tool Chain (5 Branches)

```
ted_main.csv (Input Tool 2)
    └─→ Formula (Tool 4): film_date epoch → datetime
            └─→ Formula (Tool 6): Derive Year, Month, Month_name
                    │
                    ├─→ Branch 1: Top 5 Views per Year
                    │   Sort (8) → Sample first 5/Year (10) → Sort Year desc (11)
                    │       └─→ ComposerTable (12) → BrowseV2 (14)
                    │
                    ├─→ Branch 2: Speaker Ranking
                    │   Summarize Count by speaker (15) → Sort desc (16)
                    │       → Formula Rank=1 (17) → RunningTotal (18)
                    │           → Sample first 5 (20)
                    │               └─→ ComposerTable (22) → BrowseV2 (23)
                    │
                    ├─→ Branch 3: Monthly Chart
                    │   Summarize Count by Month/Month_name (24) → Sort Month asc (25)
                    │       └─→ PlotlyCharting (26) → BrowseV2 (27)
                    │
                    ├─→ Branch 4: Consecutive Years
                    │   MultiRowFormula (28): Consecutive year detection by speaker
                    │       └─→ ComposerTable (30) → BrowseV2 (31)
                    │
                    └─→ Branch 5: Social Entrepreneur Filter
                        RegEx (32): .*social entrepreneur.* on speaker_occupation
                            └─→ ComposerTable (34) → BrowseV2 (35)
```

### TD-Input Macro (TD-input-macro.yxmc)

- **DropDown question:** Manual values "MTD", "YTD", "WTD" (lines 315-318)
- **Action tool:** Updates Filter expression based on selection
- Used standalone / reusable across workflows

---

## Dataiku Flow Diagram

```
[ted_main]
    └──→ recipe_epoch_to_datetime.py ──→ [ted_enriched]
                                              │
                                              ├──→ recipe_top5_views_per_year.py ──→ [ted_top5_views_per_year]
                                              │
                                              ├──→ recipe_speaker_ranking.py ──→ [ted_speaker_ranking]
                                              │
                                              ├──→ recipe_monthly_chart.py ──→ [ted_monthly_counts]
                                              │                              └──→ [ted_talk_charts/] (HTML)
                                              │
                                              ├──→ recipe_consecutive_years.py ──→ [ted_consecutive_years]
                                              │
                                              ├──→ recipe_social_entrepreneur.py ──→ [ted_social_entrepreneurs]
                                              │
                                              └──→ recipe_period_filter.py ──→ [ted_period_filtered]
```

---

## Setup Steps

### Datasets

1. **ted_main** — Upload `Datasets/ted_main.csv` (12 columns).
2. **ted_enriched** — Output of `recipe_epoch_to_datetime.py`.
3. **ted_top5_views_per_year** — Output of `recipe_top5_views_per_year.py`.
4. **ted_speaker_ranking** — Output of `recipe_speaker_ranking.py`.
5. **ted_monthly_counts** — Output of `recipe_monthly_chart.py`.
6. **ted_consecutive_years** — Output of `recipe_consecutive_years.py`.
7. **ted_social_entrepreneurs** — Output of `recipe_social_entrepreneur.py`.
8. **ted_period_filtered** — Output of `recipe_period_filter.py`.

### Managed Folder

- **ted_talk_charts** — Stores `monthly_talks_chart.html`.

### Project Variable

```json
{
  "period_type": "MTD"
}
```

### Recipe Wiring

| Recipe | Input(s) | Output(s) |
|---|---|---|
| `recipe_epoch_to_datetime.py` | `ted_main` | `ted_enriched` |
| `recipe_top5_views_per_year.py` | `ted_enriched` | `ted_top5_views_per_year` |
| `recipe_speaker_ranking.py` | `ted_enriched` | `ted_speaker_ranking` |
| `recipe_monthly_chart.py` | `ted_enriched` | `ted_monthly_counts` + `ted_talk_charts` |
| `recipe_consecutive_years.py` | `ted_enriched` | `ted_consecutive_years` |
| `recipe_social_entrepreneur.py` | `ted_enriched` | `ted_social_entrepreneurs` |
| `recipe_period_filter.py` | `ted_enriched` | `ted_period_filtered` |

---

## Business Logic Preserved

| Alteryx Step | Python Equivalent | Validation |
|---|---|---|
| `DateTimeAdd("1970-01-01", ToNumber([film_date]), 'second')` | `pd.to_datetime(int, unit='s')` | Epoch conversion matches |
| `DateTimeYear/Month` + `%B` format | `dt.year`, `dt.month`, `dt.strftime('%B')` | Date components match |
| Sort views desc → Sample 5/Year → Sort Year desc | `sort_values` + `groupby().head(5)` | Top 5 per year match |
| Summarize Count by speaker → Sort → Rank=1 → RunningTotal | `groupby().size()` + `cumsum()` | Ranking matches |
| Summarize by Month/Month_name + PlotlyCharting | `groupby().size()` + `plotly.graph_objects` | Chart config matches |
| MultiRowFormula consecutive detection | `groupby().diff()` | Consecutive flags match |
| RegEx `.*social entrepreneur.*` | `re.compile(pattern, IGNORECASE)` | Filter results match |
| TD-input-macro MTD/YTD/WTD | Date arithmetic + project variable | Period logic matches |
