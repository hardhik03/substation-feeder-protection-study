import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

if EIA_API_KEY is None:
    raise ValueError("EIA_API_KEY not found. Check that .env exists and contains it.")

sys.path.insert(0, "config")
from system_parameters import GRID_REGION

BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


def get_latest_available_period(api_key, region=GRID_REGION):
    """Ask EIA what the most recent published demand timestamp actually is,
    rather than assuming. Returns a datetime object."""
    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": region,
        "facets[type][]": "D",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    latest_period_str = response.json()["response"]["data"][0]["period"]
    return datetime.strptime(latest_period_str, "%Y-%m-%dT%H")


def get_hourly_demand(api_key, region=GRID_REGION, hours_back=24):
    end_time = get_latest_available_period(api_key, region)
    start_time = end_time - timedelta(hours=hours_back)

    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": region,
        "facets[type][]": "D",
        "start": start_time.strftime("%Y-%m-%dT%H"),
        "end": end_time.strftime("%Y-%m-%dT%H"),
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "offset": 0,
        "length": 100,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    data = get_hourly_demand(EIA_API_KEY)
    records = data["response"]["data"]
    print("Number of records returned:", len(records))
    print()
    for r in records:
        print(r["period"], "->", r["value"], r["value-units"])