from pathlib import Path

import pandas as pd
from pymongo import MongoClient

import config as con


file_path_results = con.RAW_DATA_PATH / "philippines_2025_elections_2025_results.csv"


def load_election_results(filepath: Path) -> None:
    client = MongoClient(con.MONGO_URL)
    db = client["polis"]
    collection = db["raw_election_results"]
    for chunk in pd.read_csv(filepath, chunksize=10000):
        collection.insert_many(chunk.to_dict("records"))
    client.close()


load_election_results(file_path_results)
