import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# Geographic Analysis")
    return


@app.cell
def _():
    import pandas as pd
    df = pd.read_csv('../datasets/senate25-final_updated.csv')
    pd.read_csv('../datasets/senate25-final_updated.csv')
    return (df,)


@app.cell
def _(df):
    df.groupby("region")[["registeredVoters", "actualVoters"]].sum().sort_values(by=["registeredVoters", "actualVoters"], ascending=False)
    return


if __name__ == "__main__":
    app.run()
