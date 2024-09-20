import os
import timedelta 

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime
import subprocess

def run_local_python_script():
    
    script_path = "/opt/airflow/breweries_use_case/src/bronze/bronze_breweries.py"
    subprocess.run(['python', script_path], check=True)

default_args = {
    'owner': 'airflow',
    'email': ['lucas.garmendia@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

with DAG(
    'exec_bronze',
    default_args=default_args,
    dagrun_timeout=timedelta(hours=2),
    description='DAG to execute the bronze_breweries.py script.',
    start_date=datetime(2024, 10, 12, 00, 00),
    schedule_interval=None,
    catchup=False
) as dag:

    # Task to execute the local Python script.
    exec_script = PythonOperator(
        task_id='exec_bronze',
        python_callable=run_local_python_script
    )

    TriggerDag = TriggerDagRunOperator(
        task_id='trigger_dag_silver',
        trigger_dag_id="exec_silver",
        wait_for_completion=True
    )
    
    exec_script >> TriggerDag 