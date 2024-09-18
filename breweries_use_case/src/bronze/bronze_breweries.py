"""Bronze layer loader."""

import sys
import json
from datetime import date
import requests
import sys

import logging
def bronze_breweries_task():
    logger = logging.getLogger("airflow.task")
    logger.info("Iniciando o script bronze_breweries.py")
    
    # Seu código aqui...
    
    logger.info("Finalizando o script bronze_breweries.py")
    
bronze_breweries_task()

sys.path.append('/opt/airflow/breweries_use_case/utils')

import render

# Setup variableclaes
ENDPOINT = render.get_yaml_value("breweries_endpoint")
BRONZE_LOCATION = render.get_yaml_value("bronze_location")
FILE_NAME = render.get_yaml_value("file_name")


# Get response
response = requests.get(ENDPOINT).json()

# Serialize json
json_object = json.dumps(response, indent=4)

# Define file name
print(BRONZE_LOCATION + FILE_NAME + date.today().strftime("%Y%m%d") + ".json")

file_name = BRONZE_LOCATION + FILE_NAME + date.today().strftime("%Y%m%d") + ".json"

# Write data
with open(file_name, "w") as outfile:
    outfile.write(json_object)
