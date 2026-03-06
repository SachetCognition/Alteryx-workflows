"""
Tests for Flow 5 — Purchase Registration Data Cleansing.

Test IDs: PC-01 through PC-06
Validates: recipe_cleanse.py
"""

import os

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow5_purchase_cleansing"))

from recipe_cleanse import cleanse_dataframe


class TestCleanse:
    """Tests for recipe_cleanse.py"""

    def test_pc_01_trim_whitespace(self, purchase_raw_df):
        """PC-01: Leading and trailing whitespace is stripped from all string columns."""
        result = cleanse_dataframe(purchase_raw_df)
        string_cols = result.select_dtypes(include=["object"]).columns
        for col in string_cols:
            for val in result[col]:
                assert val == val.strip(), f"Column '{col}' has untrimmed value: '{val}'"

    def test_pc_02_uppercase(self, purchase_raw_df):
        """PC-02: All string values are converted to uppercase."""
        result = cleanse_dataframe(purchase_raw_df)
        string_cols = result.select_dtypes(include=["object"]).columns
        for col in string_cols:
            for val in result[col]:
                assert val == val.upper(), f"Column '{col}' has non-uppercase value: '{val}'"

    def test_pc_03_null_filled(self, purchase_raw_df):
        """PC-03: NaN/null values in string columns are replaced with empty string."""
        result = cleanse_dataframe(purchase_raw_df)
        string_cols = result.select_dtypes(include=["object"]).columns
        for col in string_cols:
            assert result[col].isna().sum() == 0, f"Column '{col}' still has nulls"

    def test_pc_04_row_count_preserved(self, purchase_raw_df):
        """PC-04: Number of rows is preserved after cleansing."""
        result = cleanse_dataframe(purchase_raw_df)
        assert len(result) == len(purchase_raw_df)

    def test_pc_05_column_count_preserved(self, purchase_raw_df):
        """PC-05: Number of columns is preserved after cleansing."""
        result = cleanse_dataframe(purchase_raw_df)
        assert len(result.columns) == len(purchase_raw_df.columns)

    def test_pc_06_specific_values(self, purchase_raw_df):
        """PC-06: Specific values are correctly cleansed."""
        result = cleanse_dataframe(purchase_raw_df)
        # "  abc123 " → "ABC123"
        assert result["miro_no"].iloc[0] == "ABC123"
        # "DEF456" → "DEF456" (already uppercase, no whitespace)
        assert result["miro_no"].iloc[1] == "DEF456"
        # None → "" (null filled)
        assert result["miro_no"].iloc[2] == ""
        # " Company A " → "COMPANY A"
        assert result["name"].iloc[0] == "COMPANY A"
        # "company b" → "COMPANY B"
        assert result["name"].iloc[1] == "COMPANY B"
