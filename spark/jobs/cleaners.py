import re
import sys
from functools import reduce

sys.path.insert(0, "/opt/spark/src")

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, LongType

import config as con


# Arguments to pass both collection and output path. (In our context it would be raw_senate or raw_partylist data)
collection = sys.argv[1]
output_path = sys.argv[2]


spark = (
    SparkSession.builder.appName("Polis")
    .config("spark.sql.parquet.compression.codec", "none")
    .config("spark.sql.debug.maxToStringFields", "200")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

df = (
    spark.read.format("mongodb")
    .option("connection.uri", con.MONGO_URL)
    .option("database", "polis")
    .option("collection", collection)
    .load()
)


# check for negatives
def check_negatives(df: DataFrame) -> DataFrame:
    """
    Checks all numerical columns if they have negative numbers.
    This is important because voting machines cannot recieve negative numbers (unless machine is broken or it was tampered with.)
    """
    numeric_cols = [
        f.name
        for f in df.schema.fields
        if isinstance(f.dataType, (IntegerType, LongType))
    ]
    conditions = [F.col(f"`{c}`") < 0 for c in numeric_cols]
    condition: Column = reduce(lambda a, b: a | b, conditions)
    negative_rows = df.filter(condition)
    count = negative_rows.count()
    if count > 0:
        raise ValueError(f"Found {count} rows with negative values, aborting job.")
    print("Negative check passed: no negative values found")
    return df


# check of vote turnout is invalid
def invalid_turnout(df: DataFrame) -> DataFrame:
    """
    Checks the count of actual_voters and registered_voters
    actual_voters cannot exceed registered_voters as non-registered individuals cannot vote.
    """
    condition: Column = F.col("actualVoters") > F.col("registeredVoters")
    invalid_rows = df.filter(condition)
    count = invalid_rows.count()
    if count > 0:
        raise ValueError(
            f"Found {count} rows where actual voters exceed registered voters, aborting job."
        )
    print("Vote turnout is valid: Actual voters and registered voters add up.")
    return df


def region_checking(df: DataFrame) -> DataFrame:
    """
    Checks all regions to ensure that there are no invalid regions (follows COMELEC's different regions)
    """
    expected_regions = {
        "REGION I",
        "REGION II",
        "REGION III",
        "REGION IV-A",
        "REGION IV-B",
        "REGION V",
        "REGION VI",
        "REGION VII",
        "REGION VIII",
        "REGION IX",
        "REGION X",
        "REGION XI",
        "REGION XII",
        "REGION XIII",
        "NATIONAL CAPITAL REGION",
        "CORDILLERA ADMINISTRATIVE REGION",
        "BARMM",
        "NIR",
        "OAV",
        "LAV",
    }
    condition: Column = ~F.col("region").isin(expected_regions)
    invalid_rows = df.filter(condition)
    count = invalid_rows.count()
    if count > 0:
        raise ValueError(
            f"Found {count} of rows which have regions that do not match COMELEC's election jurisdiction"
        )
    print("Regions are valid: All regions fit COMELECs data.")
    return df


# normalize columns
def normalize_columns(df: DataFrame) -> DataFrame:
    """
    Changes column names from camelCase to snake_case for readability and to follow python syntax.
    Converts all columns to UPPERCASE to follow the format of the candidate names.
    """
    snake_cols = [
        re.sub(r"(?<=[a-z])(?=[A-Z])", "_", col).upper() for col in df.columns
    ]
    return df.toDF(*snake_cols)


# separate OAV & LAV
def separate_df(df: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]:
    """
    Separates OAV and LAV from domestic votes.
    """
    oav = df.where(F.col("REGION") == "OAV")
    lav = df.where(F.col("REGION") == "LAV")
    domestic = df.where(~F.col("REGION").isin("LAV", "OAV"))
    return oav, lav, domestic


check_negatives(df)
invalid_turnout(df)
region_checking(df)
df = normalize_columns(df)

oav, lav, domestic = separate_df(df)

oav.write.mode("overwrite").parquet(f"{output_path}/oav")
lav.write.mode("overwrite").parquet(f"{output_path}/lav")
domestic.write.mode("overwrite").parquet(f"{output_path}/domestic")

spark.read.parquet(f"{output_path}/domestic").printSchema()
print(f"Total OAV count: {spark.read.parquet(f'{output_path}/oav').count()}")
print(f"Total LAV count: {spark.read.parquet(f'{output_path}/lav').count()}")
print(f"Total domestic count: {spark.read.parquet(f'{output_path}/domestic').count()}")
