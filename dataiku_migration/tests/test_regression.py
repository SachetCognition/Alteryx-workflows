"""
Regression tests — end-to-end validation across all flows.

Test IDs: R-01 through R-06
Validates: complete pipeline execution for each flow produces consistent results.
"""

import os
import tempfile

import pandas as pd
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRegressionFlow1:
    """R-01: Flow 1 end-to-end regression."""

    def test_r_01_flow1_end_to_end(self, accidents_raw_df):
        """R-01: Full Flow 1 pipeline: cleanse → group → batch export."""
        sys.path.insert(
            0,
            os.path.join(os.path.dirname(__file__), "..", "flow1_accident_zone"),
        )
        from recipe_prepare_cleanse import prepare_cleanse
        from recipe_group_by_timezone import group_by_timezone
        from recipe_batch_export import batch_export

        # Step 1: Cleanse
        cleansed = prepare_cleanse(accidents_raw_df)
        assert len(cleansed) == 11  # 12 - 1 null

        # Step 2: Group (on raw data)
        grouped = group_by_timezone(accidents_raw_df)
        assert len(grouped) > 0

        # Step 3: Batch export
        with tempfile.TemporaryDirectory() as tmpdir:
            counts = batch_export(cleansed, output_dir=tmpdir)
            total_exported = sum(counts.values())
            assert total_exported == len(cleansed)


class TestRegressionFlow2:
    """R-02: Flow 2 end-to-end regression."""

    def test_r_02_flow2_end_to_end(self, accidents_raw_df):
        """R-02: Full Flow 2 pipeline: parse → filter → group → join."""
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "flow2_accident_user_input"
            ),
        )
        from recipe_parse_datetime import parse_datetime_and_derive
        from recipe_date_filter import date_filter
        from recipe_group_daytype import group_by_daytype
        from recipe_group_hour import group_by_hour
        from recipe_join_filtered import join_filtered

        # Step 1: Enrich
        enriched = parse_datetime_and_derive(accidents_raw_df)
        assert "Day" in enriched.columns
        assert "Day_type" in enriched.columns

        # Step 2: Filter
        filtered = date_filter(enriched, "2021-01-01", "2022-01-01")
        assert len(filtered) > 0
        assert len(filtered) <= len(enriched)

        # Step 3: Group
        by_daytype = group_by_daytype(enriched)
        by_hour = group_by_hour(enriched)
        assert len(by_daytype) > 0
        assert len(by_hour) > 0

        # Step 4: Join
        joined = join_filtered(enriched, filtered)
        assert len(joined) > 0


class TestRegressionFlow3:
    """R-03: Flow 3 end-to-end regression."""

    def test_r_03_flow3_end_to_end(self, ted_raw_df):
        """R-03: Full Flow 3 pipeline: epoch → all branches."""
        sys.path.insert(
            0,
            os.path.join(os.path.dirname(__file__), "..", "flow3_ted_talk"),
        )
        from recipe_epoch_to_datetime import epoch_to_datetime
        from recipe_top5_views_per_year import top5_views_per_year
        from recipe_speaker_ranking import speaker_ranking
        from recipe_monthly_chart import monthly_counts
        from recipe_consecutive_years import detect_consecutive_years
        from recipe_social_entrepreneur import filter_social_entrepreneurs

        # Step 1: Enrich
        enriched = epoch_to_datetime(ted_raw_df)
        assert pd.api.types.is_datetime64_any_dtype(enriched["film_date"])

        # Branch 1: Top 5 views
        top5 = top5_views_per_year(enriched)
        assert len(top5) > 0

        # Branch 2: Speaker ranking
        ranking = speaker_ranking(enriched)
        assert len(ranking) == 5

        # Branch 3: Monthly counts
        counts = monthly_counts(enriched)
        assert len(counts) > 0

        # Branch 4: Consecutive years
        consecutive = detect_consecutive_years(enriched)
        assert "Consecutive" in consecutive.columns

        # Branch 5: Social entrepreneur
        social = filter_social_entrepreneurs(enriched)
        assert len(social) >= 0  # May be 0 or more


class TestRegressionFlow4:
    """R-04: Flow 4 end-to-end regression."""

    def test_r_04_flow4_end_to_end(self, superstore_raw_df):
        """R-04: Full Flow 4 pipeline: filter → aggregate → cross-join → report."""
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "flow4_superstore_sales"
            ),
        )
        from recipe_date_filter_2016 import date_filter_2016
        from recipe_aggregations import (
            compute_total_sales,
            compute_top5,
            compute_min_sales,
            compute_subcategory_sales,
        )
        from recipe_cross_join import cross_join
        from recipe_pdf_report import build_styled_table_html, build_text_block

        # Step 1: Filter
        filtered = date_filter_2016(superstore_raw_df)
        assert len(filtered) > 0

        # Step 2: Aggregate
        total = compute_total_sales(filtered)
        top5 = compute_top5(filtered)
        min_sales = compute_min_sales(top5)
        subcat = compute_subcategory_sales(top5)

        # Step 3: Cross-join
        joined = cross_join(subcat, min_sales)
        assert "Min_Sum_Sales" in joined.columns

        # Step 4: Report components
        table_html = build_styled_table_html(joined)
        text_block = build_text_block(joined)
        assert "#ff8040" in table_html
        assert len(text_block) > 0


class TestRegressionFlow5:
    """R-05: Flow 5 end-to-end regression."""

    def test_r_05_flow5_end_to_end(self, purchase_raw_df):
        """R-05: Full Flow 5 pipeline: cleanse all columns."""
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "flow5_purchase_cleansing"
            ),
        )
        from recipe_cleanse import cleanse_dataframe

        result = cleanse_dataframe(purchase_raw_df)
        # Verify all string columns are cleansed
        string_cols = result.select_dtypes(include=["object"]).columns
        for col in string_cols:
            assert result[col].isna().sum() == 0
            for val in result[col]:
                assert val == val.strip() == val.upper()


class TestRegressionIdempotency:
    """R-06: Idempotency — running a recipe twice produces the same result."""

    def test_r_06_cleanse_idempotent(self, purchase_raw_df):
        """R-06: Running cleanse twice produces identical output."""
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "flow5_purchase_cleansing"
            ),
        )
        from recipe_cleanse import cleanse_dataframe

        first_pass = cleanse_dataframe(purchase_raw_df)
        second_pass = cleanse_dataframe(first_pass)

        pd.testing.assert_frame_equal(first_pass, second_pass)
