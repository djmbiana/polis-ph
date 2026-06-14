from pathlib import Path

import pandas as pd
from pymongo import MongoClient

import config as con

file_path_senate = con.RAW_DATA_PATH / "senate25-final_updated.csv"
file_path_partylist = con.RAW_DATA_PATH / "partylist25-final_updated.csv"


def _strip_dots(df: pd.DataFrame) -> pd.DataFrame:
    # The MongoDB Spark Connector v10+ treats any dot in a field name as a nested-document
    # path separator. Candidate columns contain dots in both ballot numbers ("1. ABALOS")
    # and abbreviations ("JR.", "ATTY.", "R."). All dots must be stripped or the connector
    # returns null for those columns.
    df.columns = df.columns.str.replace(".", "", regex=False)
    return df


def load_senate_25(filepath: Path) -> pd.DataFrame:
    df = _strip_dots(pd.read_csv(filepath))
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_senate_25"].drop()
    db["raw_senate_25"].insert_many(df.to_dict("records"))
    client.close()
    return df


def load_partylist_25(filepath: Path) -> pd.DataFrame:
    df = _strip_dots(pd.read_csv(filepath))
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_partylist_25"].drop()
    db["raw_partylist_25"].insert_many(df.to_dict("records"))
    client.close()
    return df


load_senate_25(file_path_senate)
load_partylist_25(file_path_partylist)
