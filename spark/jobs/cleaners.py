import re
import sys

sys.path.insert(0, "/opt/spark/src")
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

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


df = normalize_columns(df)

# prints schema so the user is able to see which database was passed
# df.printSchema()

oav, lav, domestic = separate_df(df)

oav.write.mode("overwrite").parquet(f"{output_path}/oav")
lav.write.mode("overwrite").parquet(f"{output_path}/lav")
domestic.write.mode("overwrite").parquet(f"{output_path}/domestic")

spark.read.parquet(f"{output_path}/domestic").printSchema()
print(f"Total OAV count: {spark.read.parquet(f'{output_path}/oav').count()}")
print(f"Total LAV count: {spark.read.parquet(f'{output_path}/lav').count()}")
print(f"Total domestic count: {spark.read.parquet(f'{output_path}/domestic').count()}")
