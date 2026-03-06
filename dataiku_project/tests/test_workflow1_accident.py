"""
Comprehensive test suite for Workflow 1: Accident Workflow.

Tests cover schema validation, business logic, and data integrity
using synthetic data (no real datasets required).
"""

import os

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers – build synthetic accident data
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "ID", "Source", "Severity", "Start_Time", "End_Time", "Start_Lat",
    "Start_Lng", "End_Lat", "End_Lng", "Distance(mi)", "Description",
    "Street", "City", "County", "State", "Zipcode", "Country", "Timezone",
    "Airport_Code", "Weather_Timestamp", "Temperature(F)", "Wind_Chill(F)",
    "Humidity(%)", "Pressure(in)", "Visibility(mi)", "Wind_Direction",
    "Wind_Speed(mph)", "Precipitation(in)", "Weather_Condition", "Amenity",
    "Bump", "Crossing", "Give_Way", "Junction", "No_Exit", "Railway",
    "Roundabout", "Station", "Stop", "Traffic_Calming", "Traffic_Signal",
    "Turning_Loop", "Sunrise_Sunset", "Civil_Twilight", "Nautical_Twilight",
    "Astronomical_Twilight",
]


def _make_synthetic_data(n: int = 200) -> pd.DataFrame:
    """Create a synthetic DataFrame mimicking US_Accidents_March23.csv."""
    rng = np.random.default_rng(42)
    timezones = ["US/Eastern", "US/Central", "US/Mountain", "US/Pacific", None, ""]

    records = []
    for i in range(n):
        tz = rng.choice(timezones)
        records.append({
            "ID": f"A-{i:05d}",
            "Source": "Source2",
            "Severity": str(rng.integers(1, 5)),
            "Start_Time": "2023-01-15 08:30:00",
            "End_Time": "2023-01-15 09:00:00",
            "Start_Lat": str(rng.uniform(25, 48)),
            "Start_Lng": str(rng.uniform(-125, -70)),
            "End_Lat": "",
            "End_Lng": "",
            "Distance(mi)": str(rng.uniform(0, 10)),
            "Description": "Test accident",
            "Street": "Main St",
            "City": "TestCity",
            "County": "TestCounty",
            "State": "CA",
            "Zipcode": "90210",
            "Country": "US",
            "Timezone": tz if tz is not None else np.nan,
            "Airport_Code": "LAX",
            "Weather_Timestamp": "2023-01-15 08:30:00",
            "Temperature(F)": str(rng.uniform(20, 100)),
            "Wind_Chill(F)": str(rng.uniform(10, 80)),
            "Humidity(%)": str(rng.uniform(0, 100)),
            "Pressure(in)": str(rng.uniform(28, 32)),
            "Visibility(mi)": str(rng.uniform(0, 10)),
            "Wind_Direction": "N",
            "Wind_Speed(mph)": str(rng.uniform(0, 50)),
            "Precipitation(in)": str(rng.uniform(0, 2)),
            "Weather_Condition": "Clear",
            "Amenity": "False",
            "Bump": "False",
            "Crossing": "False",
            "Give_Way": "False",
            "Junction": "False",
            "No_Exit": "False",
            "Railway": "False",
            "Roundabout": "False",
            "Station": "False",
            "Stop": "False",
            "Traffic_Calming": "False",
            "Traffic_Signal": "False",
            "Turning_Loop": "False",
            "Sunrise_Sunset": "Day",
            "Civil_Twilight": "Day",
            "Nautical_Twilight": "Day",
            "Astronomical_Twilight": "Day",
        })
    return pd.DataFrame(records)


@pytest.fixture
def synthetic_csv(tmp_path):
    """Write synthetic data to a CSV and return its path."""
    df = _make_synthetic_data()
    path = tmp_path / "US_Accidents_March23.csv"
    df.to_csv(path, index=False, encoding="latin-1")
    return str(path)


