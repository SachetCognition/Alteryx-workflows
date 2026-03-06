"""
Comprehensive test suite for Workflow 4: Purchase Registration Cleanse.

Tests cover schema validation, business logic, and data integrity
using synthetic data (no real datasets required).
"""

import os
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

EXPECTED_COLUMNS = [
    "miro_no", "posting_dt", "miro_acc", "doc_dt", "referance", "vendor",
    "name", "material_code", "description", "plant", "quantity1",
    "purchasing_unit", "base_amount", "net_amount", "h_and_f", "pack_and_fw",
    "freight", "central_gst", "state_gst", "integrated_gst", "other", "tcs",
    "with_hold_tax", "total_amt", "bill_amount", "po_no", "profit_center",
    "tax_code", "gst_rate", "qty",
]


def _make_synthetic_purchase(n=50):
    """Create synthetic purchase registration data."""
    rng = np.random.default_rng(55)
    records = []

    for i in range(n):
        record = {}
        for col in EXPECTED_COLUMNS:
            if col in ("quantity1", "base_amount", "net_amount", "total_amt",
                       "bill_amount", "qty", "gst_rate"):
                record[col] = str(round(float(rng.uniform(1, 10000)), 2))
            elif col == "posting_dt":
                record[col] = f"2023-{1 + (i % 12):02d}-{1 + (i % 28):02d}"
            elif col == "vendor":
                record[col] = f"  vendor_{i:03d}  "
            elif col == "name":
                if i % 10 == 0:
                    record[col] = ""
                else:
                    record[col] = f"  name {i}  "
            elif col == "description":
                record[col] = f"  item Description {i}  "
            else:
                record[col] = f"val_{i}"
        records.append(record)

    # Add rows where ALL columns are empty/NaN to test remove_nulls
    all_empty_row = {col: "" for col in EXPECTED_COLUMNS}
    records.append(all_empty_row)
    all_nan_row = {col: np.nan for col in EXPECTED_COLUMNS}
    records.append(all_nan_row)

    return pd.DataFrame(records)


@pytest.fixture
def synthetic_csv(tmp_path):
    """Write synthetic data to a CSV and return its path."""
    df = _make_synthetic_purchase()
    path = tmp_path / "updated1_pur_reg_2200_2300.csv"
    df.to_csv(path, index=False, encoding="latin-1")
    return str(path)


@pytest.fixture
def workflow_outputs(synthetic_csv):
    """Run workflow 4 and return outputs dict."""
    from recipes.workflow4_purchase_cleanse import run

    return run(input_path=synthetic_csv)


# =========================================================================
# Schema Validation Tests
# =========================================================================

class TestSchemaValidation:
    """T4.1-T4.4: Schema and type validation."""

    def test_t4_1_output_has_same_columns_as_input(
        self, workflow_outputs, synthetic_csv
    ):
        """T4.1: Output has the same columns as input."""
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        cleansed = workflow_outputs["purchase_cleansed"]
        assert list(cleansed.columns) == list(df_input.columns)

    def test_t4_2_all_columns_present(self, workflow_outputs):
        """T4.2: All expected columns are present in the output."""
        cleansed = workflow_outputs["purchase_cleansed"]
        for col in EXPECTED_COLUMNS:
            assert col in cleansed.columns, f"Column '{col}' not found"

    def test_t4_3_output_is_dataframe(self, workflow_outputs):
        """T4.3: Output is a pandas DataFrame."""
        cleansed = workflow_outputs["purchase_cleansed"]
        assert isinstance(cleansed, pd.DataFrame)

    def test_t4_4_output_key_name(self, workflow_outputs):
        """T4.4: Output dictionary contains purchase_cleansed key."""
        assert "purchase_cleansed" in workflow_outputs


# =========================================================================
# Business Logic Tests
# =========================================================================

