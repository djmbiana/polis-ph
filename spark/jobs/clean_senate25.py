import sys

sys.path.insert(0, "/opt/spark/src")

from pyspark.sql import SparkSession

import config as con

spark = SparkSession.builder.appName("Polis").getOrCreate()

df = (
    spark.read.format("mongodb")
    .option("connection.uri", con.MONGO_URL)
    .option("database", "polis")
    .option("collection", "raw_senate_25")
    .load()
)

df.show()
