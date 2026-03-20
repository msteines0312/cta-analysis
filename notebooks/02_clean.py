# step 2: Data Cleaning
# loads raw data from data/raw/, handles missing values, standardizes types,and writes clean output to data/processed/

#imports
import os
import pandas as pd
import numpy as np

def clean_data(input_path, output_path, period):
    """
    Loads raw data, performs cleaning steps, and saves cleaned data.

    Parameters
    ----------
    input_path : str
        Path to the raw data CSV file
    output_path : str
        Path where the cleaned CSV file should be saved
    period : str
        Label for which time window this data belongs to — 'pre' or 'post'
    """
    # load raw data
    df = pd.read_csv(input_path)

    # convert date column to datetime, coerce errors to NaT
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # fill missing rides with 0 — treating missing as unreported rather than zero is a judgment call,
    # but there are very few nulls here and 0 is conservative for an underutilization analysis
    df['rides'] = df['rides'].fillna(0)

    # ensure 'rides' is an integer type
    df['rides'] = df['rides'].astype(int)

    # station_id only exists in the rail dataset — cast it if it's there
    if 'station_id' in df.columns:
        df['station_id'] = df['station_id'].astype(int)

    # tag each row so we can split pre/post in EDA without needing separate dataframes
    df['period'] = period

    # save cleaned data
    df.to_csv(output_path, index=False)


# build paths relative to this script so it works from any working directory
raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
processed_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

print("Cleaning bus pre-COVID...")
clean_data(
    os.path.join(raw_dir, "bus_ridership_2018_2019.csv"),
    os.path.join(processed_dir, "bus_ridership_2018_2019_clean.csv"),
    period="pre"
)

print("Cleaning bus post-COVID...")
clean_data(
    os.path.join(raw_dir, "bus_ridership_2022_2024.csv"),
    os.path.join(processed_dir, "bus_ridership_2022_2024_clean.csv"),
    period="post"
)

print("Cleaning rail pre-COVID...")
clean_data(
    os.path.join(raw_dir, "rail_ridership_2018_2019.csv"),
    os.path.join(processed_dir, "rail_ridership_2018_2019_clean.csv"),
    period="pre"
)

print("Cleaning rail post-COVID...")
clean_data(
    os.path.join(raw_dir, "rail_ridership_2022_2024.csv"),
    os.path.join(processed_dir, "rail_ridership_2022_2024_clean.csv"),
    period="post"
)

print("Done. All cleaned files saved to data/processed/")
