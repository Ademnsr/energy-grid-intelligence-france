from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


@dag(
    dag_id='run_dbt_models',
    start_date=datetime(2026, 7, 1),
    schedule='@daily',
    catchup=False,
)
def run_dbt_dag():

    run_dbt = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir /home/airflow/.dbt',
    )

    run_dbt


run_dbt_dag()