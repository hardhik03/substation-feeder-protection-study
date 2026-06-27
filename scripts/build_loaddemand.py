import os
import sys
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

if EIA_API_KEY is None:
    raise ValueError("EIA_API_KEY not found. Check that .env exists.")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from system_parameters import GRID_REGION

BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'eia_cache.csv')

def save_cache(records):
    """Save fetched EIA records to CSV as fallback for future runs."""
    import csv
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f'Cache saved to: {CACHE_PATH}')


def load_cache():
    """Load EIA records from cache when live API is unavailable."""
    import csv
    if not os.path.exists(CACHE_PATH):
        raise FileNotFoundError(
            'No EIA cache found and live API fetch failed. '
            'Run with a valid EIA_API_KEY at least once to create the cache.'
        )
    with open(CACHE_PATH, 'r') as f:
        reader = csv.DictReader(f)
        records = list(reader)
    print(f'WARNING: Using cached EIA data from {CACHE_PATH}')
    print(f'         Live API unavailable — results may not reflect current grid conditions')
    return records

def get_latest_available_period(api_key, region=GRID_REGION):
    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": region,
        "facets[type][]": "D",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 2,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    records = response.json()["response"]["data"]

    for record in records:
        if float(record["value"]) > 0:
            return datetime.strptime(record["period"], "%Y-%m-%dT%H")

    raise ValueError("No valid non-zero period found in recent data")


def fetch_24hr_demand(api_key, region=GRID_REGION):
    end_time = get_latest_available_period(api_key, region)
    start_time = end_time - timedelta(hours=23)

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
        "length": 24,
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()["response"]["data"]

def clean_and_normalize(records):
    values = [float(r["value"]) for r in records]
    median_val = sorted(values)[len(values) // 2]
    threshold = median_val * 0.1

    # Replace zero/implausible values with linear interpolation
    cleaned = values.copy()
    flagged = [i for i, v in enumerate(values) if v < threshold]

    for i in flagged:
        left = next((j for j in range(i-1, -1, -1) if j not in flagged), None)
        right = next((j for j in range(i+1, len(values)) if j not in flagged), None)

        if left is not None and right is not None:
            cleaned[i] = cleaned[left] + (cleaned[right] - cleaned[left]) * (i - left) / (right - left)
        elif left is not None:
            cleaned[i] = cleaned[left]
        elif right is not None:
            cleaned[i] = cleaned[right]

        print(f"Flagged hour {i}: raw={values[i]:.0f} MWh → "
              f"interpolated={cleaned[i]:.0f} MWh")

    # Normalize to 0-1 range relative to peak
    peak = max(cleaned)
    multipliers = [round(v / peak, 4) for v in cleaned]

    print(f"\nPeak demand: {peak:.0f} MWh")
    print(f"Multiplier range: {min(multipliers):.4f} to {max(multipliers):.4f}")

    return multipliers

def write_loadshape(multipliers, output_path):
    mult_str = ' '.join(str(m) for m in multipliers)
    
    dss_content = f"""! LoadShape generated from EIA WACM real demand data
! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
! Region: {GRID_REGION}
! Hours: {len(multipliers)}

New LoadShape.WACMProfile
~ npts={len(multipliers)}
~ interval=1
~ mult=({mult_str})
~ useactual=no

"""
    with open(output_path, 'w') as f:
        f.write(dss_content)

    print(f"\nLoadShape written to: {output_path}")


if __name__ == "__main__":
    print("Fetching WACM demand data from EIA...")
    try:
        records = fetch_24hr_demand(EIA_API_KEY)
        print(f"Records fetched: {len(records)}")
        print(f"Period: {records[0]['period']} to {records[-1]['period']}")
        save_cache(records)
    except Exception as e:
        print(f"Live fetch failed: {e}")
        print("Falling back to cache...")
        records = load_cache()
    print()

    print("Cleaning and normalizing...")
    multipliers = clean_and_normalize(records)
    print()

    output_path = os.path.join(
        os.path.dirname(__file__), '..', 'models', 'loadshape_wacm.dss'
    )
    write_loadshape(multipliers, os.path.abspath(output_path))