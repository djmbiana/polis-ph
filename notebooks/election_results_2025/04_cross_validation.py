import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    mo.md("# Cross Validation: Parquet vs MongoDB")
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    Connect to MongoDB and load shared constants.
    """)
    return


@app.cell
def _():
    import sys
    sys.path.insert(0, "../../src")
    from config import MONGO_URL
    from pymongo import MongoClient
    import pandas as pd

    client = MongoClient(MONGO_URL)
    db = client["polis"]
    collection = db["raw_election_results"]
    return collection, pd


@app.cell
def _():
    METADATA_COLS = {
        "REGION", "PROVINCE", "MUNICIPALITY", "BARANGAY", "MACHINE_ID",
        "REGISTERED_VOTERS", "ACTUAL_VOTERS", "VALID_BALLOT", "OVER_VOTES",
        "UNDER_VOTES", "VALID_VOTES", "OBTAINED_VOTES", "_ID",
    }
    return (METADATA_COLS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Senate

    **Wide format** — `spark/output/senate_25/` Parquet, one column per candidate.
    Each row is a precinct/barangay; candidate columns hold that precinct's vote count.
    Summed across all rows to get the national total per candidate.

    **Long format** — `raw_election_results` in MongoDB, one document per candidate per precinct.
    Aggregated with `$match Position = "Senator"` → `$group by Candidate_Name` → `$sum Votes`.

    Merge key: Parquet column names have **all dots stripped** (`ingestion.py`) because
    the MongoDB Spark Connector treats any dot as a nested-document path separator —
    this affects ballot-number dots (`"1."`) and abbreviation dots (`"JR."`, `"ATTY."`,
    `"R."`). `raw_election_results` `Candidate_Name` retains the original dots.
    The merge normalizes both sides: strip all dots and uppercase before joining.
    """)
    return


@app.cell
def _(METADATA_COLS, pd):
    _df = pd.read_parquet("../../spark/output/senate_25/")
    _candidate_cols = [c for c in _df.columns if c not in METADATA_COLS]
    # min_count=1 → returns NaN (not 0) when the entire column is null,
    # making missing parquet data visible rather than silently showing 0.
    senate_wide = (
        _df[_candidate_cols]
        .sum(min_count=1)
        .rename_axis("Candidate_Name")
        .rename("wide_total")
        .reset_index()
    )
    senate_wide
    return (senate_wide,)


@app.cell
def _(collection, pd):
    _pipeline = [
        {"$match": {"Position": "Senator"}},
        {
            "$group": {
                "_id": "$Candidate_Name",
                "long_total": {"$sum": "$Votes"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    _rows = list(collection.aggregate(_pipeline, allowDiskUse=True))
    senate_long = pd.DataFrame(_rows).rename(columns={"_id": "Candidate_Name"})
    senate_long
    return (senate_long,)


@app.cell
def _(senate_long, senate_wide):
    import re as _re

    def _normalize(s):
        # Strip ALL dots then uppercase. Parquet columns have all dots removed by
        # ingestion.py. raw_election_results Candidate_Name retains original dots
        # (ballot number "1.", abbreviations "JR.", "ATTY.", "R.").
        return s.str.replace(".", "", regex=False).str.upper()

    df_senate = (
        senate_wide.assign(_key=_normalize(senate_wide["Candidate_Name"]))
        .merge(
            senate_long.assign(_key=_normalize(senate_long["Candidate_Name"])),
            on="_key",
            how="outer",
        )
        .rename(columns={"Candidate_Name_x": "parquet_name", "Candidate_Name_y": "mongo_name"})
        .drop(columns="_key")
        .assign(difference=lambda x: x["wide_total"] - x["long_total"])
        .assign(mismatch=lambda x: x["difference"].notna() & (x["difference"] != 0))
        [["parquet_name", "mongo_name", "wide_total", "long_total", "difference", "mismatch"]]
        .sort_values("parquet_name")
        .reset_index(drop=True)
    )
    df_senate
    return (df_senate,)


@app.cell
def _(df_senate):
    _flagged = df_senate[df_senate["mismatch"]]
    print(f"Senate mismatches: {len(_flagged)} / {len(df_senate)} candidates")
    _flagged
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Party List

    **Wide format** — `spark/output/partylist_25/` Parquet, one column per party.
    Each row is a precinct/barangay; party columns hold that precinct's vote count.
    Summed across all rows to get the national total per party.

    **Long format** — `raw_election_results` in MongoDB, one document per party per precinct.
    Aggregated with `$match Position = "Party List"` → `$group by Candidate_Name` → `$sum Votes`.

    Merge key: same dot-strip + uppercase normalization as Senate.
    """)
    return


@app.cell
def _(METADATA_COLS, pd):
    _df = pd.read_parquet("../../spark/output/partylist_25/")
    _candidate_cols = [c for c in _df.columns if c not in METADATA_COLS]
    partylist_wide = (
        _df[_candidate_cols]
        .sum(min_count=1)
        .rename_axis("Candidate_Name")
        .rename("wide_total")
        .reset_index()
    )
    partylist_wide
    return (partylist_wide,)


@app.cell
def _(collection, pd):
    _pipeline = [
        {"$match": {"Position": "Party List"}},
        {
            "$group": {
                "_id": "$Candidate_Name",
                "long_total": {"$sum": "$Votes"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    _rows = list(collection.aggregate(_pipeline, allowDiskUse=True))
    partylist_long = pd.DataFrame(_rows).rename(columns={"_id": "Candidate_Name"})
    partylist_long
    return (partylist_long,)


@app.cell
def _(partylist_long, partylist_wide):
    import re as _re

    def _normalize(s):
        return s.str.replace(".", "", regex=False).str.upper()

    df_partylist = (
        partylist_wide.assign(_key=_normalize(partylist_wide["Candidate_Name"]))
        .merge(
            partylist_long.assign(_key=_normalize(partylist_long["Candidate_Name"])),
            on="_key",
            how="outer",
        )
        .rename(columns={"Candidate_Name_x": "parquet_name", "Candidate_Name_y": "mongo_name"})
        .drop(columns="_key")
        .assign(difference=lambda x: x["wide_total"] - x["long_total"])
        .assign(mismatch=lambda x: x["difference"].notna() & (x["difference"] != 0))
        [["parquet_name", "mongo_name", "wide_total", "long_total", "difference", "mismatch"]]
        .sort_values("parquet_name")
        .reset_index(drop=True)
    )
    df_partylist
    return (df_partylist,)


@app.cell
def _(df_partylist):
    _flagged = df_partylist[df_partylist["mismatch"]]
    print(f"Party list mismatches: {len(_flagged)} / {len(df_partylist)} parties")
    _flagged
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Findings
    - Across the board, the wide data set has more votes than the long format. This is present throughout all rows.
       - This could be because it was scraped in the middle of the elections as compared to after. `scraped_by` in the long data set gives us this.
    - The difference between the vote counts varies, some within the 100k mark and some within the thousands.
    - This means that the wide datasets should be used for analysis, while the long data set can be used to map out the dashboard. This is because the long dataset still offers good insights on where the voting happened and it can open up polis for local analysis as a future scope.
        - The cleaning of the long dataset will focus on its geography as compared to its results.
    """)
    return


if __name__ == "__main__":
    app.run()
