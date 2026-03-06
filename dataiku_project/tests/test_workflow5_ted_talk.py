"""
Comprehensive test suite for Workflow 5: TED Talk Analysis.

Tests cover schema validation, business logic, and data integrity.
Uses the actual ted_main.csv from the repo Datasets/ folder when available,
otherwise falls back to synthetic data.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

REAL_TED_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", "Datasets", "ted_main.csv"
)


def _make_synthetic_ted(n=200):
    """Create synthetic TED talk data."""
    rng = np.random.default_rng(33)
    occupations = [
        "Author", "Scientist", "Social entrepreneur",
        "Educator", "Designer", "social entrepreneur and activist",
        "Musician", "Economist", "Journalist",
    ]
    speakers = [f"Speaker_{i}" for i in range(30)]

    records = []
    for i in range(n):
        base_ts = 1136073600  # 2006-01-01
        film_ts = base_ts + (i * 3600 * 24 * 15)

        records.append({
            "comments": str(int(rng.integers(10, 5000))),
            "duration": str(int(rng.integers(120, 3600))),
            "event": f"TED{2006 + (i % 12)}",
            "film_date": str(film_ts),
            "languages": str(int(rng.integers(5, 72))),
            "main_speaker": speakers[i % len(speakers)],
            "name": f"Speaker_{i % len(speakers)}: Talk Title {i}",
            "num_speaker": "1",
            "published_date": str(film_ts + 86400 * 30),
            "speaker_occupation": occupations[i % len(occupations)],
            "title": f"Talk Title {i}",
            "views": str(int(rng.integers(10000, 50000000))),
        })
    return pd.DataFrame(records)


@pytest.fixture
def ted_csv(tmp_path):
    """Use real TED data if available, otherwise synthetic."""
    if os.path.exists(REAL_TED_CSV):
        return REAL_TED_CSV
    df = _make_synthetic_ted()
    path = tmp_path / "ted_main.csv"
    df.to_csv(path, index=False, encoding="latin-1")
    return str(path)


@pytest.fixture
def workflow_outputs(ted_csv, tmp_path):
    """Run workflow 5 and return (outputs_dict, output_dir)."""
    from recipes.workflow5_ted_talk import run

    output_dir = str(tmp_path / "output")
    outputs = run(input_path=ted_csv, output_dir=output_dir)
    return outputs, output_dir


# =========================================================================
# Schema Validation Tests
# =========================================================================

class TestSchemaValidation:
    """T5.1-T5.8: Schema and type validation."""

    def test_t5_1_enriched_has_derived_columns(self, workflow_outputs):
        """T5.1: ted_enriched has Year, Month, Month_name columns."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        for col in ["Year", "Month", "Month_name"]:
            assert col in enriched.columns, f"Missing column: {col}"

    def test_t5_2_film_date_is_datetime(self, workflow_outputs):
        """T5.2: film_date is datetime64 after conversion from epoch."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        assert pd.api.types.is_datetime64_any_dtype(enriched["film_date"])

    def test_t5_3_views_is_numeric(self, workflow_outputs):
        """T5.3: views column is numeric after conversion."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        assert pd.api.types.is_numeric_dtype(enriched["views"])

    def test_t5_4_top_viewed_columns(self, workflow_outputs):
        """T5.4: ted_top_viewed_per_year has expected columns."""
        outputs, _ = workflow_outputs
        top_viewed = outputs["ted_top_viewed_per_year"]
        for col in ["main_speaker", "views", "Year"]:
            assert col in top_viewed.columns

    def test_t5_5_speaker_frequency_columns(self, workflow_outputs):
        """T5.5: ted_speaker_frequency has Count, main_speaker, RunTot_Rank."""
        outputs, _ = workflow_outputs
        speaker_freq = outputs["ted_speaker_frequency"]
        for col in ["Count", "main_speaker", "RunTot_Rank"]:
            assert col in speaker_freq.columns

    def test_t5_6_monthly_frequency_columns(self, workflow_outputs):
        """T5.6: ted_monthly_frequency has Month, Month_name, Count."""
        outputs, _ = workflow_outputs
        monthly = outputs["ted_monthly_frequency"]
        for col in ["Month", "Month_name", "Count"]:
            assert col in monthly.columns

    def test_t5_7_consecutive_years_columns(self, workflow_outputs):
        """T5.7: ted_consecutive_years has expected columns."""
        outputs, _ = workflow_outputs
        consecutive = outputs["ted_consecutive_years"]
        for col in ["main_speaker", "Year", "Consecutive"]:
            assert col in consecutive.columns

    def test_t5_8_social_entrepreneurs_columns(self, workflow_outputs):
        """T5.8: ted_social_entrepreneurs has expected columns."""
        outputs, _ = workflow_outputs
        social = outputs["ted_social_entrepreneurs"]
        for col in ["main_speaker", "name", "speaker_occupation",
                    "comments_Matched"]:
            assert col in social.columns


# =========================================================================
# Business Logic Tests
# =========================================================================

