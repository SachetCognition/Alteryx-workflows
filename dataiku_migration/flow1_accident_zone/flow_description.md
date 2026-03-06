# Flow 1 — Accident Zone Analysis

## Original Alteryx Workflow

**File:** `Accident Workflow.yxmd` + `accident-macro.yxmc`

### Alteryx Tool Chain

```
US_Accidents_March23.csv (Input Tool 1)
    ├─→ Summarize (Tool 2): CountDistinct(ID) by Timezone
    │       └─→ BrowseV2 (Tool 4): inspect summary
    │
    └─→ Filter (Tool 5): !IsNull([Timezone])
            └─→ Formula (Tool 16): REGEX_Replace([Timezone], "US/", " ")
                    └─→ Cleanse Macro (Tool 17): Uppercase Timezone
                            ├─→ BrowseV2 (Tool 7): inspect cleansed
                            └─→ accident-macro.yxmc (Batch Macro)
                                    └─→ Per-timezone CSV outputs
```

### Batch Macro Detail (accident-macro.yxmc)

The batch macro runs once per timezone value:
- **Control Parameter (Tool 5):** receives one timezone string per iteration
- **Action (Tool 6):** updates Filter (Tool 3) expression to `[Zone] = "{tz}"`
- **Action (Tool 8):** updates Output Data (Tool 4) file path with timezone name
- **TextInput values:** Eastern, Central, Mountain, Pacific

---

## Dataiku Flow Diagram

```
[US_Accidents_March23] ──→ recipe_prepare_cleanse.py ──→ [accidents_cleansed]
                      │                                         │
                      │                                         └──→ recipe_batch_export.py ──→ [accident_zone_exports/]
                      │                                                  (EASTERN_accidents.csv)
                      │                                                  (CENTRAL_accidents.csv)
                      │                                                  (MOUNTAIN_accidents.csv)
                      │                                                  (PACIFIC_accidents.csv)
                      │
                      └──→ recipe_group_by_timezone.py ──→ [accidents_by_timezone]
```

---

## Setup Steps

### Datasets

1. **US_Accidents_March23** — Upload `US_Accidents_March23.csv` as a new dataset
   (46 columns, ISO-8859-1 encoding, comma delimiter).
2. **accidents_cleansed** — Create as output of `recipe_prepare_cleanse.py`.
3. **accidents_by_timezone** — Create as output of `recipe_group_by_timezone.py`.

### Managed Folder

- **accident_zone_exports** — Create a managed folder. `recipe_batch_export.py`
  writes four CSV files here.

### Recipe Wiring

| Recipe | Input(s) | Output(s) |
|---|---|---|
| `recipe_prepare_cleanse.py` | `US_Accidents_March23` | `accidents_cleansed` |
| `recipe_group_by_timezone.py` | `US_Accidents_March23` | `accidents_by_timezone` |
| `recipe_batch_export.py` | `accidents_cleansed` | `accident_zone_exports` (folder) |

---

## Business Logic Preserved

| Alteryx Step | Python Equivalent | Validation |
|---|---|---|
| `!IsNull([Timezone])` | `df.dropna(subset=["Timezone"])` | Row counts match |
| `REGEX_Replace([Timezone], "US/", " ")` | `re.sub(r"US/", " ", tz).strip()` | String values match |
| Cleanse → uppercase | `.str.upper()` | All uppercase confirmed |
| Batch Macro per-zone filter | `df[df["Timezone"] == tz]` | Per-zone row counts match |
| MultiFile CSV output | `folder.upload_stream(filename, ...)` | File names match pattern |
