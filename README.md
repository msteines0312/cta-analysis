# CTA Route Utilization Analysis
Identifies the most underutilized Chicago Transit Authority bus routes and rail stations by comparing pre-COVID (2018–2019) and post-COVID (2022–2024) ridership data using a composite scoring model.

## Tech Stack
- Python 3
- pandas, numpy — data processing and aggregation
- matplotlib — visualizations
- requests, python-dotenv — API access via Chicago Data Portal (Socrata SODA API)

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
   python notebooks/01_ingest.py   # fetch raw data from Chicago Data Portal
   python notebooks/02_clean.py    # parse types, tag pre/post periods, save to data/processed/
   python notebooks/03_eda.py      # generate 7 figures + 3 Tableau-ready exports
   python notebooks/04_model.py    # build composite underutilization scores, rank routes
   ```

4. Outputs land in:
   - `outputs/figures/` — 10 PNG charts
   - `outputs/exports/` — 5 CSV exports (including final ranked scores)

## Key Features
- **Pre/post COVID comparison** across ~130 bus routes and ~150 rail stations using 6 years of daily ridership data
- **7 EDA analyses**: bottom 20 routes by ridership, absolute ridership drops, recovery rates, day-type breakdowns, system-wide trend line, and Pareto concentration chart
- **Composite underutilization score** (0–100) built from three normalized signals: post-COVID ridership level (40%), recovery rate (40%), and absolute ridership drop (20%)
- **Tableau-ready exports** of route summaries and ranked scores for further visualization

## What I Learned
Working with a real municipal dataset surfaced tradeoffs that clean classroom data doesn't: large routes shed more riders in absolute terms but may recover better proportionally, so a single metric misleads. Building a weighted composite score required thinking carefully about what "underutilized" actually means and being explicit about those design choices in the code.
