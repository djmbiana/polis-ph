import config as con
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

connect_url = con.DB_URL
file_path_senate = con.RAW_DATA_PATH / "senate25-final_updated.csv"
file_path_partylist = con.RAW_DATA_PATH / "partylist25-final_updated.csv"


def load_senate_25(filepath: Path) -> None:
    """
    loads the senate_25 csv into raw.senate_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = pd.read_csv(filepath)
    eng = create_engine(connect_url)

    df.to_sql("senate_25", eng, if_exists="replace", index=False, schema="raw")


def load_partylist_25(filepath: Path) -> None:
    """
    loads the partylist_25 csv into raw.partylist_25 table in postgresql.
    replaces the table if it already exists.
    """
    df = pd.read_csv(filepath)
    eng = create_engine(connect_url)

    df.to_sql("partylist_25", eng, if_exists="replace", index=False, schema="raw")
