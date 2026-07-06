from datetime import datetime
from airflow.decorators import dag, task
import sys

sys.path.append('/opt/airflow/ingestion')


@dag(
    dag_id='ingest_energy',
    start_date=datetime(2026, 7, 1),
    schedule='@daily',
    catchup=False,
)
def ingest_energy_dag():

    @task
    def fetch_and_save_energy():
        from eco2mix_client import get_rte_token, get_consumption, save_consumption
        token = get_rte_token()
        data = get_consumption(token)
        save_consumption(data)

    fetch_and_save_energy()


ingest_energy_dag()