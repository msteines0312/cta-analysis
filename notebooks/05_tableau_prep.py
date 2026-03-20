# Stage 5: Tableau Export Prep
# Reshapes and combines data into Tableau-ready CSVs saved to outputs/exports/tableau/
# Two outputs:
#   1. bus_ridership_combined.csv  — full time series (2018–2024) in one file for trend viz
#   2. bus_daytype_long.csv        — daytype breakdown reshaped from wide to long for bar chart

import os
import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
base_dir   = os.path.dirname(__file__)
processed  = os.path.join(base_dir, "..", "data", "processed")
export_dir = os.path.join(base_dir, "..", "outputs", "exports", "tableau")

os.makedirs(export_dir, exist_ok=True)

# ── 1. combined bus time series ───────────────────────────────────────────────
# Tableau can union CSVs manually, but a single pre-unioned file is simpler
# and avoids any schema mismatch issues in Public.

bus = pd.concat([
    pd.read_csv(os.path.join(processed, "bus_ridership_2018_2019_clean.csv")),
    pd.read_csv(os.path.join(processed, "bus_ridership_2022_2024_clean.csv")),
], ignore_index=True)

bus["date"] = pd.to_datetime(bus["date"])

# Aggregate to system-wide daily totals for the trend line viz.
# Tableau will also have the route-level rows available for drill-down.
bus_daily = (
    bus.groupby("date", as_index=False)["rides"]
    .sum()
    .rename(columns={"rides": "total_rides"})
)
bus_daily["period"] = bus_daily["date"].apply(
    lambda d: "pre" if d.year < 2020 else "post"
)

bus_daily.to_csv(os.path.join(export_dir, "bus_ridership_combined.csv"), index=False)
print(f"bus_ridership_combined.csv  — {len(bus_daily):,} rows")

# ── 2. daytype breakdown: wide → long ─────────────────────────────────────────
# Source file has one column per daytype (Weekday, Saturday, Sunday/Holiday).
# Tableau's calculated fields work better with a single 'daytype' dimension column.

daytype_wide = pd.read_csv(
    os.path.join(base_dir, "..", "outputs", "exports", "bus_daytype_breakdown.csv")
)

daytype_long = daytype_wide.melt(
    id_vars="route",
    value_vars=["Weekday", "Saturday", "Sunday/Holiday"],
    var_name="daytype",
    value_name="avg_daily_rides",
)

# Drop routes with zero ridership across all daytypes (routes with no post-period data)
routes_with_rides = daytype_long.groupby("route")["avg_daily_rides"].sum()
active_routes = routes_with_rides[routes_with_rides > 0].index
daytype_long = daytype_long[daytype_long["route"].isin(active_routes)]

daytype_long.to_csv(os.path.join(export_dir, "bus_daytype_long.csv"), index=False)
print(f"bus_daytype_long.csv        — {len(daytype_long):,} rows")

print("\nAll Tableau exports written to outputs/exports/tableau/")
