# CTA Route Utilization Analysis
Identifies the most underutilized Chicago Transit Authority bus routes and rail stations by comparing pre-COVID (2018–2019) and post-COVID (2022–2024) ridership data using a composite scoring model.

## Results
- [Policy Brief](https://portfolio-ebon-mu-75.vercel.app/docs/policy_brief.html): findings and recommendations written for a CTA planning audience (source in `docs/`)
- [Interactive Dashboard on Tableau Public](https://public.tableau.com/app/profile/matt.steines/viz/CTABusRouteUnderutilizationAnalysis/Dashboard1)

## Tech Stack
- Python 3
- pandas: data processing and aggregation
- matplotlib: visualizations
- requests, python-dotenv: API access via the Chicago Data Portal (Socrata SODA API)
- Tableau Public: interactive dashboard

## Data
Two datasets from the [Chicago Data Portal](https://data.cityofchicago.org/), pulled for 2018–2019 and 2022–2024:
- CTA Ridership: Bus Routes, Daily Totals by Route (`jyb9-n7fm`)
- CTA Ridership: 'L' Station Entries, Daily Totals (`5neh-572f`)

2020 and 2021 are left out on purpose. They capture the acute COVID collapse, not normal operations before or after it.

## How to Run

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Socrata API token:
   ```bash
   cp .env.example .env
   ```

3. Run each stage in order:
   ```bash
   python notebooks/01_ingest.py        # fetch raw data from the Chicago Data Portal into data/raw/
   python notebooks/02_clean.py         # parse types, tag pre/post periods, save to data/processed/
   python notebooks/03_eda.py           # generate 7 figures + 3 route/station summary CSVs
   python notebooks/04_model.py         # score and tier every route and station, plus 3 figures
   python notebooks/05_tableau_prep.py  # reshape data into Tableau-ready CSVs
   ```

4. Outputs land in:
   - `outputs/figures/`: 10 PNG charts
   - `outputs/exports/`: 5 CSVs, including the final ranked scores (`bus_route_scores.csv`, `rail_station_scores.csv`)
   - `outputs/exports/tableau/`: 2 CSVs used by the dashboard

## Key Features
- **Pre/post COVID comparison** across 128 bus routes and 143 rail stations using five years of daily ridership data
- **7 EDA analyses**: least-ridden bus routes and rail stations, absolute ridership drops, recovery rates, day-type breakdowns, a system-wide trend line, and a Pareto concentration chart
- **Composite underutilization score** (0–100) built from three min-max normalized signals: post-COVID ridership level (40%), recovery rate (40%), and absolute ridership drop (20%)
- **Relative risk tiers**: routes are split into equal thirds (High Risk, Moderate, Stable) by score, so tiers show how a route ranks against its peers
- **Tableau-ready exports** of route summaries and ranked scores for further visualization

## What I Learned
Working with a real municipal dataset surfaced tradeoffs that clean classroom data doesn't: large routes shed more riders in absolute terms but may recover better proportionally, so a single metric misleads. Building a weighted composite score required thinking carefully about what "underutilized" actually means and being explicit about those design choices in the code.
