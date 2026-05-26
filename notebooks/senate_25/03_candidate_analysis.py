import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# Candidate analysis")
    return (mo,)


@app.cell
def _():
    import pandas as pd
    df = pd.read_csv("../datasets/senate25-final_updated.csv")
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Election Winners
    - Senators who place within the top 12 have won their respective election
    - The dataset lines up with the official results released via COMELECS website, meaning that the data is accurate
    """)
    return


@app.cell
def _(df):
    sen = df.columns[12:]
    sen_votes = df[sen].sum().sort_values(ascending=False)
    sen_votes_region = df.groupby("region")[sen].sum()
    top12 = sen_votes.head(12).reset_index()
    top12.columns = ["candidate", "votes"]
    top12
    return sen_votes_region, top12


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Candidates per region
    - Candidates seem to score higher from their home region
        - To test this finding, I decided to isolate Dela Rosa, Bato who is from Region XI and compare his vote share between all the different regions
        - Region XI has about 66.1% more compared to the average vote share of other regions, this finding shows that our hypothesis is true.
        - I tested it further by isolating Go, Bong (Region XI) and Pangilinan, Kiko (NCR) and they followed the same results.
    """)
    return


@app.cell
def _(sen_votes_region, top12):
    top12_names = top12["candidate"].tolist()
    top12_regions = sen_votes_region[top12_names].sort_values(by=top12_names[0], ascending=False)
    top12_regions
    return (top12_regions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Vote share of each candidate per region
    """)
    return


@app.cell
def _(df, top12_regions):
    # change the candidate name for the candidate you want to examine
    candidate = "22. DELA ROSA, BATO (PDPLBN)"
    bato = top12_regions[candidate].to_frame()
    actual_vote_sum = df.groupby("region")["actualVoters"].sum()
    joined_df = bato.join(actual_vote_sum)
    joined_df["voteShare"] = (joined_df[candidate] / joined_df["actualVoters"] * 100).round(2)
    joined_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Future Scope
    - Region -> Province -> City -> Barangay
    """)
    return


if __name__ == "__main__":
    app.run()
