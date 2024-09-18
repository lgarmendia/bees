"""Silver layer loader."""

import os
import sys

import pyspark
from delta import configure_spark_with_delta_pip
from pyspark.sql.functions import lit, max
sys.path.append('/opt/airflow/breweries_use_case/utils')


import render


os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# setup a builder for a spark session
# https://docs.delta.io/latest/quick-start.html#language-python
builder = (
    pyspark.sql.SparkSession.builder.appName("silver_breweries")
    .master("local")
    .config("spark.driver.memory", "8g")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
)

# create spark session
spark = configure_spark_with_delta_pip(builder).getOrCreate()

SILVER_LOCATION = render.get_yaml_value("silver_location")
GOLD_LOCATION = render.get_yaml_value("gold_location")


def get_max_processed_file(delta_path: str) -> any:
    """Get the max processed file from a given delta location.

    :param delta_path: the delta path to get the max data.
    :return: any
    """
    try:
        df = spark.read.load(delta_path)
        return df.select(max(df.file_path)).collect()[0][0]
    except Exception:
        return None


def load_data(src_location: str, tgt_location: str):
    """Load data.

    :param src_location: source location.
    :param tgt_location:  target location.
    :return: list
    """
    # Get the latest date from silver and process it.
    if get_max_processed_file(src_location):
        df = spark.read.format("delta").load(src_location)
        df.filter(df.file_path == lit(get_max_processed_file(src_location))).groupBy(
            "brewery_type", "country", "state"
        ).count().withColumnRenamed("count", "quantity").write.format("delta").mode(
            "overwrite"
        ).option("mergeSchema", "True").partitionBy("country").save(tgt_location)
    else:
        print("There's no data to be processed.")


load_data(SILVER_LOCATION + "silver_breweries", GOLD_LOCATION + "gold_breweries")