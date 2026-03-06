"""
Dataiku Python Recipe: Purchase Registration Cleanse
Replicates Alteryx workflow "New Workflow1.yxmd"

Connection graph:
  Input(1) -> Cleanse(3) -> Browse(2)

Input:  updated1_pur_reg_2200_2300.csv
Output: purchase_cleansed
"""

import os
import sys

import pandas as pd

try:
    import dataiku

    RUNNING_IN_DATAIKU = True
except ImportError:
    RUNNING_IN_DATAIKU = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.cleanse import cleanse_dataframe  # noqa: E402

# ── Configuration ──────────────────────────────────────────────────────────
INPUT_CSV = os.environ.get(
    "INPUT_PURCHASE_CSV",
    os.path.join(
        os.path.dirname(__file__), "..", "..", "Datasets", "updated1_pur_reg_2200_2300.csv"
    ),
)

# All 80+ columns from the purchase registration dataset
PURCHASE_COLUMNS = [
    "miro_no", "posting_dt", "miro_acc", "doc_dt", "referance", "vendor", "name",
    "material_code", "description", "plant", "quantity1", "purchasing_unit",
    "base_amount", "net_amount", "h_and_f", "pack_and_fw", "freight",
    "central_gst", "state_gst", "integrated_gst", "other", "tcs",
    "with_hold_tax", "total_amt", "bill_amount", "po_no", "profit_center",
    "tax_code", "gst_rate", "qty", "net_taxable_value", "tax_code_desc",
    "vendor_gst_no", "asset_no", "asset_class", "asset_class_name",
    "g_l_account_no", "g_l_acc_descr", "miro_hsn", "material_master_hsn",
    "incl_before_tax_amount", "inc_sgst", "inc_cgst", "inc_igst",
    "registration_details", "ean_upc", "pr_item", "pr_no", "state_code",
    "state", "vendor_category", "text", "city", "doc_typ", "indentification",
    "description_of_material_type", "invoice_flag", "base_unit", "company",
    "year", "contact_no", "currency", "currency_1", "currency_2",
    "item_category", "material_type", "pan_no", "po_type", "entry_date",
    "email_id", "plant_gst_no", "place_of_supply", "acc_assignment_cate",
    "contractor_a_c", "exch_rate", "pur_return", "custom_duty",
    "asset_description", "total_tax_amt_inc", "utgst", "rcm_pay_cgst",
    "rcm_pay_sgst", "rcm_pay_igst", "rcm_pay_ugst", "business_place",
    "cess", "entry_tax", "excise", "hedcess", "inc_utgst", "internal_order",
    "reduction_3", "serv_ecs", "serv_hecs", "serv_tax", "storage_location",
    "storage_location_description", "swachha_bharat_tax", "tax_amt", "vat",
    "po_hsn",
]


def run(input_path: str | None = None) -> dict[str, pd.DataFrame]:
    """Execute the full Purchase Registration Cleanse pipeline.

    Parameters
    ----------
    input_path : str | None
        Path to the updated1_pur_reg_2200_2300.csv file.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with the ``purchase_cleansed`` DataFrame.
    """
    input_path = input_path or INPUT_CSV

    # ── Step 1: Input (ToolID 1) ───────────────────────────────────────────
    # Read CSV with all columns as string, Latin-1 encoding
    if RUNNING_IN_DATAIKU:
        df = dataiku.Dataset("updated1_pur_reg_2200_2300").get_dataframe()
    else:
        df = pd.read_csv(input_path, dtype=str, encoding="latin-1")

    # ── Step 2: Cleanse (ToolID 3) ─────────────────────────────────────────
    # Apply to ALL columns with:
    #   Check Box (84)=True  -> trim whitespace
    #   Check Box (117)=True -> remove null rows
    #   Check Box (15)=True  -> modify case
    #   Drop Down (81)=upper -> uppercase
    all_columns = list(df.columns)
    purchase_cleansed = cleanse_dataframe(
        df,
        columns=all_columns,
        remove_whitespace=True,
        remove_nulls=True,
        uppercase=True,
    )

    # ── Write Dataiku output dataset ───────────────────────────────────────
    if RUNNING_IN_DATAIKU:
        dataiku.Dataset("purchase_cleansed").write_with_schema(purchase_cleansed)

    return {
        "purchase_cleansed": purchase_cleansed,
    }


if __name__ == "__main__":
    outputs = run()
    df = outputs["purchase_cleansed"]
    print(f"=== purchase_cleansed ({len(df)} rows, {len(df.columns)} cols) ===")
    print(f"Columns: {list(df.columns)}")
    print(df.head(5).to_string(index=False))
