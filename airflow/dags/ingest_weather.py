from datetime import datetime
from airflow.decorators import dag, task
import sys

sys.path.append('/opt/airflow/ingestion')


@dag(
    dag_id='ingest_weather',
    start_date=datetime(2026, 7, 1),
    schedule='@daily',
    catchup=False,
)
def ingest_weather_dag():

    @task
    def fetch_and_save_weather():
        from weather_client import get_weather, save_weather
        lat, lon = 48.8566, 2.3522
        data = get_weather(lat, lon)
        save_weather(data, lat, lon)

    fetch_and_save_weather()


ingest_weather_dag()