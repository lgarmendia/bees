# Breweries use case

## Overview
This project consists of three Python scripts designed to load data into a data pipeline with a bronze-silver-gold architecture.

- Bronze Layer: The Bronze layer loader fetches data from an external API and saves it as JSON files. This layer serves as the raw data repository, capturing the data in its original form.

- Silver Layer: The Silver layer loader processes the data from the Bronze layer, applies transformations, and saves the data in a delta format. This stage includes cleaning, filtering, and standardizing the data, making it ready for analysis.

- Gold Layer: The Gold layer loader processes the data from the Silver layer, applies aggregations, and saves the data in a delta format for further analysis. The Gold layer is optimized for reporting and business intelligence purposes, providing curated and refined datasets.

- Data Quality Layer: Before the data is loaded into the Gold layer, a data quality step is applied. This step checks if specific key fields are populated. If these fields are missing, the corresponding records are excluded from being loaded into the Gold layer. However, if there are warnings, such as minor issues or fields that don't prevent the data from being used but still need attention, the records are loaded into the Gold layer with the warning information. This data is also saved for future analysis to identify and address any potential data quality issues.

## Prerequisites
- Docker desktop or Rancher desktop
- Python 3.7 or higher
- Apache Airflow
- PySpark
- Delta Lake
- Required Python packages in requirements.txt

## Installation
**1. Clone the repository:**
```bash
git clone https://github.com/lgarmendia/bees.git
```
**2. Path Docker file:**
cd /path/project/dockerfile

**3. Build Docker image:**
This command may take some time to download the image.
```bash
docker build -t airflow-spark .
```
**4. Docker compose:**
```bash
docker-compose up
```

## Airflow
After starting the Docker image, access the Airflow web interface at http://localhost:8080 using the following credentials:

- Username: airflow
- Password: airflow

In the Airflow dashboard, activate the DAGs to start processing the pipeline.

To execute the complete pipeline: Activate the DAG named exec_bronze. This DAG will sequentially process all stages, from data ingestion in the Bronze layer to the Gold layer.
To execute specific stages: Activate the DAGs corresponding to the desired stages. This allows you to process each phase of the pipeline independently, as needed.

Processed files will be organized into their corresponding folders:
   * bees/breweries_use_case/data/bronze
   * bees/breweries_use_case/data/silver
   * bees/breweries_use_case/data/data_quality
   * bees/breweries_use_case/data/gold

## Monitoring/Alerting
In a production environment, it would be possible to implement monitoring and alerting for the pipeline using Airflow's email configuration. However, since this is a local setup, I did not configure the SMTP server.

To send alert emails, you can configure the SMTP settings and enable notifications for DAG failures. This would require setting the email_on_failure and email_on_retry parameters with specific recipients.

It is also possible to add custom callbacks, such as on_failure_callback, to send alerts to applications like Microsoft Teams or Slack.

## Usage
### Bronze Layer Loader
This script fetches data from a specified API endpoint and saves it in a designated location as a JSON file.
#### How to run manually:
```bash
python bronze_breweries.py
```
### Silver Layer Loader
This script processes the data from the Bronze layer, applying transformations, and saves the output to the Silver layer in a tabular format using delta files.
#### How to run manually:
```bash
python silver_breweries.py
```
### Gold Layer Loader
This script is responsible for processing and transforming the data from the Silver layer and save the results in a delta format in the gold layer.
#### How to run manually:
```bash
python gold_breweries.py
```

### For development purposes:
The project uses Ruff for linting.
#### How to run a lint on the project:
```bash
ruff check .
```
#### How to run a format on the project:
```bash
ruff format .
```
#### How to fix lint issues:
```bash
ruff check . --fix
```
#### For more details about ruff run:
```bash
ruff
```
