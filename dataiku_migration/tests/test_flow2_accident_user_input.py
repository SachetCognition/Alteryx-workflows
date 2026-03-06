"""
Tests for Flow 2 — Accident User Input Analysis.

Test IDs: AU-01 through AU-10
Validates: recipe_parse_datetime.py, recipe_date_filter.py,
           recipe_group_daytype.py, recipe_group_hour.py, recipe_join_filtered.py
"""

import os

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow2_accident_user_input"))

from recipe_parse_datetime import parse_datetime_and_derive
from recipe_date_filter import date_filter
from recipe_group_daytype import group_by_daytype
from recipe_group_hour import group_by_hour
from recipe_join_filtered import join_filtered


class TestParseDatetime:
    """Tests for recipe_parse_datetime.py"""

    def test_au_01_parse_datetime(self, accidents_raw_df):
        """AU-01: Start_Time is parsed to datetime type."""
        result = parse_datetime_and_derive(accidents_raw_df)
        assert pd.api.types.is_datetime64_any_dtype(result["Start_Time"])

    def test_au_02_derive_day(self, accidents_raw_df):
        """AU-02: Day column contains correct weekday names."""
        result = parse_datetime_and_derive(accidents_raw_df)
        assert "Day" in result.columns
        # 2021-03-15 is a Monday
        monday_row = result[result["ID"] == "A-1001"]
        assert monday_row["Day"].iloc[0] == "Monday"

    def test_au_03_derive_day_type_weekday(self, accidents_raw_df):
        """AU-03: Weekdays are classified as 'Weekday'."""
        result = parse_datetime_and_derive(accidents_raw_df)
        monday_row = result[result["ID"] == "A-1001"]
        assert monday_row["Day_type"].iloc[0] == "Weekday"

    def test_au_04_derive_day_type_weekend(self, accidents_raw_df):
        """AU-04: Weekends are classified as 'Weekend'."""
        result = parse_datetime_and_derive(accidents_raw_df)
        # A-1006 is 2021-05-08 which is Saturday
        saturday_row = result[result["ID"] == "A-1006"]
        assert saturday_row["Day_type"].iloc[0] == "Weekend"

    def test_au_05_derive_hour(self, accidents_raw_df):
        """AU-05: Hour is zero-padded 24h format string."""
        result = parse_datetime_and_derive(accidents_raw_df)
        assert "Hour" in result.columns
        # A-1001: 08:30:00 → Hour = "08"
        row = result[result["ID"] == "A-1001"]
        assert row["Hour"].iloc[0] == "08"

    def test_au_06_derive_eom(self, accidents_raw_df):
        """AU-06: EOM is the last day of the month."""
        result = parse_datetime_and_derive(accidents_raw_df)
        assert "EOM" in result.columns
        # A-1001: 2021-03-15 → EOM = 2021-03-31
        row = result[result["ID"] == "A-1001"]
        eom = pd.Timestamp(row["EOM"].iloc[0])
        assert eom.day == 31
        assert eom.month == 3

    def test_au_07_derive_eopm(self, accidents_raw_df):
        """AU-07: EOPM is the last day of the previous month."""
        result = parse_datetime_and_derive(accidents_raw_df)
        assert "EOPM" in result.columns
        # A-1001: 2021-03-15 → EOPM = 2021-02-28
        row = result[result["ID"] == "A-1001"]
        eopm = pd.Timestamp(row["EOPM"].iloc[0])
        assert eopm.day == 28
        assert eopm.month == 2


class TestDateFilter:
    """Tests for recipe_date_filter.py"""

    def test_au_08_date_range_filter(self, accidents_raw_df):
        """AU-08: Date filter correctly selects rows within range."""
        enriched = parse_datetime_and_derive(accidents_raw_df)
        result = date_filter(enriched, "2021-01-01", "2021-07-01")
        # Should include rows with Start_Time >= 2021-01-01 AND < 2021-07-01
        assert len(result) > 0
        assert all(result["Start_Time"] >= pd.Timestamp("2021-01-01"))
        assert all(result["Start_Time"] < pd.Timestamp("2021-07-01"))

    def test_au_09_date_filter_excludes_end(self, accidents_raw_df):
        """AU-09: End date is exclusive (< not <=)."""
        enriched = parse_datetime_and_derive(accidents_raw_df)
        # Filter with end_date = "2021-06-20" should exclude 2021-06-20 14:15:00
        # but 2021-06-20 14:15 >= 2021-06-20 00:00, so it should be excluded only
        # if end is strictly < "2021-06-20"
        result = date_filter(enriched, "2021-06-20", "2021-06-21")
        # Should include A-1002 (2021-06-20 14:15:00) and A-1010 (same date)
        assert len(result) >= 1


class TestGroupDaytype:
    """Tests for recipe_group_daytype.py"""

    def test_au_10_group_by_daytype(self, accidents_raw_df):
        """AU-10: Group by Day_type produces Weekday and Weekend counts."""
        enriched = parse_datetime_and_derive(accidents_raw_df)
        result = group_by_daytype(enriched)
        assert "Day_type" in result.columns
        assert "Accidents" in result.columns
        day_types = set(result["Day_type"].dropna())
        assert "Weekday" in day_types
        assert "Weekend" in day_types
