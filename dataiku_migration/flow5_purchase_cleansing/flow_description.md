# Flow 5 — Purchase Registration Data Cleansing

## Original Alteryx Workflow

**File:** `New Workflow1.yxmd`

### Alteryx Tool Chain

```
updated1_pur_reg_2200_2300.csv (Input Tool 1)
    └─→ Cleanse Macro (Cleanse.yxmc)
            └─→ BrowseV2 (Tool 3)
```

This is the simplest workflow in the repository — a two-step pipeline that
reads a 98-column CSV and runs it through the built-in Alteryx Cleanse macro.

### Input File Details

- **File:** `updated1_pur_reg_2200_2300.csv`
- **Encoding:** ISO-8859-1 (CodePage 28591)
- **Columns:** 98 (all V_String type in Alteryx)
- **Key columns include:** miro_no, posting_dt, vendor, name, material_code,
  description, plant, quantity1, base_amount, net_amount, tax_code, gst_rate,
  vendor_gst_no, asset_no, asset_class, g_l_account_no, etc.

### Cleanse Macro Operations

The built-in Cleanse.yxmc macro applies to all string columns:
1. **Trim whitespace** — Remove leading/trailing spaces
2. **Uppercase** — Convert all characters to uppercase
3. **Null handling** — Replace null/empty values with empty string

---

## Dataiku Flow Diagram

```
[purchase_registration]
    └──→ recipe_cleanse.py ──→ [purchase_cleansed]
```

---

## Setup Steps

### Datasets

1. **purchase_registration** — Upload `updated1_pur_reg_2200_2300.csv`
   (set encoding to ISO-8859-1 in the dataset settings).
2. **purchase_cleansed** — Output of `recipe_cleanse.py`.

### Recipe Wiring

| Recipe | Input(s) | Output(s) |
|---|---|---|
| `recipe_cleanse.py` | `purchase_registration` | `purchase_cleansed` |

---

## Business Logic Preserved

| Alteryx Step | Python Equivalent | Validation |
|---|---|---|
| Cleanse: trim whitespace | `str.strip()` | No leading/trailing spaces |
| Cleanse: uppercase | `str.upper()` | All uppercase confirmed |
| Cleanse: null → empty | `fillna("")` | No null values in output |
| 98 columns processed | `select_dtypes(include=['object'])` | All string cols covered |
