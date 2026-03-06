"""
Comprehensive test suite for Workflow 2: Accident User-Input Workflow.

Tests cover schema validation, business logic, and data integrity
using synthetic data (no real datasets required).
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_synthetic_data(n=300):
    """Create synthetic accident data with various Start_Time values."""
    rng = np.random.default_rng(99)
    records = []
    base_dates = [
        "2022-06-15 08:30:00",
        "2022-07-02 14:00:00",
        "2023-01-10 06:15:00",
        "2023-01-15 23:45:00",
        "2023-01-20 12:00:00",
        "2023-02-14 09:30:00",
        "2023-03-25 17:00:00",
        "2023-04-01 00:00:00",
        "2023-05-15 11:00:00",
        "2023-06-30 22:30:00",
    ]
    timezones = ["US/Eastern", "US/Central", "US/Mountain", "US/Pacific"]

    for i in range(n):
        dt_str = base_dates[i % len(base_dates)]
        tz = timezones[i % len(timezones)]
        records.append({
            "ID": f"A-{i:05d}",
            "Source": "Source2",
            "Severity": str(int(rng.integers(1, 5))),
            "Start_Time": dt_str,
            "End_Time": "2023-01-15 09:00:00",
            "Start_Lat": str(round(float(rng.uniform(25, 48)), 6)),
            "Start_Lng": str(round(float(rng.uniform(-125, -70)), 6)),
            "End_Lat": "",
            "End_Lng": "",
            "Distance(mi)": str(round(float(rng.uniform(0, 10)), 2)),
            "Description": "Test accident",
            "Street": "Main St",
            "City": "TestCity",
            "County": "TestCounty",
            "State": "CA",
            "Zipcode": "90210",
            "Country": "US",
            "Timezone": tz,
            "Airport_Code": "LAX",
            "Weather_Timestamp": dt_str,
            "Temperature(F)": str(round(float(rng.uniform(20, 100)), 1)),
            "Wind_Chill(F)": str(round(float(rng.uniform(10, 80)), 1)),
            "Humidity(%)": str(round(float(rng.uniform(0, 100)), 1)),
            "Pressure(in)": str(round(float(rng.uniform(28, 32)), 2)),
            "Visibility(mi)": str(round(float(rng.uniform(0, 10)), 1)),
            "Wind_Direction": "N",
            "Wind_Speed(mph)": str(round(float(rng.uniform(0, 50)), 1)),
            "Precipitation(in)": str(round(float(rng.uniform(0, 2)), 2)),
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
def workflow_outputs(synthetic_csv):
    """Run workflow 2 and return outputs dict."""
    from recipes.workflow2_accident_user_input import run

    return run(
        input_path=synthetic_csv,
        start_date="2023-01-01",
        end_date="2023-01-31",
    )


@pytest.fixture
def workflow_outputs_full(synthetic_csv):
    """Run workflow 2 with a wide date range covering all data."""
    from recipes.workflow2_accident_user_input import run

    return run(
        input_path=synthetic_csv,
        start_date="2020-01-01",
        end_date="2025-12-31",
    )


# =========================================================================
# Schema Validation Tests
# =========================================================================

class TestSchemaValidation:
    """T2.1-T2.7: Schema and type validation."""

    def test_t2_1_start_time_is_datetime(self, workflow_outputs):
        """T2.1: After DateTime parsing, Start_Time is datetime64 dtype."""
        filtered = workflow_outputs["accident_date_filtered"]
        assert pd.api.types.is_datetime64_any_dtype(filtered["Start_Time"])

    def test_t2_2_day_column_valid_weekday_names(self, workflow_outputs_full):
        """T2.2: Day column contains only valid weekday names."""
        df = workflow_outputs_full["accident_date_filtered"]
        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"}
        actual_days = set(df["Day"].dropna().unique())
        assert actual_days.issubset(valid_days), (
            f"Invalid day values: {actual_days - valid_days}"
        )

    def test_t2_3_day_type_valid_values(self, workflow_outputs_full):
        """T2.3: Day_type column contains only Weekday, Weekend, or Data issue."""
        df = workflow_outputs_full["accident_date_filtered"]
        valid_types = {"Weekday", "Weekend", "Data issue"}
        actual_types = set(df["Day_type"].dropna().unique())
        assert actual_types.issubset(valid_types), (
            f"Invalid Day_type values: {actual_types - valid_types}"
        )

    def test_t2_4_hour_column_valid_values(self, workflow_outputs_full):
        """T2.4: Hour column contains only values 00-23 (zero-padded strings)."""
        df = workflow_outputs_full["accident_date_filtered"]
        valid_hours = {f"{h:02d}" for h in range(24)}
        actual_hours = set(df["Hour"].dropna().unique())
        assert actual_hours.issubset(valid_hours), (
            f"Invalid Hour values: {actual_hours - valid_hours}"
        )

    def test_t2_5_eom_and_eopm_are_valid_dates(self, workflow_outputs_full):
        """T2.5: EOM and EOPM are valid dates."""
        df = workflow_outputs_full["accident_date_filtered"]
        assert pd.api.types.is_datetime64_any_dtype(df["EOM"])
        assert pd.api.types.is_datetime64_any_dtype(df["EOPM"])

    def test_t2_6_accident_by_day_type_columns(self, workflow_outputs):
        """T2.6: accident_by_day_type has exactly 2 columns."""
        day_type_df = workflow_outputs["accident_by_day_type"]
        assert list(day_type_df.columns) == ["Day_type", "Accidents"]

    def test_t2_7_accident_by_hour_columns(self, workflow_outputs):
        """T2.7: accident_by_hour has exactly 2 columns."""
        hourly_df = workflow_outputs["accident_by_hour"]
        assert list(hourly_df.columns) == ["Hour", "Accidents Count"]


# =========================================================================
# Business Logic Tests
# =========================================================================

class TestBusinessLogic:
    """T2.8-T2.16: Business logic validation."""

    def test_t2_8_weekday_weekend_mapping(self, workflow_outputs_full):
        """T2.8: Mon-Fri map to Weekday, Sat-Sun map to Weekend."""
        df = workflow_outputs_full["accident_date_filtered"]
        weekdays = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
        weekends = {"Saturday", "Sunday"}
        for _, row in df[["Day", "Day_type"]].drop_duplicates().iterrows():
            if row["Day"] in weekdays:
                assert row["Day_type"] == "Weekday"
            elif row["Day"] in weekends:
                assert row["Day_type"] == "Weekend"

    def test_t2_9_day_type_accidents_sum_equals_total(
        self, workflow_outputs_full, synthetic_csv
    ):
        """T2.9: Accidents sum in day_type output equals total distinct IDs."""
        day_type_df = workflow_outputs_full["accident_by_day_type"]
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        total_distinct = df_input["ID"].nunique()
        assert day_type_df["Accidents"].sum() == total_distinct

    def test_t2_10_hourly_accidents_sum_equals_total(
        self, workflow_outputs_full, synthetic_csv
    ):
        """T2.10: Accidents Count sum in hourly output equals total distinct IDs."""
        hourly_df = workflow_outputs_full["accident_by_hour"]
        df_input = pd.read_csv(synthetic_csv, dtype=str, encoding="latin-1")
        total_distinct = df_input["ID"].nunique()
        assert hourly_df["Accidents Count"].sum() == total_distinct

    def test_t2_11_hourly_sorted_descending(self, workflow_outputs):
        """T2.11: Hourly output is sorted descending by Accidents Count."""
        hourly_df = workflow_outputs["accident_by_hour"]
        values = hourly_df["Accidents Count"].tolist()
        assert values == sorted(values, reverse=True)

    def test_t2_12_eom_is_last_day_of_month(self, workflow_outputs_full):
        """T2.12: EOM is always the last day of the month of Start_Time."""
        df = workflow_outputs_full["accident_date_filtered"]
        sample = df[df["Start_Time"].notna()].head(50)
        for _, row in sample.iterrows():
            st = row["Start_Time"]
            eom = row["EOM"]
            next_day = eom + pd.Timedelta(days=1)
            assert next_day.month != eom.month or next_day.year != eom.year
            assert eom.month == st.month and eom.year == st.year

    def test_t2_13_eopm_is_day_before_first_of_month(self, workflow_outputs_full):
        """T2.13: EOPM is always the day before the first day of the month."""
        df = workflow_outputs_full["accident_date_filtered"]
        sample = df[df["Start_Time"].notna()].head(50)
        for _, row in sample.iterrows():
            st = row["Start_Time"]
            eopm = row["EOPM"]
            first_of_month = st.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            expected_eopm = first_of_month - pd.Timedelta(days=1)
            assert eopm.date() == expected_eopm.date()

    def test_t2_14_date_range_filter_correct(self, workflow_outputs):
        """T2.14: Date range filter returns only records in the range."""
        filtered = workflow_outputs["accident_date_filtered"]
        start = pd.Timestamp("2023-01-01")
        end = pd.Timestamp("2023-01-31")
        for _, row in filtered.iterrows():
            assert row["Start_Time"] >= start
            assert row["Start_Time"] < end

    def test_t2_15_impossible_date_range_returns_empty(self, synthetic_csv):
        """T2.15: Date range filter with end < start returns 0 records."""
        from recipes.workflow2_accident_user_input import run

        outputs = run(
            input_path=synthetic_csv,
            start_date="2023-12-31",
            end_date="2023-01-01",
        )
        assert len(outputs["accident_date_filtered"]) == 0

    def test_t2_16_no_data_issue_in_day_type(self, workflow_outputs_full):
        """T2.16: No Data issue values exist in Day_type."""
        df = workflow_outputs_full["accident_date_filtered"]
        data_issues = df[df["Day_type"] == "Data issue"]
        assert len(data_issues) == 0
