"""
Tests for Flow 3 — TED Talk Analysis.

Test IDs: TT-01 through TT-10
Validates: recipe_epoch_to_datetime.py, recipe_top5_views_per_year.py,
           recipe_speaker_ranking.py, recipe_monthly_chart.py,
           recipe_consecutive_years.py, recipe_social_entrepreneur.py,
           recipe_period_filter.py
"""

import os
from datetime import datetime

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow3_ted_talk"))

from recipe_epoch_to_datetime import epoch_to_datetime
from recipe_top5_views_per_year import top5_views_per_year
from recipe_speaker_ranking import speaker_ranking
from recipe_monthly_chart import monthly_counts
from recipe_consecutive_years import detect_consecutive_years
from recipe_social_entrepreneur import filter_social_entrepreneurs
from recipe_period_filter import period_filter


class TestEpochToDatetime:
    """Tests for recipe_epoch_to_datetime.py"""

    def test_tt_01_epoch_conversion(self, ted_raw_df):
        """TT-01: film_date is correctly converted from epoch to datetime."""
        result = epoch_to_datetime(ted_raw_df)
        assert pd.api.types.is_datetime64_any_dtype(result["film_date"])
        # 1140825600 = 2006-02-25 00:00:00 UTC
        first_date = result["film_date"].iloc[0]
        assert first_date.year == 2006
        assert first_date.month == 2

    def test_tt_02_year_derivation(self, ted_raw_df):
        """TT-02: Year is correctly derived from film_date."""
        result = epoch_to_datetime(ted_raw_df)
        assert "Year" in result.columns
        assert result["Year"].iloc[0] == 2006

    def test_tt_03_month_derivation(self, ted_raw_df):
        """TT-03: Month is correctly derived as numeric value."""
        result = epoch_to_datetime(ted_raw_df)
        assert "Month" in result.columns
        # First talk: February = month 2
        assert result["Month"].iloc[0] == 2

    def test_tt_04_month_name_derivation(self, ted_raw_df):
        """TT-04: Month_name is the full month name string."""
        result = epoch_to_datetime(ted_raw_df)
        assert "Month_name" in result.columns
        assert result["Month_name"].iloc[0] == "February"


class TestTop5ViewsPerYear:
    """Tests for recipe_top5_views_per_year.py"""

    def test_tt_05_top5_per_year(self, ted_enriched_df):
        """TT-05: Returns at most 5 talks per year, sorted by year desc."""
        result = top5_views_per_year(ted_enriched_df)
        # Check each year has <= 5 entries
        for year, group in result.groupby("Year"):
            assert len(group) <= 5
        # Check sorted by Year descending
        years = result["Year"].tolist()
        # Within same-year blocks, order may vary, but year sequence should be desc
        unique_years = []
        for y in years:
            if not unique_years or y != unique_years[-1]:
                unique_years.append(y)
        assert unique_years == sorted(unique_years, reverse=True)


class TestSpeakerRanking:
    """Tests for recipe_speaker_ranking.py"""

    def test_tt_06_speaker_ranking_top5(self, ted_enriched_df):
        """TT-06: Returns exactly 5 speakers with running rank."""
        result = speaker_ranking(ted_enriched_df)
        assert len(result) == 5
        assert "Count" in result.columns
        assert "main_speaker" in result.columns
        assert "RunTot_Rank" in result.columns

    def test_tt_07_running_rank_sequential(self, ted_enriched_df):
        """TT-07: RunTot_Rank is sequential 1,2,3,4,5."""
        result = speaker_ranking(ted_enriched_df)
        assert result["RunTot_Rank"].tolist() == [1, 2, 3, 4, 5]


class TestMonthlyCounts:
    """Tests for recipe_monthly_chart.py"""

    def test_tt_08_monthly_counts_sorted(self, ted_enriched_df):
        """TT-08: Monthly counts are sorted by Month ascending."""
        result = monthly_counts(ted_enriched_df)
        assert "Month" in result.columns
        assert "Month_name" in result.columns
        assert "Count" in result.columns
        months = result["Month"].tolist()
        assert months == sorted(months)


class TestConsecutiveYears:
    """Tests for recipe_consecutive_years.py"""

    def test_tt_09_consecutive_years_detection(self, ted_enriched_df):
        """TT-09: Consecutive years are detected for speakers with multi-year talks."""
        result = detect_consecutive_years(ted_enriched_df)
        assert "Consecutive" in result.columns
        # Ken Robinson speaks in 2006, 2007, 2008, 2009 → should have "Yes" entries
        ken_rows = result[result["main_speaker"] == "Ken Robinson"]
        assert "Yes" in ken_rows["Consecutive"].values
        # First row per speaker should be empty
        first_ken = ken_rows.iloc[0]
        assert first_ken["Consecutive"] == ""


class TestSocialEntrepreneur:
    """Tests for recipe_social_entrepreneur.py"""

    def test_tt_10_social_entrepreneur_filter(self, ted_enriched_df):
        """TT-10: Regex filter captures 'Social entrepreneur' occupation."""
        result = filter_social_entrepreneurs(ted_enriched_df)
        assert len(result) > 0
        assert "comments_Matched" in result.columns
        assert all(result["comments_Matched"])
        # All filtered rows should contain 'social entrepreneur' in occupation
        for occ in result["speaker_occupation"]:
            assert "social entrepreneur" in str(occ).lower()
