"""
Shared pytest fixtures for Dataiku migration test suite.

Provides synthetic DataFrames that mirror the structure of each source dataset
used by the five Alteryx workflows. Tests do NOT require the full production
CSV files — these fixtures create small representative datasets that exercise
every code path in the recipe functions.
"""

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Flow 1 & 2: US Accidents dataset fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def accidents_raw_df():
    """
    Minimal US_Accidents_March23 DataFrame (46-column structure, subset of columns).
    Includes rows with null Timezone, US/ prefixed values, and various timezones.
    """
    data = {
        "ID": [
            "A-1001", "A-1002", "A-1003", "A-1004", "A-1005",
            "A-1006", "A-1007", "A-1008", "A-1009", "A-1010",
            "A-1011", "A-1012",
        ],
        "Source": ["S1"] * 12,
        "Severity": ["2", "3", "2", "4", "2", "3", "2", "3", "2", "4", "2", "3"],
        "Start_Time": [
            "2021-03-15 08:30:00",
            "2021-06-20 14:15:00",
            "2021-09-01 06:45:00",
            "2021-12-25 23:00:00",
            "2022-01-10 07:00:00",
            "2021-05-08 10:30:00",  # Saturday
            "2021-07-04 16:00:00",  # Sunday
            "2021-11-11 09:00:00",
            "2021-03-15 08:30:00",  # duplicate time as A-1001
            "2021-06-20 14:15:00",  # duplicate time as A-1002
            "2021-08-15 12:00:00",
            "2021-10-31 18:45:00",  # Sunday
        ],
        "End_Time": ["2021-03-15 09:00:00"] * 12,
        "Start_Lat": ["39.0"] * 12,
        "Start_Lng": ["-84.0"] * 12,
        "End_Lat": [""] * 12,
        "End_Lng": [""] * 12,
        "Distance(mi)": ["0.5"] * 12,
        "Description": ["Test accident"] * 12,
        "Street": ["Main St"] * 12,
        "City": ["TestCity"] * 12,
        "County": ["TestCounty"] * 12,
        "State": ["OH"] * 12,
        "Zipcode": ["45202"] * 12,
        "Country": ["US"] * 12,
        "Timezone": [
            "US/Eastern",
            "US/Central",
            "US/Mountain",
            "US/Pacific",
            "US/Eastern",
            "US/Central",
            None,          # null timezone — should be filtered
            "US/Eastern",
            "US/Pacific",
            "US/Mountain",
            "US/Eastern",
            "US/Central",
        ],
        "Airport_Code": ["KCVG"] * 12,
        "Weather_Timestamp": ["2021-03-15 08:30:00"] * 12,
        "Temperature(F)": ["45.0"] * 12,
        "Wind_Chill(F)": ["40.0"] * 12,
        "Humidity(%)": ["60.0"] * 12,
        "Pressure(in)": ["29.9"] * 12,
        "Visibility(mi)": ["10.0"] * 12,
        "Wind_Direction": ["NW"] * 12,
        "Wind_Speed(mph)": ["5.0"] * 12,
        "Precipitation(in)": ["0.0"] * 12,
        "Weather_Condition": ["Clear"] * 12,
        "Amenity": ["False"] * 12,
        "Bump": ["False"] * 12,
        "Crossing": ["False"] * 12,
        "Give_Way": ["False"] * 12,
        "Junction": ["False"] * 12,
        "No_Exit": ["False"] * 12,
        "Railway": ["False"] * 12,
        "Roundabout": ["False"] * 12,
        "Station": ["False"] * 12,
        "Stop": ["False"] * 12,
        "Traffic_Calming": ["False"] * 12,
        "Traffic_Signal": ["False"] * 12,
        "Turning_Loop": ["False"] * 12,
        "Sunrise_Sunset": ["Day"] * 12,
        "Civil_Twilight": ["Day"] * 12,
        "Nautical_Twilight": ["Day"] * 12,
        "Astronomical_Twilight": ["Day"] * 12,
    }
    return pd.DataFrame(data)


