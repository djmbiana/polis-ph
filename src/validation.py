import pandas as pd

import config as con

senate_df = pd.read_csv(con.RAW_DATA_PATH / "senate25-final_updated.csv")
partylist_df = pd.read_csv(con.RAW_DATA_PATH / "partylist25-final_updated.csv")


def check_negatives(df: pd.DataFrame) -> pd.DataFrame:
    """
    checks all numeric datatypes for negative numbers to ensure accuracy
    negative numbers would flag a problem with data collection as all voting machines must have no negative numbers
    """
    numeric_df = df.select_dtypes(include="int64")
    mask = (numeric_df < 0).any(axis=1)
    negative_rows: pd.DataFrame = df.loc[mask]

    if not negative_rows.empty:
        print("Some rows have negative values")

    else:
        print(f"Negative rows found: {len(negative_rows)}")

    return negative_rows


def invalid_turnout(df: pd.DataFrame) -> pd.DataFrame:
    """
    ensures that actual_voters does not exceed registered_voters
    if actual_voters is higher than registered_voters, it wouldn't make logical sense as only registered individuals can vote.
    """
    actual_voters = df["actualVoters"]
    registered_voters = df["registeredVoters"]
    mask = actual_voters > registered_voters
    turnout_validity: pd.DataFrame = df.loc[mask]

    if not turnout_validity.empty:
        print("Some rows have inaccurate turnout")

    else:
        print("All turnouts are accurate and make sense")

    return turnout_validity


def region_checking(df: pd.DataFrame) -> pd.DataFrame:
    """
    checks if any regions are missing from the datasets
    cross references all unique regions that were discovered during inital dataset exploration.
    """
    expected_regions = {
        "REGION I",
        "REGION II",
        "REGION III",
        "REGION IV-A",
        "REGION IV-B",
        "REGION V",
        "REGION VI",
        "REGION VII",
        "REGION VIII",
        "REGION IX",
        "REGION X",
        "REGION XI",
        "REGION XII",
        "REGION XIII",
        "NATIONAL CAPITAL REGION",
        "CORDILLERA ADMINISTRATIVE REGION",
        "BARMM",
        "NIR",
        "OAV",
        "LAV",
    }
    unique_regions = set(df["region"].unique())
    regions_in_data = expected_regions - unique_regions

    if len(regions_in_data) != 0:
        print("Data is missing the expected amount of regions")

    else:
        print("Data has the expected amount of regions")

    return pd.DataFrame(list(regions_in_data), columns=["missing_region"])  # type: ignore
