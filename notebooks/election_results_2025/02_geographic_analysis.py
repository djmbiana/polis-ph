import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    mo.md("# Election Results 2025_Geographic Analysis")
    return (mo,)


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distinct Geographic Unit Counts

    How many distinct regions, provinces, and municipalities appear in the data.
    Single `$group` with `$addToSet` for all three fields - one query, one pass.
    - Expected: 18 regions, 82 provinces, and 1,493 municipalities under standard COMELEC structure.
    - OAV and LAV are special voting groups that inflate region/province counts above the geographic baseline.
        - OAV is not included, the additional region and provinces being LAV. The municipalities being under our expected digit is because of COMELECs clustered precinct system.
    """)
    return


@app.cell
def _(collection, pd):
    _pipeline = [
        {
            "$group": {
                "_id": None,
                "regions_set": {"$addToSet": "$Region"},
                "provinces_set": {"$addToSet": "$Province"},
                "municipalities_set": {"$addToSet": "$Municipality"},
            }
        },

        {
            "$project": {
                "_id": 0,
                "regions": {"$size": "$regions_set"},
                "provinces": {"$size": "$provinces_set"},
                "municipalities": {"$size": "$municipalities_set"},
            }
        },
    ]

    _result = list(collection.aggregate(_pipeline, allowDiskUse=True))
    df_geo = pd.DataFrame(_result).T.rename(columns={0: "distinct_count"})

    df_geo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distinct Precinct Count vs Baseline
    The senate_25 EDA established **92,822** as the expected precinct baseline.
    A higher count here may indicate additional contest types (local races) or duplicate precinct codes across contest types.
    """)
    return


@app.cell
def _(collection):
    _result = list(collection.aggregate([
        {"$group": {"_id": "$Precinct_Code"}},
        {"$count": "distinct_precincts"},
    ], allowDiskUse=True))

    _precinct_count = _result[0]["distinct_precincts"] if _result else 0
    _baseline = 92_822
    _delta = _precinct_count - _baseline

    print(f"Distinct Precinct_Code values : {_precinct_count:,}")
    print(f"Senate_25 baseline            : {_baseline:,}")
    print(f"Delta                         : {_delta:+,}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Precincts Per Region
    Count of distinct `Precinct_Code` values broken down by region.
    Two-stage `$group`: deduplicate `(Region, Precinct_Code)` pairs first, then count per region.
    """)
    return


@app.cell
def _(collection, pd):
    _pipeline = [
        {"$group": {"_id": {"Region": "$Region", "Precinct_Code": "$Precinct_Code"}}},
        {"$group": {"_id": "$_id.Region", "precinct_count": {"$sum": 1}}},
        {"$sort": {"precinct_count": -1}},
    ]

    _result = list(collection.aggregate(_pipeline, allowDiskUse=True))
    df_precincts_per_region = pd.DataFrame(_result).rename(columns={"_id": "Region"})

    df_precincts_per_region
    return


if __name__ == "__main__":
    app.run()
