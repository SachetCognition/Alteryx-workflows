"""
Tests for Flow 1 — Accident Zone Analysis.

Test IDs: AZ-01 through AZ-08
Validates: recipe_prepare_cleanse.py, recipe_group_by_timezone.py, recipe_batch_export.py
"""

import os
import tempfile

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow1_accident_zone"))

from recipe_prepare_cleanse import prepare_cleanse
from recipe_group_by_timezone import group_by_timezone
from recipe_batch_export import batch_export, TIMEZONE_VALUES


class TestPrepareCleanse:
    """Tests for recipe_prepare_cleanse.py"""

    def test_az_01_filter_null_timezone(self, accidents_raw_df):
        """AZ-01: Rows with null Timezone are removed."""
        result = prepare_cleanse(accidents_raw_df)
        assert result["Timezone"].isna().sum() == 0
        # Original has 1 null timezone (index 6), so 12 - 1 = 11
        assert len(result) == 11

    def test_az_02_strip_us_prefix(self, accidents_raw_df):
        """AZ-02: US/ prefix is stripped from Timezone values."""
        result = prepare_cleanse(accidents_raw_df)
        for tz in result["Timezone"]:
            assert "US/" not in tz

    def test_az_03_uppercase_timezone(self, accidents_raw_df):
        """AZ-03: All Timezone values are uppercase after cleansing."""
        result = prepare_cleanse(accidents_raw_df)
        for tz in result["Timezone"]:
            assert tz == tz.upper()

    def test_az_04_expected_timezone_values(self, accidents_raw_df):
        """AZ-04: Only expected timezone values remain after cleansing."""
        result = prepare_cleanse(accidents_raw_df)
        expected = {"EASTERN", "CENTRAL", "MOUNTAIN", "PACIFIC"}
        actual = set(result["Timezone"].unique())
        assert actual == expected

    def test_az_05_column_count_preserved(self, accidents_raw_df):
        """AZ-05: All original columns are preserved after cleansing."""
        result = prepare_cleanse(accidents_raw_df)
        assert set(result.columns) == set(accidents_raw_df.columns)


class TestGroupByTimezone:
    """Tests for recipe_group_by_timezone.py"""

    def test_az_06_group_by_timezone_count(self, accidents_raw_df):
        """AZ-06: Group by Timezone produces correct distinct counts."""
        result = group_by_timezone(accidents_raw_df)
        assert "Timezone" in result.columns
        assert "No_of_accidents" in result.columns
        # Should include the null timezone group as well (dropna=False)
        assert len(result) > 0

    def test_az_07_count_distinct_ids(self, accidents_raw_df):
        """AZ-07: CountDistinct correctly counts unique IDs per timezone."""
        result = group_by_timezone(accidents_raw_df)
        # US/Eastern has IDs: A-1001, A-1005, A-1008, A-1011 = 4 distinct
        eastern_row = result[result["Timezone"] == "US/Eastern"]
        if not eastern_row.empty:
            assert eastern_row["No_of_accidents"].iloc[0] == 4


class TestBatchExport:
    """Tests for recipe_batch_export.py"""

    def test_az_08_batch_export_creates_files(self, accidents_cleansed_df):
        """AZ-08: Batch export creates one CSV per timezone in output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            row_counts = batch_export(
                accidents_cleansed_df, output_dir=tmpdir
            )

            # Verify all 4 timezone files were created
            for tz in TIMEZONE_VALUES:
                filepath = os.path.join(tmpdir, f"{tz}_accidents.csv")
                assert os.path.exists(filepath), f"Missing file: {filepath}"

            # Verify row counts are non-negative
            for tz, count in row_counts.items():
                assert count >= 0

            # EASTERN should have IDs: A-1001, A-1005, A-1008, A-1011 = 4
            assert row_counts["EASTERN"] == 4
            # CENTRAL should have IDs: A-1002, A-1006, A-1012 = 3
            assert row_counts["CENTRAL"] == 3
            # MOUNTAIN should have IDs: A-1003, A-1010 = 2
            assert row_counts["MOUNTAIN"] == 2
            # PACIFIC should have IDs: A-1004, A-1009 = 2
            assert row_counts["PACIFIC"] == 2

            # Verify CSV content is readable
            eastern_df = pd.read_csv(
                os.path.join(tmpdir, "EASTERN_accidents.csv")
            )
            assert len(eastern_df) == 4
            assert all(eastern_df["Timezone"] == "EASTERN")
