# step 1: Data Ingestion
# pulls ridership data from the Chicago Data Portal (Socrata SODA API) and saves raw responses to data/raw/

#imports
import os
import time
import requests 
import pandas as pd
from dotenv import load_dotenv

#get token from .env file
load_dotenv()
token = os.getenv("SOCRATA_APP_TOKEN")

def fetch_dataset(dataset_id, start_date, end_date, token):
    """
    Pulls all rows from a Socrata dataset within a date range, handling pagination.

    Parameters
    ----------
    dataset_id : str
        The Socrata dataset ID (e.g. 'jyb9-n7fm')
    start_date : str
        Start of date range in 'YYYY-MM-DD' format
    end_date : str
        End of date range in 'YYYY-MM-DD' format
    token : str
        Socrata app token for authentication

    Returns
    -------
    pd.DataFrame
        All rows returned by the API for the given date range
    """
    base_url = f"https://data.cityofchicago.org/resource/{dataset_id}.json"
    all_rows = []
    offset = 0
    limit = 1000

    while True:
        params = {
            "$where": f"date >= '{start_date}' AND date <= '{end_date}'",
            "$limit": limit,
            "$offset": offset,
            "$$app_token": token
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()  # blows up immediately if the request failed, easier than silent bad data
        batch = response.json()

        if not batch:
            break

        all_rows.extend(batch)
        print(f"  fetched {len(all_rows)} rows so far...")

        # if we got less than a full page, we've reached the end
        if len(batch) < limit:
            break

        offset += limit
        time.sleep(0.5)  # be polite to the API

    return pd.DataFrame(all_rows)


# dataset IDs from the Chicago Data Portal
BUS_ID = "jyb9-n7fm"
RAIL_ID = "5neh-572f"

# fetch bus ridership for both windows
print("Fetching bus pre-COVID (2018-2019)...")
bus_pre = fetch_dataset(BUS_ID, "2018-01-01", "2019-12-31", token)

print("Fetching bus post-COVID (2022-2024)...")
bus_post = fetch_dataset(BUS_ID, "2022-01-01", "2024-12-31", token)

# fetch rail ridership for both windows
print("Fetching rail pre-COVID (2018-2019)...")
rail_pre = fetch_dataset(RAIL_ID, "2018-01-01", "2019-12-31", token)

print("Fetching rail post-COVID (2022-2024)...")
rail_post = fetch_dataset(RAIL_ID, "2022-01-01", "2024-12-31", token)

# build the path to data/raw/ relative to this script's location, not wherever it's run from
raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# save everything to data/raw/ — these files stay untouched after this point
bus_pre.to_csv(os.path.join(raw_dir, "bus_ridership_2018_2019.csv"), index=False)
bus_post.to_csv(os.path.join(raw_dir, "bus_ridership_2022_2024.csv"), index=False)
rail_pre.to_csv(os.path.join(raw_dir, "rail_ridership_2018_2019.csv"), index=False)
rail_post.to_csv(os.path.join(raw_dir, "rail_ridership_2022_2024.csv"), index=False)

print("Done. All files saved to data/raw/")


def fetch_static(dataset_id, token):
    """
    Pulls all rows from a Socrata dataset with no date filtering — for reference/lookup tables.

    Parameters
    ----------
    dataset_id : str
        The Socrata dataset ID
    token : str
        Socrata app token for authentication

    Returns
    -------
    pd.DataFrame
        All rows in the dataset
    """
    base_url = f"https://data.cityofchicago.org/resource/{dataset_id}.json"
    all_rows = []
    offset = 0
    limit = 1000

    while True:
        params = {
            "$limit": limit,
            "$offset": offset,
            "$$app_token": token
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        all_rows.extend(batch)

        if len(batch) < limit:
            break

        offset += limit
        time.sleep(0.5)

    return pd.DataFrame(all_rows)


# pull L station locations from the Chicago Data Portal (still using Socrata for this one)
print("Fetching L station locations...")
l_stations = fetch_static("8pix-ypme", token)
l_stations.to_csv(os.path.join(raw_dir, "l_station_locations.csv"), index=False)
print("L station locations saved.")


import zipfile
import io

def fetch_gtfs(save_dir):
    """
    Downloads the CTA's official GTFS feed and extracts the files needed
    to map bus stops to routes with lat/lon coordinates.

    The GTFS zip contains plain-text CSVs — stops.txt, routes.txt, trips.txt,
    and stop_times.txt together let us compute the geographic footprint of each route.

    Parameters
    ----------
    save_dir : str
        Directory to extract GTFS files into (data/raw/gtfs/)
    """
    gtfs_url = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"

    print("Downloading CTA GTFS feed...")
    response = requests.get(gtfs_url, timeout=60)
    response.raise_for_status()

    # files we actually need — skip the rest to keep things lean
    files_to_extract = {"stops.txt", "routes.txt", "trips.txt", "stop_times.txt"}

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        available = set(z.namelist())
        for filename in files_to_extract:
            if filename in available:
                z.extract(filename, save_dir)
                print(f"  extracted {filename}")
            else:
                print(f"  warning: {filename} not found in zip")


gtfs_dir = os.path.join(raw_dir, "gtfs")
os.makedirs(gtfs_dir, exist_ok=True)
fetch_gtfs(gtfs_dir)

print("All reference data saved to data/raw/")
