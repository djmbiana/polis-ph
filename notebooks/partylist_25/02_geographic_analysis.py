import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# Partylist Votes Geographic Analysis")
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    df = pd.read_csv('../../datasets/partylist25-final_updated.csv')
    return df, plt, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Registered voters vs Actual voters per region
    - Registered voters are individuals who have registered under comelec for voting
    - Actual voters are those who actually voted, indicating actual turnouts during the election
    - Results are similar to the senate_25 dataset
        - Region IV-A has the most registered voters
        - Region VII has the highest turnout percentage
        - OAV has a turnout percentage of 18.37%. This could indicate that a lot of overseas Filipinos are able to register but are unable to vote.
    - LAV has a turnout percentage of 52.07%. This is because these are individuals who do not vote at their registered precinct
    """)
    return


@app.cell
def _(df):
    to = df.groupby("region")[["registeredVoters", "actualVoters"]].sum()
    to["turnoutPercentage"] = (to["actualVoters"] / to["registeredVoters"] * 100).round(2)
    to.sort_values("registeredVoters", ascending=False)
    return (to,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Turnout Perecentage
    - The average turnout rate across all regions is the same as senate_25 (78.90%)
    - OAV and LAV are also outliers
        - OAV is an outlier because OFWs may not be able to vote at their given embassy
        - LAV only accounts for special individuals who do not vote at their registered precinct.
    """)
    return


@app.cell
def _(plt, sns, to):
    plt.figure(figsize=(14, 6))
    sns.set_style("whitegrid")
    to.index = to.index.str.replace("CORDILLERA ADMINISTRATIVE REGION", "CAR")
    to.index = to.index.str.replace("NATIONAL CAPITAL REGION", "NCR")

    bp = sns.barplot(data=to.reset_index().sort_values("turnoutPercentage", ascending=False), 
                x="region", y="turnoutPercentage")

    bp.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    for p in bp.patches:
        bp.annotate(f'{p.get_height():,.0f}', 
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha='center', va='bottom', fontsize=7)

    avg = to["turnoutPercentage"].mean()
    bp.axhline(avg, color='red', linestyle='--', linewidth=1, label=f'Average: {avg:.2f}%')
    bp.legend()

    plt.xticks(rotation=45, ha="right")
    plt.title("Turnout percentage per Region")
    plt.xlabel("Region")
    plt.ylabel("Turnout percentage")
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()