@pytest.fixture
def workflow_outputs(synthetic_csv, tmp_path):
    """Run workflow 1 and return outputs."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from recipes.workflow1_accident import run

    output_dir = str(tmp_path / "output")
    return run(input_path=synthetic_csv, output_dir=output_dir), output_dir


# ═══════════════════════════════════════════════════════════════════════════
# Schema Validation Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSchemaValidation:
    """T1.1–T1.5: Schema and type validation."""

    def test_t1_1_input_has_46_columns(self, synthetic_csv):
        """T1.1: Input CSV has exactly 46 columns with correct names."""
        df = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        assert len(df.columns) == 46
        assert list(df.columns) == EXPECTED_COLUMNS

    def test_t1_2_summary_has_correct_columns(self, workflow_outputs):
        """T1.2: accident_summary has exactly 2 columns: Timezone, No_of_accidents."""
        outputs, _ = workflow_outputs
        summary = outputs["accident_summary"]
        assert list(summary.columns) == ["Timezone", "No_of_accidents"]

    def test_t1_3_no_of_accidents_is_integer(self, workflow_outputs):
        """T1.3: No_of_accidents is integer type."""
        outputs, _ = workflow_outputs
        summary = outputs["accident_summary"]
        assert pd.api.types.is_integer_dtype(summary["No_of_accidents"])

    def test_t1_4_timezone_is_uppercase(self, workflow_outputs):
        """T1.4: Timezone column in cleansed output is all uppercase."""
        outputs, _ = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        for tz in cleansed["Timezone"].dropna():
            assert tz == tz.upper(), f"Timezone '{tz}' is not uppercase"

    def test_t1_5_per_timezone_csvs_use_dot_delimiter(self, workflow_outputs):
        """T1.5: Per-timezone output CSVs use '.' as delimiter."""
        _, output_dir = workflow_outputs
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        assert len(csv_files) > 0, "No per-timezone CSV files found"
        for csv_file in csv_files:
            with open(os.path.join(output_dir, csv_file), "r", encoding="latin-1") as f:
                header = f.readline().strip()
                # Dot delimiter means columns separated by dots
                assert "." in header, f"File {csv_file} does not use '.' delimiter"


# ═══════════════════════════════════════════════════════════════════════════
# Business Logic Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestBusinessLogic:
    """T1.6–T1.12: Business logic validation."""

    def test_t1_6_sum_accidents_equals_total_distinct_ids(self, workflow_outputs, synthetic_csv):
        """T1.6: Sum of No_of_accidents across timezones equals distinct IDs with a Timezone value."""
        outputs, _ = workflow_outputs
        summary = outputs["accident_summary"]
        df = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        # pandas groupby drops NaN keys by default, so the summary only
        # counts IDs that have a non-null, non-empty Timezone.
        df_with_tz = df[df["Timezone"].notna() & (df["Timezone"].str.strip() != "")]
        expected = df_with_tz["ID"].nunique()
        assert summary["No_of_accidents"].sum() == expected

    def test_t1_7_no_nulls_in_cleansed_timezone(self, workflow_outputs):
        """T1.7: No null values in Timezone column after filter step."""
        outputs, _ = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        assert cleansed["Timezone"].isna().sum() == 0
        assert (cleansed["Timezone"].str.strip() == "").sum() == 0

    def test_t1_8_no_us_prefix_in_timezone(self, workflow_outputs):
        """T1.8: Timezone column contains no 'US/' prefix after regex replace."""
        outputs, _ = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        for tz in cleansed["Timezone"]:
            assert "US/" not in str(tz), f"Timezone '{tz}' still contains 'US/'"

    def test_t1_9_unique_timezones_equals_csv_count(self, workflow_outputs):
        """T1.9: Number of unique timezone values equals number of output CSV files."""
        outputs, output_dir = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        unique_tz = cleansed["Timezone"].dropna().nunique()
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        assert unique_tz == len(csv_files)

    def test_t1_10_each_csv_has_correct_timezone_only(self, workflow_outputs):
        """T1.10: Each per-timezone CSV contains only records for that timezone."""
        _, output_dir = workflow_outputs
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        for csv_file in csv_files:
            filepath = os.path.join(output_dir, csv_file)
            tz_df = pd.read_csv(filepath, sep=".", dtype=str, encoding="latin-1")
            if "Timezone" in tz_df.columns:
                unique_tzs = tz_df["Timezone"].unique()
                assert len(unique_tzs) == 1, (
                    f"File {csv_file} has multiple timezones: {unique_tzs}"
                )

    def test_t1_11_union_of_csvs_equals_cleansed(self, workflow_outputs):
        """T1.11: Union of all per-timezone CSVs equals the full cleansed dataset."""
        outputs, output_dir = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        total_rows = 0
        for csv_file in csv_files:
            filepath = os.path.join(output_dir, csv_file)
            tz_df = pd.read_csv(filepath, sep=".", dtype=str, encoding="latin-1")
            total_rows += len(tz_df)
        assert total_rows == len(cleansed), (
            f"Union has {total_rows} rows but cleansed has {len(cleansed)}"
        )

    def test_t1_12_count_distinct_matches_per_timezone(self, workflow_outputs, synthetic_csv):
        """T1.12: CountDistinct aggregation matches per timezone group."""
        outputs, _ = workflow_outputs
        summary = outputs["accident_summary"]
        df = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        expected = (
            df.groupby("Timezone")
            .agg(No_of_accidents=("ID", "nunique"))
            .reset_index()
        )
        merged = summary.merge(expected, on="Timezone", suffixes=("_actual", "_expected"))
        for _, row in merged.iterrows():
            assert row["No_of_accidents_actual"] == row["No_of_accidents_expected"]


# ═══════════════════════════════════════════════════════════════════════════
# Data Integrity Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestDataIntegrity:
    """T1.13–T1.15: Data integrity validation."""

    def test_t1_13_no_duplicate_ids_within_timezone_csv(self, workflow_outputs):
        """T1.13: No duplicate IDs within any single timezone CSV."""
        _, output_dir = workflow_outputs
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        for csv_file in csv_files:
            filepath = os.path.join(output_dir, csv_file)
            tz_df = pd.read_csv(filepath, sep=".", dtype=str, encoding="latin-1")
            if "Timezone" in tz_df.columns:
                assert tz_df["Timezone"].nunique() <= 1, (
                    f"File {csv_file} has duplicate timezone values"
                )

    def test_t1_14_record_count_sums_correctly(self, workflow_outputs):
        """T1.14: Record count across all timezone files sums to total cleansed records."""
        outputs, output_dir = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        csv_files = [f for f in os.listdir(output_dir) if f.endswith("_time.csv")]
        total = sum(
            len(pd.read_csv(os.path.join(output_dir, f), sep=".", dtype=str, encoding="latin-1"))
            for f in csv_files
        )
        assert total == len(cleansed)

    def test_t1_15_expected_timezone_values_exist(self, workflow_outputs):
        """T1.15: Verify expected timezone values exist after cleanse."""
        outputs, _ = workflow_outputs
        cleansed = outputs["accident_cleansed"]
        tz_values = set(cleansed["Timezone"].dropna().unique())
        # After replacing US/ with space and uppercasing:
        # US/Eastern -> " EASTERN", US/Central -> " CENTRAL", etc.
        expected_substrings = ["EASTERN", "CENTRAL", "MOUNTAIN", "PACIFIC"]
        for substr in expected_substrings:
            found = any(substr in tz for tz in tz_values)
            assert found, f"Expected timezone containing '{substr}' not found in {tz_values}"
