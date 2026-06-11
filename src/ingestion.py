from pathlib import Path

import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine

import config as con

file_path_senate = con.RAW_DATA_PATH / "senate25-final_updated.csv"
file_path_partylist = con.RAW_DATA_PATH / "partylist25-final_updated.csv"
postgres_url = con.POSTGRES_URL


def _strip_dots(df: pd.DataFrame) -> pd.DataFrame:
    # The MongoDB Spark Connector v10+ treats any dot in a field name as a nested-document
    # path separator. Candidate columns contain dots in both ballot numbers ("1. ABALOS")
    # and abbreviations ("JR.", "ATTY.", "R."). All dots must be stripped or the connector
    # returns null for those columns.
    df.columns = df.columns.str.replace(".", "", regex=False)
    return df


def load_senate_25(filepath: Path) -> pd.DataFrame:
    """
    loads the senate_25 csv into raw.senate_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = _strip_dots(pd.read_csv(filepath))
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_senate_25"].drop()
    db["raw_senate_25"].insert_many(df.to_dict("records"))
    client.close()
    eng = create_engine(postgres_url)
    df.to_sql("senate_25", eng, if_exists="replace", index=False, schema="raw")
    return df


def load_partylist_25(filepath: Path) -> pd.DataFrame:
    """
    loads the partylist_25 csv into raw.partylist_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = _strip_dots(pd.read_csv(filepath))
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_partylist_25"].drop()
    db["raw_partylist_25"].insert_many(df.to_dict("records"))
    client.close()
    eng = create_engine(postgres_url)
    df.to_sql("partylist_25", eng, if_exists="replace", index=False, schema="raw")
    return df


load_senate_25(file_path_senate)
load_partylist_25(file_path_partylist)
