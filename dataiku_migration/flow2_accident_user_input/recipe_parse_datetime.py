# Dataiku Python Recipe: Parse DateTime and Derive Time Fields
#
# Mirrors: Accident-user-input.yxmd
#   - DateTime tool (Tool 5, line 138): Convert Start_Time string → datetime
#   - Select tool (Tool 6, line 158): Rename DateTime_Out → Start_Time
#   - Formula tool (Tool 3, lines 86-108): Derive Day, Day_type, Hour, EOM, EOPM
#
# Input dataset:  US_Accidents_March23
# Output dataset: accidents_enriched

import pandas as pd

try:
    import dataiku

    INPUT_DATASET = "US_Accidents_March23"
    OUTPUT_DATASET = "accidents_enriched"

    input_ds = dataiku.Dataset(INPUT_DATASET)
    df = input_ds.get_dataframe()
except ImportError:
    dataiku = None
    df = None


def parse_datetime_and_derive(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse Start_Time string to datetime and derive temporal fields.

    Mirrors Alteryx Formula tool (Tool 3):
        - Day       = DateTimeFormat([Start_Time], "%A")      → full day name
        - Day_type  = if Day in (Mon-Fri) then "Weekday"
                      elseif Day in (Sat, Sun) then "Weekend"
                      else "Data issue"
        - Hour      = DateTimeFormat([Start_Time], "%H")      → zero-padded hour
        - EOM       = DateTimeTrim([Start_Time], "lastofmonth")
        - EOPM      = DateTimeAdd(DateTimeTrim([Start_Time], "firstofmonth"), -1, "days")

    Args:
        df: Raw accident DataFrame with 'Start_Time' as string column.

    Returns:
        Enriched DataFrame with new columns: Day, Day_type, Hour, EOM, EOPM.
    """
    df = df.copy()

    # Parse Start_Time string to datetime (format: yyyy-MM-dd hh:mm:ss)
    df["Start_Time"] = pd.to_datetime(
        df["Start_Time"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )

    # Derive Day — full weekday name (e.g., "Monday")
    df["Day"] = df["Start_Time"].dt.day_name()

    # Derive Day_type — Weekday, Weekend, or Data issue
    weekdays = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
    weekends = {"Saturday", "Sunday"}

    def classify_day(day_name):
        if pd.isna(day_name):
            return "Data issue"
        if day_name in weekdays:
            return "Weekday"
        if day_name in weekends:
            return "Weekend"
        return "Data issue"

    df["Day_type"] = df["Day"].apply(classify_day)

    # Derive Hour — zero-padded 24h hour string (e.g., "08", "23")
    df["Hour"] = df["Start_Time"].dt.strftime("%H")

    # Derive EOM — End of Month (last day of the month)
    # Mirrors: DateTimeTrim([Start_Time], "lastofmonth")
    df["EOM"] = (
        df["Start_Time"]
        .dt.to_period("M")
        .dt.to_timestamp("M")
        .dt.normalize()
    )
    # to_timestamp("M") gives the last day of the month at midnight

    # Derive EOPM — End of Previous Month
    # Mirrors: DateTimeAdd(DateTimeTrim([Start_Time], "firstofmonth"), -1, "days")
    first_of_month = df["Start_Time"].dt.to_period("M").dt.to_timestamp()
    df["EOPM"] = first_of_month - pd.Timedelta(days=1)

    return df


if dataiku is not None and df is not None:
    df = parse_datetime_and_derive(df)
    output_ds = dataiku.Dataset(OUTPUT_DATASET)
    output_ds.write_with_schema(df)
