import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# Geographic Analysis")
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    df = pd.read_csv('../datasets/senate25-final_updated.csv')
    return df, plt, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Registered Voters vs Actual Voters per region
    - Registered voters are individuals who have registered under comelec for voting
    - Actual voters are those who actually voted, indicating actual turnouts during the election
    - Region IV-A has the most registered voters
    - Region VII has the highest turnout percentage, meaning that 86.51% of registered voters do end up voting
    - OAV has a lot of registered voters with a turnout percentage of 18.37%. This could indicate that a lot of overseas Filipinos are able to register but are unable to make it to their respective embassies to vote.
    - LAV has the least amount of registered voters with a turnout percentage of 52.07%. This is because these are special individuals (military, media, government officials, etc) who do not vote under their registered precinct, hence the low counts.
    - Keep in mind, turnout percentage only reflects the proportion of registered voters who voted, not the overall voting-age population of each region
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
    ### Turnout percentage
    - The average turnout rate across all regions is 78.90%
    - Most regions under Government jurisdiction have a turnout percentage of 80%+
    - BARMM is an autonomous region with its own governance structure (Bangsamoro Government), which may contribute to its lower turnout of 77%
    - OAV and LAV are outliers as well
        - As mentioned, OAV remains an outlier as overseas filipinos may not be able to vote at their given embassy
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
