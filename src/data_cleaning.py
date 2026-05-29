import config as con
import pandas as pd

# import ingestion as ing re-write this later on

df = pd.read_csv(con.RAW_DATA_PATH / "senate25-final_updated.csv")


def separate_df(df: pd.DataFrame) -> tuple:
    """
    cleans senate_25.csv by separating OAV, LAV, and Domestic votes
    this is to cleanly separate the non domestic and special votes for later reporting.
    """
    oav = df[df["region"] == "OAV"].copy()
    oav = oav.reset_index(drop=True)

    lav = df[df["region"] == "LAV"].copy()
    lav = lav.reset_index(drop=True)

    domestic = df[~df["region"].isin(["LAV", "OAV"])].copy()
    domestic = domestic.reset_index(drop=True)

    return oav, lav, domestic


# def normalize_columns():
