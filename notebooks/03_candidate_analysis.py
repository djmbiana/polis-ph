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


@app.cell
def _(sen_votes_region, top12):
    top12_names = top12["candidate"].tolist()
    sen_votes_region[top12_names].sort_values(by=top12_names[0], ascending=False)
    return


if __name__ == "__main__":
    app.run()
