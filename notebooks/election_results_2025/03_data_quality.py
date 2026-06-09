import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    mo.md("# Election Results 2025_Data Quality")
    return (mo,)


@app.cell
def _():
    import sys
    sys.path.insert(0, "../../src")
    from config import MONGO_URL
    from pymongo import MongoClient

    client = MongoClient(MONGO_URL)
    db = client["polis"]
    collection = db["raw_election_results"]
    return (collection,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Negative Votes
    Any `Votes` value below zero indicates a data entry or scraping error.
    """)
    return


@app.cell
def _(collection):
    _result = list(collection.aggregate([
        {"$match": {"Votes": {"$lt": 0}}},
        {"$count": "n"},
    ]))
    _count = _result[0]["n"] if _result else 0
    print(f"Documents with negative Votes: {_count:,}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Impossible Turnout
    Records where `Votes > Total_Voters` are physically impossible — a candidate cannot receive
    more votes than there are registered voters in a precinct.
    """)
    return


@app.cell
def _(collection):
    import pandas as _pd

    _result = list(collection.aggregate([
        {"$match": {"$expr": {"$gt": ["$Votes", "$Total_Voters"]}}},
        {"$count": "n"},
    ], allowDiskUse=True))
    _count = _result[0]["n"] if _result else 0
    print(f"Documents with Votes > Total_Voters: {_count:,}")

    _rows = list(collection.aggregate([
        {"$match": {"$expr": {"$gt": ["$Votes", "$Total_Voters"]}}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "Precinct_Code": 1, "Candidate_Name": 1, "Position": 1,
            "Votes": 1, "Total_Voters": 1,
        }},
    ])) if _count > 0 else []
    _pd.DataFrame(_rows)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Total_Votes Consistency
    Within a `(Precinct_Code, Contest_ID)` group, `Total_Votes` should be the same for all
    candidates — it represents the total ballots cast in that contest at that precinct.
    Groups where `min(Total_Votes) != max(Total_Votes)` are inconsistent.
    """)
    return


@app.cell
def _(collection):
    import pandas as _pd

    _pipeline = [
        {
            "$group": {
                "_id": {
                    "Precinct_Code": "$Precinct_Code",
                    "Contest_ID": "$Contest_ID",
                },
                "min_tv": {"$min": "$Total_Votes"},
                "max_tv": {"$max": "$Total_Votes"},
            }
        },
        {"$match": {"$expr": {"$ne": ["$min_tv", "$max_tv"]}}},
        {"$count": "n"},
    ]
    _result = list(collection.aggregate(_pipeline, allowDiskUse=True))
    _count = _result[0]["n"] if _result else 0
    print(f"(Precinct_Code, Contest_ID) groups with inconsistent Total_Votes: {_count:,}")

    _rows = list(collection.aggregate([
        {
            "$group": {
                "_id": {
                    "Precinct_Code": "$Precinct_Code",
                    "Contest_ID": "$Contest_ID",
                },
                "min_tv": {"$min": "$Total_Votes"},
                "max_tv": {"$max": "$Total_Votes"},
                "doc_count": {"$sum": 1},
            }
        },
        {"$match": {"$expr": {"$ne": ["$min_tv", "$max_tv"]}}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "Precinct_Code": "$_id.Precinct_Code",
            "Contest_ID": "$_id.Contest_ID",
            "min_Total_Votes": "$min_tv",
            "max_Total_Votes": "$max_tv",
            "doc_count": 1,
        }},
    ], allowDiskUse=True)) if _count > 0 else []
    _pd.DataFrame(_rows)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Duplicate Detection
    A `(Precinct_Code, Candidate_ID)` pair appearing more than once suggests the same record
    was scraped multiple times. `Scraped_At` timestamps are collected per group to confirm
    whether duplicates originate from separate scrape runs.

    Note: if `Candidate_ID` is `0` across the dataset, group by `(Precinct_Code, Candidate_Name)` instead.
    """)
    return


@app.cell
def _(collection):
    import pandas as _pd

    _result = list(collection.aggregate([
        {
            "$group": {
                "_id": {
                    "Precinct_Code": "$Precinct_Code",
                    "Candidate_ID": "$Candidate_ID",
                },
                "count": {"$sum": 1},
                "scraped_at_values": {"$addToSet": "$Scraped_At"},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$count": "n"},
    ], allowDiskUse=True))
    _dup_count = _result[0]["n"] if _result else 0
    print(f"(Precinct_Code, Candidate_ID) groups with more than one record: {_dup_count:,}")

    _rows = list(collection.aggregate([
        {
            "$group": {
                "_id": {
                    "Precinct_Code": "$Precinct_Code",
                    "Candidate_ID": "$Candidate_ID",
                },
                "count": {"$sum": 1},
                "scraped_at_values": {"$addToSet": "$Scraped_At"},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "Precinct_Code": "$_id.Precinct_Code",
            "Candidate_ID": "$_id.Candidate_ID",
            "count": 1,
            "scraped_at_values": 1,
        }},
    ], allowDiskUse=True)) if _dup_count > 0 else []
    _pd.DataFrame(_rows)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Null Candidate Name Rows
    Records with no `Candidate_Name` are unusable for any candidate-level analysis.
    """)
    return


@app.cell
def _(collection):
    _result = list(collection.aggregate([
        {"$match": {"$or": [
            {"Candidate_Name": None},
            {"Candidate_Name": {"$exists": False}},
        ]}},
        {"$count": "n"},
    ]))
    _count = _result[0]["n"] if _result else 0
    print(f"Documents with null/missing Candidate_Name: {_count:,}")
    return


if __name__ == "__main__":
    app.run()
