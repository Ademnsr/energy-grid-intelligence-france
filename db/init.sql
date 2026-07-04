CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.weather_observations (
    id SERIAL PRIMARY KEY,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    temperature_2m NUMERIC,
    relative_humidity_2m NUMERIC,
    wind_speed_10m NUMERIC,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.energy_observations (
    id SERIAL PRIMARY KEY,
    period_type TEXT NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    consumption_mw NUMERIC NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);