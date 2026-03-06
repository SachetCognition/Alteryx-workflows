# Flow 2 — Accident User Input Analysis

## Original Alteryx Workflow

**File:** `Accident-user-input.yxmd` + `user-input-macro.yxmc`

### Alteryx Tool Chain

```
US_Accidents_March23.csv (Input Tool 1)
    └─→ DateTime (Tool 5): Start_Time string → datetime
            └─→ Select (Tool 6): Rename DateTime_Out → Start_Time
                    └─→ Formula (Tool 3): Derive Day, Day_type, Hour, EOM, EOPM
                            ├─→ BrowseV2 (Tool 4): inspect enriched data
                            │
                            ├─→ Summarize (Tool 7): CountDistinct(ID) by Day_type
                            │       └─→ BrowseV2 (Tool 8)
                            │
                            ├─→ Summarize (Tool 9): CountDistinct(ID) by Hour
                            │       └─→ Sort (Tool 10) desc
                            │               └─→ BrowseV2 (Tool 11)
                            │
                            └─→ Join (Tool 12) ←── user-input-macro.yxmc
                                    └─→ BrowseV2 (Tool 13)
```

### User-Input Macro Detail (user-input-macro.yxmc)

- **Date Question (D6):** "Select Start Date" → feeds Action A7
- **Date Question (D8):** "Select End Date" → feeds Action A9
- **Action A7:** UpdateValueFormula on Filter 3 → `[User_input] >= StartDate`
- **Action A9:** UpdateValueFormula on Filter 4 → `[User_input] < EndDate`
- **Lines 286-312:** Two chained filters with date range logic

---

## Dataiku Flow Diagram

```
[US_Accidents_March23]
    └──→ recipe_parse_datetime.py ──→ [accidents_enriched]
                                            │
                                            ├──→ recipe_group_daytype.py ──→ [accidents_by_daytype]
                                            │
                                            ├──→ recipe_group_hour.py ──→ [accidents_by_hour]
                                            │
                                            ├──→ recipe_date_filter.py ──→ [accidents_date_filtered]
                                            │                                    │
                                            └──→ recipe_join_filtered.py ←───────┘
                                                    └──→ [accidents_joined]
```

---

## Setup Steps

### Datasets

1. **US_Accidents_March23** — Same input as Flow 1.
2. **accidents_enriched** — Output of `recipe_parse_datetime.py`.
3. **accidents_by_daytype** — Output of `recipe_group_daytype.py`.
4. **accidents_by_hour** — Output of `recipe_group_hour.py`.
5. **accidents_date_filtered** — Output of `recipe_date_filter.py`.
6. **accidents_joined** — Output of `recipe_join_filtered.py`.

### Project Variables

Set in **Project Settings > Variables**:

```json
{
  "start_date": "2021-01-01",
  "end_date": "2022-01-01"
}
```

### Recipe Wiring

| Recipe | Input(s) | Output(s) |
|---|---|---|
| `recipe_parse_datetime.py` | `US_Accidents_March23` | `accidents_enriched` |
| `recipe_group_daytype.py` | `accidents_enriched` | `accidents_by_daytype` |
| `recipe_group_hour.py` | `accidents_enriched` | `accidents_by_hour` |
| `recipe_date_filter.py` | `accidents_enriched` | `accidents_date_filtered` |
| `recipe_join_filtered.py` | `accidents_enriched`, `accidents_date_filtered` | `accidents_joined` |

---

## Business Logic Preserved

| Alteryx Step | Python Equivalent | Validation |
|---|---|---|
| DateTime tool `yyyy-MM-dd hh:mm:ss` | `pd.to_datetime(format='%Y-%m-%d %H:%M:%S')` | Parsed dates match |
| Day = `DateTimeFormat(%A)` | `dt.day_name()` | Day names match |
| Day_type weekday/weekend logic | `classify_day()` with set lookup | Classification matches |
| Hour = `DateTimeFormat(%H)` | `dt.strftime('%H')` | Zero-padded hours match |
| EOM = `DateTimeTrim(lastofmonth)` | `to_period('M').to_timestamp('M')` | Last-of-month dates match |
| EOPM = first-of-month minus 1 day | `to_timestamp() - Timedelta(days=1)` | End-of-prev-month matches |
| User-input macro date filters | `df[(Start_Time >= start) & (Start_Time < end)]` | Row counts match |
