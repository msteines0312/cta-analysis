# Stage 3: Exploratory Data Analysis
# Investigates ridership patterns, identifies underutilized routes,
# and generates figures saved to outputs/figures/

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── paths ────────────────────────────────────────────────────────────────────
base_dir     = os.path.dirname(__file__)
processed    = os.path.join(base_dir, "..", "data", "processed")
fig_dir      = os.path.join(base_dir, "..", "outputs", "figures")
export_dir   = os.path.join(base_dir, "..", "outputs", "exports")

# ── load data ────────────────────────────────────────────────────────────────
bus = pd.concat([
    pd.read_csv(os.path.join(processed, "bus_ridership_2018_2019_clean.csv")),
    pd.read_csv(os.path.join(processed, "bus_ridership_2022_2024_clean.csv")),
], ignore_index=True)

rail = pd.concat([
    pd.read_csv(os.path.join(processed, "rail_ridership_2018_2019_clean.csv")),
    pd.read_csv(os.path.join(processed, "rail_ridership_2022_2024_clean.csv")),
], ignore_index=True)

bus['date']  = pd.to_datetime(bus['date'])
rail['date'] = pd.to_datetime(rail['date'])

# consistent plot style across all figures
plt.rcParams.update({
    'figure.dpi': 150,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 10,
})

print("Data loaded.")
print(f"  Bus rows:  {len(bus):,}")
print(f"  Rail rows: {len(rail):,}")


# ── Q1: bottom 20 bus routes by avg daily ridership (post-COVID) ─────────────
# this is the most direct measure of underutilization right now
bus_post_avg = (
    bus[bus['period'] == 'post']
    .groupby('route')['rides']
    .mean()
    .sort_values()
    .head(20)
)

fig, ax = plt.subplots(figsize=(10, 7))
bus_post_avg.plot(kind='barh', ax=ax, color='steelblue')
ax.set_title("20 Least-Ridden Bus Routes (2022–2024 Avg Daily Boardings)", fontweight='bold')
ax.set_xlabel("Average Daily Boardings")
ax.set_ylabel("Route")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_bottom20_post.png"))
plt.close()
print("Saved: bus_bottom20_post.png")


# ── Q2: biggest absolute ridership drops (pre vs post, bus) ──────────────────
# routes that lost the most riders in raw numbers
bus_avg = (
    bus.groupby(['route', 'period'])['rides']
    .mean()
    .unstack('period')
)
bus_avg['drop'] = bus_avg['pre'] - bus_avg['post']
top_drops = bus_avg['drop'].sort_values(ascending=False).head(20)

fig, ax = plt.subplots(figsize=(10, 7))
top_drops.plot(kind='barh', ax=ax, color='tomato')
ax.set_title("20 Bus Routes with Largest Ridership Drop (Pre vs Post COVID)", fontweight='bold')
ax.set_xlabel("Avg Daily Ridership Lost")
ax.set_ylabel("Route")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_top20_drops.png"))
plt.close()
print("Saved: bus_top20_drops.png")


# ── Q3: recovery rate % by bus route ─────────────────────────────────────────
# % of pre-COVID ridership each route has gotten back — this separates
# "always small" routes from "used to matter, now doesn't"
bus_avg['recovery_pct'] = (bus_avg['post'] / bus_avg['pre'] * 100).round(1)
worst_recovery = bus_avg['recovery_pct'].dropna().sort_values().head(20)

fig, ax = plt.subplots(figsize=(10, 7))
worst_recovery.plot(kind='barh', ax=ax, color='darkorange')
ax.axvline(100, color='gray', linestyle='--', linewidth=1, label='Full recovery')
ax.set_title("20 Bus Routes with Lowest COVID Recovery Rate", fontweight='bold')
ax.set_xlabel("Post-COVID Ridership as % of Pre-COVID")
ax.set_ylabel("Route")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_worst_recovery.png"))
plt.close()
print("Saved: bus_worst_recovery.png")


# ── Q4: bottom 20 rail stations by avg daily ridership (post-COVID) ───────────
rail_post_avg = (
    rail[rail['period'] == 'post']
    .groupby('stationname')['rides']
    .mean()
    .sort_values()
    .head(20)
)

