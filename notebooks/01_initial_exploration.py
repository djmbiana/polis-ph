import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md("# SENATE_25 EDA")
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyzing Columns
    """)
    return


@app.cell
def _():
    # Importing pandas and loading the senate25-final csv file
    import pandas as pd
    df = pd.read_csv("../datasets/senate25-final_updated.csv")
    return df, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data types of each column:
    - The object data types describe where the voting took place
    - The rest of the data types present are integers
        - **MachineID:**  Id of the vote counting machine used in the precinct
        - **registeredVoters, actualVoters, validBallot, overVotes, underVotes:** Numeric values which dictate how many registered voters there were in that area, how many ballots were valid, and how many votes went over, under, and the resulting obtained votes
        - The rest of the columns are for each of the candidates present in this election.

    ### Checking unique values present in each column
    - The region and province have a higher count than what the country actually has, this could be either our OAV or LAV votes
    - The count of barangay's may be lower compared to the total barangays in the Philippines because of COMELEC's Clustered Precinct System.
    - To save on resources and money, COMELEC establishes a singular clustered precinct which can host multiple small barangays within the precincts general area.
    """)
    return


@app.cell
def _(df):
    print(df.info())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Viewing the first 10 records
    - Data seems to be valid and complete
    - Might be nice to consider collapsing underVotes and validBallot into one as they are both still counted as valid to total votes
    - Should also consider renaming the columns from camelCase to snake_case for readability and consistency throughout the project
    """)
    return


@app.cell
def _(df, pd):
    pd.set_option('display.max_columns', None)
    print(df.head(10))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Checking for Nulls
    - All rows have no NULL's present
    - Each column returns an int of '0' meaning that there are no nulls present
    """)
    return


@app.cell
def _(df):
    df.isnull().sum()[df.columns]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Checking unique values present in each column
    - The region and province have a higher count than what the country actually has, this could be either our OAV or LAV votes
    - The count of barangay's may be lower compared to the total barangays in the Philippines because of COMELEC's Clustered Precinct System.
    - To save on resources and money, COMELEC establishes a singular clustered precinct which can host multiple small barangays within the precincts general area.
    """)
    return


@app.cell
def _(df):
    print("Unique count in region:", df['region'].nunique())
    print("Unique count in province:", df['province'].nunique())
    print("Unique count in municipality:", df['municipality'].nunique())
    print("Unique count in barangay:", df['barangay'].nunique())
    return


if __name__ == "__main__":
    app.run()
