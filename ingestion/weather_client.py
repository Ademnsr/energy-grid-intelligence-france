import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_weather(latitude: float, longitude: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def save_weather(data: dict, latitude: float, longitude: float):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cur = conn.cursor()

    current = data["current"]
    cur.execute(
        """
        INSERT INTO raw.weather_observations
            (latitude, longitude, observed_at, temperature_2m, relative_humidity_2m, wind_speed_10m)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (latitude, longitude, observed_at)
        DO UPDATE SET
            temperature_2m = EXCLUDED.temperature_2m,
            relative_humidity_2m = EXCLUDED.relative_humidity_2m,
            wind_speed_10m = EXCLUDED.wind_speed_10m,
            inserted_at = now()
        """,
        (
            latitude,
            longitude,
            current["time"],
            current["temperature_2m"],
            current["relative_humidity_2m"],
            current["wind_speed_10m"],
        ),
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    lat, lon = 48.8566, 2.3522
    data = get_weather(lat, lon)
    save_weather(data, lat, lon)
    print("Observation météo enregistrée dans PostgreSQL.")