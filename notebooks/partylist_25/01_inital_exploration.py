import marimo

__generated_with = "0.23.8"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    mo.md("# PARTYLIST_25 EDA")
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyzing Columns
    """)
    return


@app.cell
def _():
    # Importing pandas and loading the partylist_25 csv file
    import pandas as pd
    df = pd.read_csv('../../datasets/partylist25-final_updated.csv')
    return df, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data types of each column
    - It follows the same structure as senate_25
        - object data types take the form of strings and describe where the precinct and voting took place
        - the rest are int6 and describes the vount counting machine id, and details on the votes
        - the rest of the columns are also int64 and show the total votes for each partylist
    """)
    return


@app.cell
def _(df):
    print(df.info(verbose=True))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Loading the first 10 records
    - Data seems to be valid and complete
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
    ### Checking for NULLs
    - All of the data has no NULLs present
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
    - Region and province data has the same counts as the senate_25 database
    - Region and province both have higher counts than expected, this could be either OAV, LAV or NIR votes
    - The count of barangay's may be lower compared to the total barangays in the Philippines because of COMELEC's Clustered Precinct System.
    """)
    return


@app.cell
def _(df):
    print("Unique count in region:", df['region'].nunique())
    print("Unique count in province:", df['province'].nunique())
    print("Unique count in municipality:", df['municipality'].nunique())
    print("Unique count in barangay:", df['barangay'].nunique())
    return


@app.cell
def _(df):
    # Investigating the additional 3 regions (expected 17)
    df['region'].unique()
    return


@app.cell
def _(df):
    df.iloc[:, 12:].sum()
    return


if __name__ == "__main__":
    app.run()
