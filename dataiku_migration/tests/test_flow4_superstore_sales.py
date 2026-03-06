"""
Tests for Flow 4 — Superstore Sales Analysis.

Test IDs: SS-01 through SS-11
Validates: recipe_date_filter_2016.py, recipe_aggregations.py,
           recipe_cross_join.py, recipe_plotly_bar.py, recipe_pdf_report.py
"""

import os
import tempfile

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow4_superstore_sales"))

from recipe_date_filter_2016 import date_filter_2016
from recipe_aggregations import (
    compute_total_sales,
    compute_top5,
    compute_min_sales,
    compute_subcategory_sales,
)
from recipe_cross_join import cross_join
from recipe_pdf_report import (
    build_styled_table_html,
    build_text_block,
)


class TestDateFilter2016:
    """Tests for recipe_date_filter_2016.py"""

    def test_ss_01_date_filter_2016(self, superstore_raw_df):
        """SS-01: Only orders between 2016-01-01 and 2017-01-01 are kept."""
        result = date_filter_2016(superstore_raw_df)
        assert len(result) > 0
        assert all(result["Order Date"] >= pd.Timestamp("2016-01-01"))
        assert all(result["Order Date"] <= pd.Timestamp("2017-01-01"))

    def test_ss_02_excludes_2015(self, superstore_raw_df):
        """SS-02: Orders from 2015 are excluded."""
        result = date_filter_2016(superstore_raw_df)
        # Row with Order Date 2015-11-08 should be excluded
        dates_2015 = result[result["Order Date"] < pd.Timestamp("2016-01-01")]
        assert len(dates_2015) == 0

    def test_ss_03_includes_boundary(self, superstore_raw_df):
        """SS-03: Order on 2017-01-01 is included (<=)."""
        result = date_filter_2016(superstore_raw_df)
        boundary = result[result["Order Date"] == pd.Timestamp("2017-01-01")]
        assert len(boundary) == 1


class TestAggregations:
    """Tests for recipe_aggregations.py"""

    def test_ss_04_total_sales(self, superstore_raw_df):
        """SS-04: Total sales sum is computed correctly."""
        filtered = date_filter_2016(superstore_raw_df)
        total = compute_total_sales(filtered)
        assert "Sum_Sales" in total.columns
        assert len(total) == 1
        expected = filtered["Sales"].sum()
        assert abs(total["Sum_Sales"].iloc[0] - expected) < 0.01

    def test_ss_05_top5_by_sales(self, superstore_raw_df):
        """SS-05: Top 5 rows by Sales are returned."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        assert len(top5) == 5
        # Verify sorted descending
        sales_values = top5["Sales"].tolist()
        assert sales_values == sorted(sales_values, reverse=True)

    def test_ss_06_min_sales_from_top5(self, superstore_raw_df):
        """SS-06: Minimum sales from top 5 is correct."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        min_df = compute_min_sales(top5)
        assert "Min_Sum_Sales" in min_df.columns
        assert min_df["Min_Sum_Sales"].iloc[0] == top5["Sales"].min()

    def test_ss_07_subcategory_groupby(self, superstore_raw_df):
        """SS-07: Sub-Category groupby produces correct aggregation."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        subcat = compute_subcategory_sales(top5)
        assert "Sub-Category" in subcat.columns
        assert "Sum_Sales" in subcat.columns
        # Total of sub-category sums should equal top5 total
        assert abs(subcat["Sum_Sales"].sum() - top5["Sales"].sum()) < 0.01


class TestCrossJoin:
    """Tests for recipe_cross_join.py"""

    def test_ss_08_cross_join_appends_min(self, superstore_raw_df):
        """SS-08: Cross join appends Min_Sum_Sales to every row."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        min_df = compute_min_sales(top5)
        subcat = compute_subcategory_sales(top5)

        result = cross_join(subcat, min_df)
        assert "Min_Sum_Sales" in result.columns
        assert all(result["Min_Sum_Sales"] == min_df["Min_Sum_Sales"].iloc[0])
        assert len(result) == len(subcat)

    def test_ss_09_cross_join_preserves_data(self, superstore_raw_df):
        """SS-09: Original Sub-Category and Sum_Sales data is preserved."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        min_df = compute_min_sales(top5)
        subcat = compute_subcategory_sales(top5)

        result = cross_join(subcat, min_df)
        assert set(result["Sub-Category"]) == set(subcat["Sub-Category"])


class TestPdfReport:
    """Tests for recipe_pdf_report.py"""

    def test_ss_10_styled_table_html(self, superstore_raw_df):
        """SS-10: Styled table HTML contains orange highlight on min row."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        min_df = compute_min_sales(top5)
        subcat = compute_subcategory_sales(top5)
        joined = cross_join(subcat, min_df)

        html = build_styled_table_html(joined)
        assert "#ff8040" in html
        assert "<table" in html
        assert "Sub-Category" in html

    def test_ss_11_text_block(self, superstore_raw_df):
        """SS-11: Text block lists each Sub-Category with sales amount."""
        filtered = date_filter_2016(superstore_raw_df)
        top5 = compute_top5(filtered)
        min_df = compute_min_sales(top5)
        subcat = compute_subcategory_sales(top5)
        joined = cross_join(subcat, min_df)

        text = build_text_block(joined)
        for _, row in joined.iterrows():
            assert row["Sub-Category"] in text
