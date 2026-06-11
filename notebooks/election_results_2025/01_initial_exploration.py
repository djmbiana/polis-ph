import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    mo.md("# Election Results 2025_EDA")
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    Connect to MongoDB `polis` database and target the `raw_election_results` collection.
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
    return collection, db, pd


@app.cell
def _(db):
    data_types = db["raw_election_results"].find_one()

    for key, value in data_types.items():
        print(f"{key}: {type(value).__name__}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Row Count
    - Total number of documents in the collection.
    - Has more records as compared to senate_25 and partylist_25 combined (give or take around 180,000+)
    """)
    return


@app.cell
def _(collection):
    total_docs = collection.count_documents({})
    print(f"Total documents: {total_docs:,}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distinct Positions and Row Counts

    - Each distinct `Position` value and how many records belong to it.
    - Has more information as it even scrapes local government data (senate_25 and partylist_25 only contain senate and partylist votes)
    """)
    return


@app.cell
def _(collection, pd):
    _pipeline = [
        {"$group": {"_id": "$Position", "row_count": {"$sum": 1}}},
        {"$sort": {"row_count": -1}},
    ]

    _result = list(collection.aggregate(_pipeline, allowDiskUse=True))
    df_positions = pd.DataFrame(_result).rename(columns={"_id": "Position"})

    df_positions
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Null Counts Per Column
    - Number of null or missing values for each field across all documents.
    `$eq: [field, null]` in an aggregation pipeline matches both explicit `null` and missing fields.
    Single `$group` stage — one query for all 18 fields.
    - No NULLs present within the dataset
    """)
    return


@app.cell
def _(collection, pd):
    _fields = [
        "Year", "Election_Type", "Region", "Province", "Municipality",
        "Barangay", "Precinct_Code", "Candidate_Name", "Position", "Party",
        "Votes", "Total_Votes", "Total_Voters", "Percentage",
        "Contest_ID", "Candidate_ID", "Scraped_At", "Source",
    ]

    _group_stage = {
        "_id": None,
        **{
            f: {"$sum": {"$cond": {"if": {"$eq": [f"${f}", None]}, "then": 1, "else": 0}}}
            for f in _fields
        },
    }

    _result = list(collection.aggregate([{"$group": _group_stage}], allowDiskUse=True))

    _row = {k: v for k, v in _result[0].items() if k != "_id"}

    df_nulls = pd.DataFrame.from_dict(_row, orient="index", columns=["null_count"])
    df_nulls = df_nulls.sort_values("null_count", ascending=False)

    df_nulls
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sample Rows Per Position Type
    One representative document per distinct position type — single `$group` using `$first`.
    """)
    return


@app.cell
def _(collection, pd):
    pd.set_option("display.max_columns", None)

    _pipeline = [
        {
            "$group": {
                "_id": "$Position",
                "Candidate_Name": {"$first": "$Candidate_Name"},
                "Region": {"$first": "$Region"},
                "Province": {"$first": "$Province"},
                "Municipality": {"$first": "$Municipality"},
                "Precinct_Code": {"$first": "$Precinct_Code"},
                "Party": {"$first": "$Party"},
                "Votes": {"$first": "$Votes"},
                "Total_Votes": {"$first": "$Total_Votes"},
                "Total_Voters": {"$first": "$Total_Voters"},
                "Percentage": {"$first": "$Percentage"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    _result = list(collection.aggregate(_pipeline, allowDiskUse=True))
    df_samples = pd.DataFrame(_result).rename(columns={"_id": "Position"})

    df_samples
    return


if __name__ == "__main__":
    app.run()