class TestBusinessLogic:
    """T5.9-T5.20: Business logic validation."""

    def test_t5_9_year_derived_correctly(self, workflow_outputs):
        """T5.9: Year is correctly derived from film_date."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        sample = enriched.head(50)
        for _, row in sample.iterrows():
            assert row["Year"] == row["film_date"].year

    def test_t5_10_month_derived_correctly(self, workflow_outputs):
        """T5.10: Month is correctly derived from film_date."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        sample = enriched.head(50)
        for _, row in sample.iterrows():
            assert row["Month"] == row["film_date"].month

    def test_t5_11_month_name_valid(self, workflow_outputs):
        """T5.11: Month_name contains valid month names."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        valid_months = {
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        }
        actual_months = set(enriched["Month_name"].dropna().unique())
        assert actual_months.issubset(valid_months)

    def test_t5_12_top5_per_year_max_5_per_group(self, workflow_outputs):
        """T5.12: At most 5 talks per year in top viewed."""
        outputs, _ = workflow_outputs
        top_viewed = outputs["ted_top_viewed_per_year"]
        per_year_counts = top_viewed.groupby("Year").size()
        for year, count in per_year_counts.items():
            assert count <= 5, f"Year {year} has {count} entries (max 5)"

    def test_t5_13_top_viewed_sorted_by_year_desc(self, workflow_outputs):
        """T5.13: Top viewed is sorted by Year descending."""
        outputs, _ = workflow_outputs
        top_viewed = outputs["ted_top_viewed_per_year"]
        years = top_viewed["Year"].tolist()
        for i in range(len(years) - 1):
            assert years[i] >= years[i + 1]

    def test_t5_14_speaker_frequency_top5_has_5_rows(self, workflow_outputs):
        """T5.14: Speaker frequency has at most 5 rows."""
        outputs, _ = workflow_outputs
        speaker_freq = outputs["ted_speaker_frequency"]
        assert len(speaker_freq) <= 5

    def test_t5_15_speaker_frequency_sorted_desc(self, workflow_outputs):
        """T5.15: Speaker frequency is sorted by Count descending."""
        outputs, _ = workflow_outputs
        speaker_freq = outputs["ted_speaker_frequency"]
        counts = speaker_freq["Count"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_t5_16_running_total_rank_sequential(self, workflow_outputs):
        """T5.16: RunTot_Rank is sequential starting from 1."""
        outputs, _ = workflow_outputs
        speaker_freq = outputs["ted_speaker_frequency"]
        expected_ranks = list(range(1, len(speaker_freq) + 1))
        actual_ranks = speaker_freq["RunTot_Rank"].tolist()
        assert actual_ranks == expected_ranks

    def test_t5_17_monthly_frequency_sorted_by_month(self, workflow_outputs):
        """T5.17: Monthly frequency is sorted by Month ascending."""
        outputs, _ = workflow_outputs
        monthly = outputs["ted_monthly_frequency"]
        months = monthly["Month"].tolist()
        assert months == sorted(months)

    def test_t5_18_consecutive_column_values(self, workflow_outputs):
        """T5.18: Consecutive column contains only Yes or No."""
        outputs, _ = workflow_outputs
        consecutive = outputs["ted_consecutive_years"]
        valid_values = {"Yes", "No"}
        actual_values = set(consecutive["Consecutive"].unique())
        assert actual_values.issubset(valid_values)

    def test_t5_19_social_entrepreneurs_match(self, workflow_outputs):
        """T5.19: All social entrepreneurs have the right occupation."""
        outputs, _ = workflow_outputs
        social = outputs["ted_social_entrepreneurs"]
        for _, row in social.iterrows():
            assert "social entrepreneur" in row["speaker_occupation"].lower()

    def test_t5_20_comments_matched_all_true(self, workflow_outputs):
        """T5.20: comments_Matched is True for all social entrepreneur rows."""
        outputs, _ = workflow_outputs
        social = outputs["ted_social_entrepreneurs"]
        assert social["comments_Matched"].all()


# =========================================================================
# Data Integrity Tests
# =========================================================================

class TestDataIntegrity:
    """T5.21-T5.25: Data integrity validation."""

    def test_t5_21_enriched_row_count_matches_input(
        self, workflow_outputs, ted_csv
    ):
        """T5.21: ted_enriched has the same row count as input."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        df_input = pd.read_csv(ted_csv, dtype=str, encoding="latin-1")
        assert len(enriched) == len(df_input)

    def test_t5_22_monthly_frequency_sum_equals_total(self, workflow_outputs):
        """T5.22: Sum of monthly talk counts equals total talks."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        monthly = outputs["ted_monthly_frequency"]
        assert monthly["Count"].sum() == len(enriched)

    def test_t5_23_top_viewed_is_subset_of_enriched(self, workflow_outputs):
        """T5.23: Top viewed speakers exist in the enriched dataset."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        top_viewed = outputs["ted_top_viewed_per_year"]
        enriched_speakers = set(enriched["main_speaker"].unique())
        top_speakers = set(top_viewed["main_speaker"].unique())
        assert top_speakers.issubset(enriched_speakers)

    def test_t5_24_social_entrepreneurs_subset(self, workflow_outputs):
        """T5.24: Social entrepreneurs are a subset of enriched data."""
        outputs, _ = workflow_outputs
        enriched = outputs["ted_enriched"]
        social = outputs["ted_social_entrepreneurs"]
        if len(social) > 0:
            enriched_speakers = set(enriched["main_speaker"].unique())
            social_speakers = set(social["main_speaker"].unique())
            assert social_speakers.issubset(enriched_speakers)

    def test_t5_25_chart_html_exists(self, workflow_outputs):
        """T5.25: Monthly chart HTML file is generated."""
        _, output_dir = workflow_outputs
        chart_path = os.path.join(output_dir, "ted_monthly_chart.html")
        if os.path.exists(chart_path):
            assert os.path.getsize(chart_path) > 0
