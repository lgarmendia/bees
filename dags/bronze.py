import os
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime
import subprocess

def run_local_python_script():
   
    script_path = "/opt/airflow/breweries_use_case/src/bronze/bronze_breweries.py"
    # Usando subprocess para executar o script
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
    description='DAG to execute the bronze_breweries.py script',
    start_date=datetime(2024, 9, 12, 00, 00),
    schedule_interval="0 6 * * *",
    dagrun_timeout=timedelta(hours=2),
    catchup=False
) as dag:

    # Tarefa para executar o script Python local
    executar_script = PythonOperator(
        task_id='exec_bronze',
        python_callable=run_local_python_script
    )

    TriggerDag = TriggerDagRunOperator(
        task_id='trigger_dag_silver',
        trigger_dag_id="exec_silver",
        wait_for_completion=True
    )
    executar_script >> TriggerDag
