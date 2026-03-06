"""
Comprehensive test suite for Workflow 3: Superstore Sales Report.

Tests cover schema validation, business logic, and data integrity
using synthetic data (no real datasets required).
"""

import os
import sys
from datetime import date

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_synthetic_superstore(n=100):
    """Create synthetic Superstore orders data."""
    rng = np.random.default_rng(77)
    categories = ["Furniture", "Office Supplies", "Technology"]
    sub_categories = {
        "Furniture": ["Chairs", "Tables", "Bookcases"],
        "Office Supplies": ["Paper", "Binders", "Pens"],
        "Technology": ["Phones", "Accessories", "Copiers"],
    }
    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    segments = ["Consumer", "Corporate", "Home Office"]
    regions = ["East", "West", "Central", "South"]

    records = []
    for i in range(n):
        cat = categories[i % len(categories)]
        sub_cat = sub_categories[cat][i % len(sub_categories[cat])]
        year = 2015 + (i % 4)
        month = 1 + (i % 12)
        day = 1 + (i % 28)
        order_date = f"{year}-{month:02d}-{day:02d}"
        ship_date = f"{year}-{month:02d}-{min(day + 3, 28):02d}"

        records.append({
            "Row ID": i + 1,
            "Order ID": f"CA-{year}-{i:06d}",
            "Order Date": order_date,
            "Ship Date": ship_date,
            "Ship Mode": ship_modes[i % len(ship_modes)],
            "Customer ID": f"CG-{i % 20:05d}",
            "Customer Name": f"Customer {i % 20}",
            "Segment": segments[i % len(segments)],
            "Country": "United States",
            "City": "Test City",
            "State": "California",
            "Postal Code": 90210 + (i % 100),
            "Region": regions[i % len(regions)],
            "Product ID": f"OFF-{cat[:3].upper()}-{i:06d}",
            "Category": cat,
            "Sub-Category": sub_cat,
            "Product Name": f"Product {i}",
            "Sales": round(float(rng.uniform(50, 20000)), 2),
            "Quantity": int(rng.integers(1, 15)),
            "Discount": round(float(rng.uniform(0, 0.5)), 2),
            "Profit": round(float(rng.uniform(-500, 5000)), 2),
        })
    return pd.DataFrame(records)


@pytest.fixture
def synthetic_xls(tmp_path):
    """Write synthetic data to an Excel file and return its path."""
    df = _make_synthetic_superstore()
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])
    path = tmp_path / "Sample - Superstore.xlsx"
    df.to_excel(str(path), sheet_name="Orders", index=False, engine="openpyxl")
    return str(path)


@pytest.fixture
def workflow_outputs(synthetic_xls, tmp_path):
    """Run workflow 3 and return (outputs_dict, output_dir)."""
    from recipes.workflow3_superstore import run

    output_dir = str(tmp_path / "output")
    outputs = run(input_path=synthetic_xls, output_dir=output_dir)
    return outputs, output_dir


# =========================================================================
# Schema Validation Tests
# =========================================================================

class TestSchemaValidation:
    """T3.1-T3.7: Schema and type validation."""

    def test_t3_1_filtered_contains_order_date(self, workflow_outputs):
        """T3.1: superstore_filtered contains Order Date column."""
        outputs, _ = workflow_outputs
        assert "Order Date" in outputs["superstore_filtered"].columns

    def test_t3_2_total_sales_single_row(self, workflow_outputs):
        """T3.2: superstore_total_sales has exactly 1 row with Sum_Sales."""
        outputs, _ = workflow_outputs
        total_sales = outputs["superstore_total_sales"]
        assert len(total_sales) == 1
        assert "Sum_Sales" in total_sales.columns

    def test_t3_3_top5_has_at_most_5_rows(self, workflow_outputs):
        """T3.3: superstore_top5 has at most 5 rows."""
        outputs, _ = workflow_outputs
        assert len(outputs["superstore_top5"]) <= 5

    def test_t3_4_min_sales_single_row(self, workflow_outputs):
        """T3.4: superstore_min_sales has exactly 1 row with Min_Sales."""
        outputs, _ = workflow_outputs
        min_sales = outputs["superstore_min_sales"]
        assert len(min_sales) == 1
        assert "Min_Sales" in min_sales.columns

    def test_t3_5_subcategory_sales_columns(self, workflow_outputs):
        """T3.5: superstore_subcategory_sales has expected columns."""
        outputs, _ = workflow_outputs
        sub_sales = outputs["superstore_subcategory_sales"]
        required_cols = {"Sub-Category", "Sum_Sales", "Min_Sum_Sales"}
        assert required_cols.issubset(set(sub_sales.columns))

    def test_t3_6_sales_is_numeric(self, workflow_outputs):
        """T3.6: Sales column in filtered output is numeric."""
        outputs, _ = workflow_outputs
        filtered = outputs["superstore_filtered"]
        assert pd.api.types.is_numeric_dtype(filtered["Sales"])

    def test_t3_7_output_keys_present(self, workflow_outputs):
        """T3.7: All expected output keys are present."""
        outputs, _ = workflow_outputs
        expected_keys = {
            "superstore_filtered",
            "superstore_total_sales",
            "superstore_top5",
            "superstore_min_sales",
            "superstore_subcategory_sales",
        }
        assert expected_keys.issubset(set(outputs.keys()))


