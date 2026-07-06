# Energy Grid Intelligence France

End-to-end data engineering pipeline that ingests French electricity consumption and weather data, transforms it with dbt, orchestrates everything with Airflow, and serves analytics through a REST API.

*Version française disponible plus bas : [Version française](#version-française)*

## Architecture

```
 RTE API (eco2mix)          Open-Meteo API
 national consumption       weather (Paris)
        |                         |
        v                         v
 +---------------------------------------+
 |        Python ingestion clients       |
 |  (OAuth2 + upsert, idempotent runs)   |
 +---------------------------------------+
                    |
                    v
 +---------------------------------------+
 |          PostgreSQL 16 (Docker)       |
 |          schema raw: 2 tables         |
 +---------------------------------------+
                    |
                    v
 +---------------------------------------+
 |                  dbt                  |
 |   staging views -> marts, 8 tests     |
 +---------------------------------------+
                    |
                    v
 +---------------------------------------+
 |              FastAPI                  |
 |  /health  /consumption/hourly  /daily |
 +---------------------------------------+

 Apache Airflow 3 (CeleryExecutor) orchestrates
 the whole chain with 3 daily DAGs.
```

## Tech stack

| Layer | Tool |
|---|---|
| Ingestion | Python 3.12, requests, psycopg2 |
| Storage | PostgreSQL 16 (Docker) |
| Transformation | dbt-core (dbt-postgres) |
| Orchestration | Apache Airflow 3.2 (CeleryExecutor, Redis) |
| Serving | FastAPI, Uvicorn |
| Packaging | uv |
| Infrastructure | Docker Compose |

## Data sources

- **RTE (Réseau de Transport d'Électricité)**: national electricity consumption in MW, 15 minute resolution, via the official `consumption/v1/short_term` API with OAuth2 client credentials. Rolling 7 day window on each run.
- **Open-Meteo**: current weather observations for Paris (temperature, humidity, wind speed), no authentication required.

## Key engineering decisions

- **Idempotent ingestion**: raw tables carry a unique constraint on their natural key, and inserts use `ON CONFLICT ... DO UPDATE`. Running a DAG twice never creates duplicates, and revised values published by RTE overwrite stale ones.
- **Two separate PostgreSQL instances**: one for business data, one for Airflow metadata. The pipeline database stays clean and portable.
- **dbt models use `ref()`**: dependencies between staging and mart models are explicit, so dbt builds them in the correct order.
- **Data quality tests**: 8 dbt tests (`not_null`, `unique`) run on staging models.

## Project structure

```
.
|-- api/                  FastAPI application
|   |-- main.py           app entrypoint, router registration
|   |-- database.py       PostgreSQL connection helper
|   `-- routers/          /health and /consumption endpoints
|-- airflow/
|   `-- dags/             3 DAGs: ingest_energy, ingest_weather, run_dbt_models
|-- db/
|   `-- init.sql          raw schema and tables DDL (unique constraints)
|-- dbt/
|   `-- models/
|       |-- staging/      1:1 views over raw tables + schema tests
|       `-- marts/        hourly and daily consumption aggregates
|-- ingestion/
|   |-- eco2mix_client.py RTE OAuth2 client, fetch + upsert
|   `-- weather_client.py Open-Meteo client, fetch + upsert
|-- docker-compose.yml    business PostgreSQL + full Airflow stack
`-- pyproject.toml        Python dependencies (managed with uv)
```

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Service health check |
| `GET /consumption/hourly` | Average, min, max consumption per hour of day |
| `GET /consumption/daily` | Daily aggregates: average, min, max, total, observation count |

Example response from `/consumption/daily`:

```json
{
  "day": "2026-07-01",
  "avg_consumption_mw": 46651.99,
  "min_consumption_mw": 38109,
  "max_consumption_mw": 52762,
  "total_consumption_mw": 4431939,
  "nb_observations": 95
}
```

## Running the project locally

Prerequisites: Docker Desktop, [uv](https://docs.astral.sh/uv/), and free RTE API credentials from [data.rte-france.com](https://data.rte-france.com).

```bash
# 1. Clone and configure
git clone https://github.com/Ademnsr/energy-grid-intelligence-france.git
cd energy-grid-intelligence-france
cp .env.example .env
# fill in: RTE_CLIENT_ID, RTE_CLIENT_SECRET, POSTGRES_PASSWORD,
# FERNET_KEY (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# AIRFLOW_UID (id -u on Linux, 50000 otherwise)

# 2. Start PostgreSQL and the Airflow stack
docker compose up -d

# 3. Create the raw schema and tables
docker exec -i energy_postgres psql -U energy_admin -d energy_grid < db/init.sql

# 4. Install Python dependencies
uv sync

# 5. Configure dbt: create ~/.dbt/profiles.yml with an "energy_grid" profile
#    (type: postgres, host: localhost, port: 5432, dbname: energy_grid,
#     schema: public, user/pass from your .env)

# 6. Trigger the DAGs from the Airflow UI
#    http://localhost:8080 (default credentials: airflow / airflow)
#    Order: ingest_energy, ingest_weather, then run_dbt_models

# 7. Start the API
uv run uvicorn api.main:app --reload
# http://localhost:8000/docs for the interactive Swagger UI
```

## Possible improvements

- Regional consumption endpoint backed by the ODRE `eco2mix-regional-tr` open dataset
- Join weather and consumption marts to analyze temperature sensitivity of the grid
- dbt incremental materializations once data volume grows
- CI pipeline running dbt tests on every push

---

# Version française

Pipeline de data engineering de bout en bout : ingestion de la consommation électrique française et de données météo, transformation avec dbt, orchestration avec Airflow, et exposition via une API REST.

## Architecture

Le schéma est identique à la version anglaise ci-dessus : deux APIs publiques (RTE et Open-Meteo) sont interrogées par des clients Python, les données brutes sont stockées dans PostgreSQL (schéma `raw`), dbt construit des vues de staging puis des marts d'agrégation, et FastAPI expose le résultat. Apache Airflow orchestre la chaîne complète avec 3 DAGs quotidiens.

## Sources de données

- **RTE (Réseau de Transport d'Électricité)** : consommation électrique nationale en MW, au pas de 15 minutes, via l'API officielle `consumption/v1/short_term` avec authentification OAuth2. Fenêtre glissante de 7 jours à chaque exécution.
- **Open-Meteo** : observations météo courantes pour Paris (température, humidité, vent), sans authentification.

## Choix d'ingénierie notables

- **Ingestion idempotente** : les tables brutes portent une contrainte unique sur leur clé naturelle et les insertions utilisent `ON CONFLICT ... DO UPDATE`. Relancer un DAG ne crée jamais de doublons, et les valeurs révisées publiées par RTE écrasent les anciennes.
- **Deux instances PostgreSQL séparées** : une pour les données métier, une pour les métadonnées Airflow.
- **Modèles dbt avec `ref()`** : les dépendances entre staging et marts sont explicites, dbt construit donc les vues dans le bon ordre.
- **Tests de qualité de données** : 8 tests dbt (`not_null`, `unique`) sur les modèles de staging.

## Endpoints de l'API

| Endpoint | Description |
|---|---|
| `GET /health` | Vérification de l'état du service |
| `GET /consumption/hourly` | Consommation moyenne, min, max par heure de la journée |
| `GET /consumption/daily` | Agrégats journaliers : moyenne, min, max, total, nombre d'observations |

## Lancer le projet en local

Les étapes détaillées figurent dans la section anglaise ci-dessus : configuration du fichier `.env`, démarrage de la stack avec `docker compose up -d`, création du schéma avec `db/init.sql`, installation des dépendances avec `uv sync`, configuration du profil dbt, déclenchement des DAGs depuis l'interface Airflow (http://localhost:8080), puis lancement de l'API avec `uv run uvicorn api.main:app --reload`.

## Améliorations possibles

- Endpoint de consommation régionale via le jeu de données ouvert ODRE `eco2mix-regional-tr`
- Croisement des marts météo et consommation pour analyser la sensibilité du réseau à la température
- Matérialisations incrémentales dbt quand le volume augmentera
- Pipeline CI exécutant les tests dbt à chaque push
