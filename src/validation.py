import config as con
import pandas as pd

senate_df = pd.read_csv(con.RAW_DATA_PATH / "senate25-final_updated.csv")
partylist_df = pd.read_csv(con.RAW_DATA_PATH / "partylist25-final_updated.csv")


def check_negatives(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include="int64")
    mask = (numeric_df < 0).any(axis=1)
    negative_rows: pd.DataFrame = df.loc[mask]

    if not negative_rows.empty:
        print("Some rows have negative values")
        print(negative_rows)

    else:
        print(f"Negative rows found: {len(negative_rows)}")

    return negative_rows