@pytest.fixture
def accidents_cleansed_df():
    """
    Cleansed accident DataFrame (after prepare_cleanse).
    Timezone values are uppercased, US/ prefix removed, no nulls.
    """
    data = {
        "ID": [
            "A-1001", "A-1002", "A-1003", "A-1004", "A-1005",
            "A-1006", "A-1008", "A-1009", "A-1010", "A-1011", "A-1012",
        ],
        "Timezone": [
            "EASTERN", "CENTRAL", "MOUNTAIN", "PACIFIC", "EASTERN",
            "CENTRAL", "EASTERN", "PACIFIC", "MOUNTAIN", "EASTERN", "CENTRAL",
        ],
        "Start_Time": [
            "2021-03-15 08:30:00",
            "2021-06-20 14:15:00",
            "2021-09-01 06:45:00",
            "2021-12-25 23:00:00",
            "2022-01-10 07:00:00",
            "2021-05-08 10:30:00",
            "2021-11-11 09:00:00",
            "2021-03-15 08:30:00",
            "2021-06-20 14:15:00",
            "2021-08-15 12:00:00",
            "2021-10-31 18:45:00",
        ],
    }
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Flow 3: TED Talk dataset fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def ted_raw_df():
    """
    Minimal ted_main DataFrame (12 columns) with a mix of years and speakers.
    """
    data = {
        "comments": [100, 200, 300, 150, 250, 180, 220, 350, 400, 120],
        "duration": [1000, 1100, 1200, 900, 1300, 800, 1000, 1100, 1200, 950],
        "event": [
            "TED2006", "TED2006", "TED2007", "TED2007", "TED2007",
            "TED2008", "TED2008", "TED2009", "TED2009", "TED2010",
        ],
        "film_date": [
            "1140825600",   # 2006-02-25
            "1140912000",   # 2006-02-26
            "1173312000",   # 2007-03-08
            "1173398400",   # 2007-03-09
            "1173484800",   # 2007-03-10
            "1204848000",   # 2008-03-07
            "1204934400",   # 2008-03-08
            "1236384000",   # 2009-03-07
            "1236470400",   # 2009-03-08
            "1267920000",   # 2010-03-07
        ],
        "languages": [60, 43, 26, 35, 48, 36, 31, 32, 30, 28],
        "main_speaker": [
            "Ken Robinson", "Al Gore", "Ken Robinson", "Bill Gates",
            "Hans Rosling", "Ken Robinson", "Jill Bolte Taylor",
            "Ken Robinson", "Hans Rosling", "social entrepreneur Jane",
        ],
        "name": [f"Talk {i}" for i in range(1, 11)],
        "num_speaker": [1] * 10,
        "published_date": [
            "1151367060", "1151367060", "1175559060", "1175559060",
            "1175559060", "1207612860", "1207612860", "1240185660",
            "1240185660", "1272038460",
        ],
        "speaker_occupation": [
            "Author/educator",
            "Climate advocate",
            "Author/educator",
            "Technologist",
            "Global health expert",
            "Author/educator",
            "Neuroanatomist",
            "Author/educator",
            "Global health expert",
            "Social entrepreneur",
        ],
        "title": [f"Title {i}" for i in range(1, 11)],
        "views": [
            47227110, 3200520, 25000000, 30000000, 12005869,
            15000000, 20685401, 8000000, 5000000, 2000000,
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def ted_enriched_df(ted_raw_df):
    """Pre-enriched TED DataFrame with film_date as datetime and derived columns."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flow3_ted_talk"))
    from recipe_epoch_to_datetime import epoch_to_datetime
    return epoch_to_datetime(ted_raw_df)


# ---------------------------------------------------------------------------
# Flow 4: Superstore dataset fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def superstore_raw_df():
    """
    Minimal Superstore orders DataFrame matching the XLS schema.
    Includes orders from 2015, 2016, and 2017 to test date filtering.
    """
    data = {
        "Row ID": list(range(1, 11)),
        "Order ID": [f"CA-2016-{i:06d}" for i in range(1, 11)],
        "Order Date": pd.to_datetime([
            "2015-11-08", "2016-01-15", "2016-03-20", "2016-06-12",
            "2016-08-05", "2016-09-17", "2016-11-22", "2016-12-30",
            "2017-01-01", "2017-02-15",
        ]),
        "Ship Date": pd.to_datetime(["2016-01-20"] * 10),
        "Ship Mode": ["Standard Class"] * 10,
        "Customer ID": [f"CG-{i:05d}" for i in range(1, 11)],
        "Customer Name": [f"Customer {i}" for i in range(1, 11)],
        "Segment": ["Consumer", "Corporate", "Consumer", "Home Office",
                     "Consumer", "Corporate", "Consumer", "Home Office",
                     "Consumer", "Corporate"],
        "Country": ["United States"] * 10,
        "City": ["New York"] * 10,
        "State": ["New York"] * 10,
        "Postal Code": [10001.0] * 10,
        "Region": ["East"] * 10,
        "Product ID": [f"FUR-{i:04d}" for i in range(1, 11)],
        "Category": [
            "Furniture", "Technology", "Office Supplies", "Furniture",
            "Technology", "Office Supplies", "Furniture", "Technology",
            "Office Supplies", "Furniture",
        ],
        "Sub-Category": [
            "Chairs", "Phones", "Paper", "Tables", "Accessories",
            "Binders", "Chairs", "Phones", "Paper", "Tables",
        ],
        "Product Name": [f"Product {i}" for i in range(1, 11)],
        "Sales": [500.0, 1200.0, 50.0, 800.0, 300.0, 150.0, 900.0, 1500.0, 25.0, 400.0],
        "Quantity": [2.0, 3.0, 10.0, 1.0, 5.0, 7.0, 2.0, 1.0, 20.0, 3.0],
        "Discount": [0.0, 0.1, 0.0, 0.2, 0.0, 0.1, 0.0, 0.2, 0.0, 0.1],
        "Profit": [100.0, 200.0, 10.0, -50.0, 80.0, 30.0, 150.0, 300.0, 5.0, -20.0],
    }
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Flow 5: Purchase Registration dataset fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def purchase_raw_df():
    """
    Minimal purchase registration DataFrame (subset of 98 columns).
    Includes whitespace, mixed case, and null values to test cleansing.
    """
    data = {
        "miro_no": ["  abc123 ", "DEF456", None, "ghi789  ", "  JKL012  "],
        "posting_dt": ["2023-01-15", "  2023-02-20 ", None, "2023-03-25", "2023-04-30"],
        "miro_acc": ["1000", " 2000", "3000 ", None, "5000"],
        "doc_dt": ["2023-01-15", "2023-02-20", "2023-03-25", "2023-04-30", None],
        "referance": [" ref1 ", "REF2", None, "  ref3", "ref4  "],
        "vendor": ["V001", " v002 ", "V003", None, "v005"],
        "name": [" Company A ", "company b", "COMPANY C", None, "  company e "],
        "material_code": ["M100", "m200 ", " M300", None, "m500"],
        "description": ["Item A", " item b ", "ITEM C", "item d", None],
        "plant": ["P1", "P2", None, "p4", " P5 "],
    }
    return pd.DataFrame(data)