class TestBusinessLogic:
    """T4.5-T4.11: Business logic validation."""

    def test_t4_5_whitespace_trimmed(self, workflow_outputs):
        """T4.5: Leading/trailing whitespace is trimmed from string cols."""
        cleansed = workflow_outputs["purchase_cleansed"]
        str_cols = [c for c in cleansed.columns if cleansed[c].dtype == object]
        for col in str_cols:
            for val in cleansed[col].dropna():
                assert val == val.strip(), (
                    f"Column '{col}' has untrimmed value: '{val}'"
                )

    def test_t4_6_uppercase_applied(self, workflow_outputs):
        """T4.6: All string columns are converted to uppercase."""
        cleansed = workflow_outputs["purchase_cleansed"]
        str_cols = [c for c in cleansed.columns if cleansed[c].dtype == object]
        for col in str_cols:
            for val in cleansed[col].dropna():
                assert val == val.upper(), (
                    f"Column '{col}' has non-uppercase value: '{val}'"
                )

    def test_t4_7_all_null_rows_removed(self, workflow_outputs, synthetic_csv):
        """T4.7: Rows where ALL columns are null/empty are removed."""
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        cleansed = workflow_outputs["purchase_cleansed"]
        assert len(cleansed) < len(df_input)

    def test_t4_8_non_null_rows_preserved(self, workflow_outputs):
        """T4.8: Rows with at least one non-null value are preserved."""
        cleansed = workflow_outputs["purchase_cleansed"]
        assert len(cleansed) == 50

    def test_t4_9_partial_null_rows_kept(self, workflow_outputs):
        """T4.9: Rows with some null/empty values but not ALL are kept."""
        cleansed = workflow_outputs["purchase_cleansed"]
        assert len(cleansed) > 0

    def test_t4_10_cleanse_idempotent(self, synthetic_csv):
        """T4.10: Running cleanse twice produces the same result."""
        from recipes.workflow4_purchase_cleanse import run

        first_run = run(input_path=synthetic_csv)
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="w"
        ) as f:
            tmp_path = f.name
        first_run["purchase_cleansed"].to_csv(
            tmp_path, index=False, encoding="latin-1"
        )
        second_run = run(input_path=tmp_path)
        os.unlink(tmp_path)

        pd.testing.assert_frame_equal(
            first_run["purchase_cleansed"].reset_index(drop=True),
            second_run["purchase_cleansed"].reset_index(drop=True),
        )

    def test_t4_11_vendor_whitespace_trimmed(self, workflow_outputs):
        """T4.11: Vendor column specifically has whitespace trimmed."""
        cleansed = workflow_outputs["purchase_cleansed"]
        if "vendor" in cleansed.columns:
            for val in cleansed["vendor"].dropna():
                assert not val.startswith(" ")
                assert not val.endswith(" ")


# =========================================================================
# Data Integrity Tests
# =========================================================================

class TestDataIntegrity:
    """T4.12-T4.15: Data integrity validation."""

    def test_t4_12_no_all_null_rows_remain(self, workflow_outputs):
        """T4.12: No rows remain where all columns are null/empty."""
        cleansed = workflow_outputs["purchase_cleansed"]
        for idx, row in cleansed.iterrows():
            all_null = True
            for col in cleansed.columns:
                val = row[col]
                if pd.notna(val) and str(val).strip() != "":
                    all_null = False
                    break
            assert not all_null, f"Row {idx} has all null/empty values"

    def test_t4_13_column_count_unchanged(self, workflow_outputs, synthetic_csv):
        """T4.13: Number of columns is unchanged after cleansing."""
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        cleansed = workflow_outputs["purchase_cleansed"]
        assert len(cleansed.columns) == len(df_input.columns)

    def test_t4_14_row_count_decreased_by_null_rows(
        self, workflow_outputs, synthetic_csv
    ):
        """T4.14: Row count decreased by the number of all-null rows."""
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        cleansed = workflow_outputs["purchase_cleansed"]
        null_mask = pd.DataFrame()
        for col in df_input.columns:
            if df_input[col].dtype == object:
                null_mask[col] = (
                    df_input[col].isna() | (df_input[col].str.strip() == "")
                )
            else:
                null_mask[col] = df_input[col].isna()
        all_null_count = null_mask.all(axis=1).sum()
        assert len(cleansed) == len(df_input) - all_null_count

    def test_t4_15_description_values_uppercased(self, workflow_outputs):
        """T4.15: Description column values are all uppercase and trimmed."""
        cleansed = workflow_outputs["purchase_cleansed"]
        if "description" in cleansed.columns:
            for val in cleansed["description"].dropna():
                assert val == val.upper().strip()
