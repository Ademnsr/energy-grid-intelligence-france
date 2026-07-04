import base64
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth/"
CONSUMPTION_URL = "https://digital.iservices.rte-france.com/open_api/consumption/v1/short_term"


def get_rte_token() -> str:
    client_id = os.getenv("RTE_CLIENT_ID")
    client_secret = os.getenv("RTE_CLIENT_SECRET")

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {"Authorization": f"Basic {encoded_credentials}"}
    response = requests.post(TOKEN_URL, headers=headers)
    response.raise_for_status()

    return response.json()["access_token"]


def get_consumption(token: str) -> dict:
    now = datetime.now().astimezone()
    start = now - timedelta(days=7)

    def format_date(dt):
        s = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        return s[:-2] + ":" + s[-2:]

    params = {
        "start_date": format_date(start),
        "end_date": format_date(now),
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(CONSUMPTION_URL, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    token = get_rte_token()
    data = get_consumption(token)
    print(f"Nombre de séries : {len(data['short_term'])}")
    print(f"Première série : type={data['short_term'][0]['type']}, "
          f"{len(data['short_term'][0]['values'])} valeurs")