# =========================================================================
# Business Logic Tests
# =========================================================================

class TestBusinessLogic:
    """T3.8-T3.15: Business logic validation."""

    def test_t3_8_filter_date_range(self, workflow_outputs):
        """T3.8: All filtered rows have Order Date in 2016-01-01..2017-01-01."""
        outputs, _ = workflow_outputs
        filtered = outputs["superstore_filtered"]
        for _, row in filtered.iterrows():
            order_date = row["Order Date"]
            assert order_date.date() >= date(2016, 1, 1)
            assert order_date.date() <= date(2017, 1, 1)

    def test_t3_9_total_sales_matches_sum(self, workflow_outputs):
        """T3.9: Sum_Sales equals sum of filtered Sales."""
        outputs, _ = workflow_outputs
        filtered = outputs["superstore_filtered"]
        total = outputs["superstore_total_sales"]
        expected_sum = filtered["Sales"].astype(float).sum()
        assert abs(total["Sum_Sales"].iloc[0] - expected_sum) < 0.01

    def test_t3_10_top5_sorted_descending(self, workflow_outputs):
        """T3.10: Top 5 are the highest Sales values from filtered data."""
        outputs, _ = workflow_outputs
        top5 = outputs["superstore_top5"]
        filtered = outputs["superstore_filtered"]
        expected_top5 = filtered.nlargest(5, "Sales")["Sales"].values
        actual_top5 = top5["Sales"].values
        np.testing.assert_array_almost_equal(
            sorted(actual_top5, reverse=True),
            sorted(expected_top5, reverse=True),
            decimal=2,
        )

    def test_t3_11_min_sales_from_top5(self, workflow_outputs):
        """T3.11: Min_Sales is the minimum Sales from top5."""
        outputs, _ = workflow_outputs
        top5 = outputs["superstore_top5"]
        min_sales = outputs["superstore_min_sales"]
        assert abs(min_sales["Min_Sales"].iloc[0] - top5["Sales"].min()) < 0.01

    def test_t3_12_subcategory_aggregation_on_top5(self, workflow_outputs):
        """T3.12: Subcategory sales are computed from top5 only."""
        outputs, _ = workflow_outputs
        top5 = outputs["superstore_top5"]
        sub_sales = outputs["superstore_subcategory_sales"]
        assert abs(sub_sales["Sum_Sales"].sum() - top5["Sales"].sum()) < 0.01

    def test_t3_13_min_sum_sales_is_cross_joined(self, workflow_outputs):
        """T3.13: Min_Sum_Sales is the same value in all rows."""
        outputs, _ = workflow_outputs
        sub_sales = outputs["superstore_subcategory_sales"]
        min_vals = sub_sales["Min_Sum_Sales"].unique()
        assert len(min_vals) == 1

    def test_t3_14_min_sum_sales_matches_min_of_subcategory(self, workflow_outputs):
        """T3.14: Min_Sum_Sales equals the minimum of Sum_Sales."""
        outputs, _ = workflow_outputs
        sub_sales = outputs["superstore_subcategory_sales"]
        expected_min = sub_sales["Sum_Sales"].min()
        actual_min = sub_sales["Min_Sum_Sales"].iloc[0]
        assert abs(actual_min - expected_min) < 0.01

    def test_t3_15_report_file_exists(self, workflow_outputs):
        """T3.15: Report file is generated in output directory."""
        _, output_dir = workflow_outputs
        pdf_path = os.path.join(output_dir, "superstore_report.pdf")
        html_path = os.path.join(output_dir, "superstore_report.html")
        assert os.path.exists(pdf_path) or os.path.exists(html_path)


# =========================================================================
# Data Integrity Tests
# =========================================================================

class TestDataIntegrity:
    """T3.16-T3.18: Data integrity validation."""

    def test_t3_16_no_rows_outside_date_range(self, workflow_outputs):
        """T3.16: No rows in filtered output with dates outside range."""
        outputs, _ = workflow_outputs
        filtered = outputs["superstore_filtered"]
        outside = filtered[
            (filtered["Order Date"].dt.date < date(2016, 1, 1))
            | (filtered["Order Date"].dt.date > date(2017, 1, 1))
        ]
        assert len(outside) == 0

    def test_t3_17_top5_is_subset_of_filtered(self, workflow_outputs):
        """T3.17: Top 5 records are a subset of the filtered dataset."""
        outputs, _ = workflow_outputs
        top5 = outputs["superstore_top5"]
        filtered = outputs["superstore_filtered"]
        for sale in top5["Sales"].values:
            assert sale in filtered["Sales"].values

    def test_t3_18_subcategory_names_from_top5(self, workflow_outputs):
        """T3.18: Sub-Category names in subcategory_sales are from top5."""
        outputs, _ = workflow_outputs
        top5 = outputs["superstore_top5"]
        sub_sales = outputs["superstore_subcategory_sales"]
        top5_subcats = set(top5["Sub-Category"].unique())
        actual_subcats = set(sub_sales["Sub-Category"].unique())
        assert actual_subcats.issubset(top5_subcats)
