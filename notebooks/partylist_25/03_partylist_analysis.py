import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# Partylist analysis")
    return (mo,)


@app.cell
def _():
    import pandas as pd
    df = pd.read_csv("../../datasets/partylist25-final_updated.csv")
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Election Winners (Partylist)
    - Partylists who have a 2% of total partylist vote casts nationwide are guaranteed a seat
        - If a partylist fails to get the 2%, they may still win a seat through the BANAT formula (if there are seats that need to be filled due to the 20% House of Representative quota)
    - This dataset matches up with the actual results presented by COMELEC
    """)
    return


@app.cell
def _(df):
    # Sorting metadata columns from partylist columns
    md_cols = ["region", "province", "municipality", "barangay", "machineId", "registeredVoters", "actualVoters", "validBallot", "overVotes", "underVotes", "validVotes", "obtainedVotes"]

    pl_cols = [col for col in df.columns if col not in md_cols]

    # Adding all values together
    sum = df[pl_cols].sum().reset_index()
    sum.columns = ["partylist", "total_votes"]

    # Rank by votes
    sum = sum.sort_values("total_votes", ascending=False).reset_index(drop=True)
    sum["rank"] = sum.index + 1

    # Calculate vote percentage
    sum["vote_percentage"] = (sum["total_votes"] / sum["total_votes"].sum() * 100).round(2)

    # Assigned seats 
    def assigned_seats(rank):
        if rank <= 3:
            return 3
        elif rank <= 6:
            return 2
        elif rank <=54:
            return 1
        else:
            return 0

    sum["seats"] = sum["rank"].apply(assigned_seats)
    sum["qualified"] = sum["seats"] > 0 

    sum
    return


if __name__ == "__main__":
    app.run()