fig, ax = plt.subplots(figsize=(10, 7))
rail_post_avg.plot(kind='barh', ax=ax, color='mediumpurple')
ax.set_title("20 Least-Ridden L Stations (2022–2024 Avg Daily Boardings)", fontweight='bold')
ax.set_xlabel("Average Daily Boardings")
ax.set_ylabel("Station")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "rail_bottom20_post.png"))
plt.close()
print("Saved: rail_bottom20_post.png")


# ── Q5: ridership by day type (bus, post-COVID) ───────────────────────────────
# some routes may be weekday-only in practice even if scheduled 7 days —
# useful for targeted service reduction recommendations
daytype_avg = (
    bus[bus['period'] == 'post']
    .groupby(['route', 'daytype'])['rides']
    .mean()
    .unstack('daytype')
    .rename(columns={'W': 'Weekday', 'A': 'Saturday', 'U': 'Sunday/Holiday'})
    .fillna(0)
)
# just show the bottom 30 routes by total ridership to keep the chart readable
low_ridership_routes = bus_post_avg.index.tolist()
daytype_subset = daytype_avg.loc[daytype_avg.index.isin(low_ridership_routes)]

fig, ax = plt.subplots(figsize=(10, 7))
daytype_subset.plot(kind='barh', stacked=True, ax=ax,
                    color=['steelblue', 'coral', 'mediumseagreen'])
ax.set_title("Day Type Breakdown — Least-Ridden Bus Routes (Post-COVID)", fontweight='bold')
ax.set_xlabel("Average Daily Boardings")
ax.set_ylabel("Route")
ax.legend(title="Day Type", bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_daytype_breakdown.png"))
plt.close()
print("Saved: bus_daytype_breakdown.png")


# ── Q6: system-wide ridership trend over time (monthly, bus) ──────────────────
# big-picture context for the brief — shows the COVID dip and partial recovery arc
bus['month'] = bus['date'].dt.to_period('M')
monthly = bus.groupby('month')['rides'].sum().reset_index()
monthly['month_dt'] = monthly['month'].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly['month_dt'], monthly['rides'], color='steelblue', linewidth=1.5)
ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-12-31'),
           alpha=0.15, color='red', label='COVID period (excluded from analysis)')
ax.set_title("CTA Bus System Monthly Ridership (2018–2024)", fontweight='bold')
ax.set_ylabel("Total Monthly Boardings")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_system_trend.png"))
plt.close()
print("Saved: bus_system_trend.png")


# ── Q7: ridership concentration (Pareto) ─────────────────────────────────────
# what share of total ridership do the top routes carry?
# if a small number of routes dominate, that shapes where resources should go
post_totals = (
    bus[bus['period'] == 'post']
    .groupby('route')['rides']
    .sum()
    .sort_values(ascending=False)
)
cumulative_share = (post_totals.cumsum() / post_totals.sum() * 100)
x = range(1, len(cumulative_share) + 1)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(list(x), cumulative_share.values, color='steelblue', linewidth=2)
ax.axhline(80, color='gray', linestyle='--', linewidth=1, label='80% of ridership')
ax.set_title("Ridership Concentration — Bus Routes (Post-COVID)", fontweight='bold')
ax.set_xlabel("Number of Routes (ranked by ridership)")
ax.set_ylabel("Cumulative % of Total Ridership")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_pareto.png"))
plt.close()
print("Saved: bus_pareto.png")


# ── exports for Tableau ───────────────────────────────────────────────────────
# route-level bus summary
bus_export = bus_avg.copy()
bus_export.columns.name = None
bus_export = bus_export.reset_index()
bus_export.to_csv(os.path.join(export_dir, "bus_route_summary.csv"), index=False)

# station-level rail summary
rail_avg = (
    rail.groupby(['stationname', 'period'])['rides']
    .mean()
    .unstack('period')
)
rail_avg['drop']         = rail_avg['pre'] - rail_avg['post']
rail_avg['recovery_pct'] = (rail_avg['post'] / rail_avg['pre'] * 100).round(1)
rail_avg.columns.name    = None
rail_avg                 = rail_avg.reset_index()
rail_avg.to_csv(os.path.join(export_dir, "rail_station_summary.csv"), index=False)

# day type breakdown for Tableau
daytype_avg.reset_index().to_csv(os.path.join(export_dir, "bus_daytype_breakdown.csv"), index=False)

print("\nAll exports saved to outputs/exports/")
print("EDA complete.")
