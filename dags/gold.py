import os
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime
import subprocess

def run_local_python_script():
    
    script_path = "/opt/airflow/breweries_use_case/src/gold/gold_breweries.py"
    subprocess.run(['python', script_path], check=True)

default_args = {
    'owner': 'airflow',
    'email': ['lucas.garmendia@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

with DAG(
    'exec_gold',
    dagrun_timeout=timedelta(hours=2),
    default_args=default_args,
    description='DAG to execute the gold_breweries.py script.',
    start_date=datetime(2024, 9, 12, 00, 00),
    schedule_interval=None,
    catchup=False
) as dag:

    # Task to execute the local Python script.
    exec_script = PythonOperator(
        task_id='exec_gold',
        python_callable=run_local_python_script
    )

    exec_script
