import sys

sys.path.insert(0, "/opt/spark/src")

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, LongType

import config as con

output_path = sys.argv[1]

spark = (
    SparkSession.builder.appName("Polis")
    .config("spark.sql.parquet.compression.codec", "none")
    .config("spark.sql.debug.maxToStringFields", "200")
    # Executor must fit in the ~8G Docker VM alongside MongoDB and Airflow;
    # in-code conf takes precedence over spark-submit --conf
    .config("spark.executor.memory", "2g")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

df = (
    spark.read.format("mongodb")
    .option("connection.uri", con.MONGO_URL)
    .option("database", "polis")
    .option("collection", "raw_election_results")
    .option(
        "aggregation.pipeline",
        '[{"$match": {"Position": {"$in": ["Senator", "Party List"]}}}]',
    )
    .option(
        "partitioner",
        "com.mongodb.spark.sql.connector.read.partitioner.SamplePartitioner",
    )
    .option("partitionerOptions.partitionSizeMB", "64")
    .load()
    # Cache after the first action: every count() below is a separate action,
    # and without this each one re-reads all ~3M documents from MongoDB
    .persist()
)


def check_negatives(df: DataFrame) -> DataFrame:
    """
    Checks all numerical columns for negative values.
    Voting machines cannot record negative votes.
    """
    numeric_cols = [
        f.name
        for f in df.schema.fields
        if isinstance(f.dataType, (IntegerType, LongType))
    ]
    row_min: Column = F.least(*[F.col(f"`{c}`") for c in numeric_cols])
    negative_rows = df.filter(row_min < 0)
    count = negative_rows.count()
    if count > 0:
        raise ValueError(f"Found {count} rows with negative values, aborting job.")
    print("Negative check passed: no negative values found")
    return df


def invalid_turnout(df: DataFrame) -> DataFrame:
    """
    Checks that Votes does not exceed Total_Voters.
    A precinct cannot report more votes than registered voters.
    """
    condition: Column = F.col("Votes") > F.col("Total_Voters")
    invalid_rows = df.filter(condition)
    count = invalid_rows.count()
    if count > 0:
        raise ValueError(
            f"Found {count} rows where votes exceed total voters, aborting job."
        )
    print("Vote turnout is valid: Votes do not exceed Total_Voters.")
    return df


def region_checking(df: DataFrame) -> DataFrame:
    """
    Checks all regions against COMELEC's known jurisdictions.
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
    condition: Column = ~F.col("Region").isin(expected_regions)
    invalid_rows = df.filter(condition)
    count = invalid_rows.count()
    if count > 0:
        raise ValueError(
            f"Found {count} rows with regions outside COMELEC jurisdiction, aborting job."
        )
    print("Region check passed: all regions valid.")
    return df


def deduplicate(df: DataFrame) -> DataFrame:
    """
    Deduplicates on (Precinct_Code, Candidate_Name) — the natural key for this dataset.
    Candidate_ID is unreliable (0 for all senators); Candidate_Name is the correct identifier.
    """
    before = df.count()
    df = df.dropDuplicates(["Precinct_Code", "Candidate_Name"])
    after = df.count()
    print(
        f"Deduplication: {before - after:,} duplicate rows removed, {after:,} rows retained"
    )
    return df


def drop_unreliable_columns(df: DataFrame) -> DataFrame:
    """
    Drops Candidate_ID and Contest_ID — both are 0 for all senatorial records
    and unreliable across the dataset.
    """
    df = df.drop("Candidate_ID", "Contest_ID")
    print("Dropped unreliable columns: Candidate_ID, Contest_ID")
    return df


def normalize_columns(df: DataFrame) -> DataFrame:
    """
    Converts column names to SCREAMING_SNAKE_CASE for consistency
    with senate_25 and partylist_25 Parquet outputs.
    """
    screaming_cols = [col.upper() for col in df.columns]
    return df.toDF(*screaming_cols)


check_negatives(df)
invalid_turnout(df)
region_checking(df)
df = deduplicate(df)
df = drop_unreliable_columns(df)
df = normalize_columns(df)

df.write.mode("overwrite").parquet(output_path)

print(f"Total rows written: {spark.read.parquet(output_path).count():,}")
spark.read.parquet(output_path).printSchema()
