from pathlib import Path

import pandas as pd
from pymongo import MongoClient

import config as con

file_path_senate = con.RAW_DATA_PATH / "senate25-final_updated.csv"
file_path_partylist = con.RAW_DATA_PATH / "partylist25-final_updated.csv"


def load_senate_25(filepath: Path) -> pd.DataFrame:
    """
    loads the senate_25 csv into raw.senate_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = pd.read_csv(filepath)
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_senate_25"].insert_many(df.to_dict("records"))
    client.close()
    return df


def load_partylist_25(filepath: Path) -> pd.DataFrame:
    """
    loads the partylist_25 csv into raw.partylist_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = pd.read_csv(filepath)
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    db["raw_partylist_25"].insert_many(df.to_dict("records"))
    client.close()
    return df


load_senate_25(file_path_senate)
load_partylist_25(file_path_partylist)
