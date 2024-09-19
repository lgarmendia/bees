"""Silver layer loader."""


import os
import sys
import pyspark
from datetime import datetime
from delta import configure_spark_with_delta_pip
from pyspark.sql.functions import input_file_name, lit, max

sys.path.append('/opt/airflow/breweries_use_case/utils')


import render

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# setup a builder for a spark session
# https://docs.delta.io/latest/quick-start.html#language-python
builder = (
    pyspark.sql.SparkSession.builder.appName("silver_breweries")
    .master("local")
    # .config("spark.driver.memory", "4g")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
)
BRONZE_LOCATION = render.get_yaml_value("bronze_location")
SILVER_LOCATION = render.get_yaml_value("silver_location")
# # # create spark session
spark = configure_spark_with_delta_pip(builder).getOrCreate()

def get_max_processed_date(delta_path: str) -> str:
    """Get the max date of a given delta location.

    :param delta_path: the delta path to get the max data.
    :return: str
    """
    try:
       
        df = spark.read.load(delta_path)
       
        return df.select(max(df.created_on)).collect()[0][0].strftime("%Y%m%d")
    except Exception:
        return "19000101"


def list_bronze_files(bronze_path: str, max_processed_date: str) -> list:
    """List all files to be processed.

    :param bronze_path: the bronze path location to list files to be processed.
    :param max_processed_date: the max processed data from the target location.
    :return: list
    """
    files_to_process = []
    for path in os.listdir(bronze_path):
        files_to_process = []
        for path in os.listdir(bronze_path):
            # Verifica se o caminho atual é um arquivo
            if (
                os.path.isfile(os.path.join(bronze_path, path))
                and path.endswith(".json") 
                and path.split("_")[1].split(".")[0] > max_processed_date
            ):
                # Concatena o caminho corretamente e substitui as barras invertidas
                file_path = os.path.join(bronze_path, path).replace("\\", "")
                files_to_process.append(file_path)
    return files_to_process if files_to_process else files_to_process.append(bronze_path)


def load_data(src_location: str, tgt_location: str, rerun: bool = False):
   
    """Load data.

        If flag rerun is set to True, the process takes all files from the bronze location.

    :param src_location: source location.
    :param tgt_location:  target location.
    :param rerun:  target location.
    """
    list_to_process = []
    
    if list_bronze_files(src_location, get_max_processed_date(tgt_location)) and not rerun:
        # Print the list of files to be processed
       
        print(
            "LIST OF FILES TO BE PROCESSED:",
            list_bronze_files(src_location, get_max_processed_date(tgt_location)),
        )
        list_to_process = list_bronze_files(src_location, get_max_processed_date(tgt_location))
    elif rerun:
        list_to_process.append(src_location)
    else:
        print("No files to process.")

    if list_to_process:
        
        # Read data from bronze layer        
        df = spark.read.option("multiline", "true").json(list_to_process)
        
        # Create process date
        df = df.withColumn("created_on", lit(datetime.now())).withColumn(
            "file_path", input_file_name()
        )
        # Write data partitioned by country, state
        df.write.format("delta").mode("overwrite").option("mergeSchema", "True").partitionBy(
            "country", "state"
        ).save(tgt_location)

load_data(BRONZE_LOCATION, SILVER_LOCATION + "silver_breweries")
