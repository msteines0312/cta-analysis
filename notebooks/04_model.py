# Stage 4: Route Scoring Model
# Builds a composite underutilization score for each bus route and rail station.
# Reads from outputs/exports/ (produced by 03_eda.py) and writes ranked CSVs
# and summary figures back to outputs/.

import os
import pandas as pd
import matplotlib.pyplot as plt

# ── paths ─────────────────────────────────────────────────────────────────────
base_dir   = os.path.dirname(__file__)
export_dir = os.path.join(base_dir, "..", "outputs", "exports")
fig_dir    = os.path.join(base_dir, "..", "outputs", "figures")

# ── plot style (matches 03_eda.py) ────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi': 150,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.size': 10,
})


def score_routes(df):
    """
    Compute a composite underutilization score (0–100) for each route or station.

    Three signals are min-max normalized to [0, 1], then flipped so that
    1 = most underutilized. A weighted sum produces the final score.

    Weights:
      - post-COVID avg daily ridership : 40%  (low ridership = more underutilized)
      - recovery_pct (post as % of pre): 40%  (low recovery  = more underutilized)
      - absolute ridership drop        : 20%  (high drop      = more underutilized)

    The drop signal is down-weighted because large routes naturally shed more
    riders in absolute terms — raw volume alone shouldn't dominate the ranking.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: post, recovery_pct, drop.
    Returns
    -------
    pd.DataFrame
        Original df with a new 'score' column (0–100), sorted descending by score.
    """
    df = df.copy()

    def minmax(series):
        """Scale a series to [0, 1]."""
        lo, hi = series.min(), series.max()
        if hi == lo:
            return pd.Series(0.5, index=series.index)
        return (series - lo) / (hi - lo)

    # normalize each signal — flip post and recovery so high normalized value = bad
    norm_post     = 1 - minmax(df['post'])          # low ridership is worse
    norm_recovery = 1 - minmax(df['recovery_pct'])  # low recovery is worse
    norm_drop     = minmax(df['drop'])               # high drop is worse

    df['score'] = (
        0.40 * norm_post +
        0.40 * norm_recovery +
        0.20 * norm_drop
    ) * 100

    df['score'] = df['score'].round(1)

    df = df.sort_values('score', ascending=False).reset_index(drop=True)

    # assign tier based on score percentile within this dataset
    # top third = High Risk, middle = Moderate, bottom = Stable
    df['tier'] = pd.qcut(df['score'], q=3, labels=['Stable', 'Moderate', 'High Risk'])

    return df


# ── load EDA exports ──────────────────────────────────────────────────────────
print("Loading route summaries...")

bus  = pd.read_csv(os.path.join(export_dir, "bus_route_summary.csv"))
rail = pd.read_csv(os.path.join(export_dir, "rail_station_summary.csv"))

# ── score ─────────────────────────────────────────────────────────────────────
bus_scored  = score_routes(bus)
rail_scored = score_routes(rail)

# ── save ranked CSVs ──────────────────────────────────────────────────────────
bus_out  = os.path.join(export_dir, "bus_route_scores.csv")
rail_out = os.path.join(export_dir, "rail_station_scores.csv")

bus_scored.to_csv(bus_out,   index=False)
rail_scored.to_csv(rail_out, index=False)

print(f"Saved: {bus_out}")
print(f"Saved: {rail_out}")

# ── figure 1: score distribution (bus) ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(bus_scored['score'], bins=20, color='steelblue', edgecolor='white')
ax.set_xlabel("Underutilization Score")
ax.set_ylabel("Number of Routes")
ax.set_title("Distribution of Bus Route Underutilization Scores")
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "bus_score_distribution.png"), bbox_inches='tight')
plt.close()
print("Saved: bus_score_distribution.png")

# ── figure 2: top 20 most underutilized bus routes ────────────────────────────
top20_bus = bus_scored.head(20).sort_values('score')  # ascending for horizontal bar

fig, ax = plt.subplots(figsize=(8, 7))
bars = ax.barh(top20_bus['route'].astype(str), top20_bus['score'], color='steelblue')
ax.set_xlabel("Underutilization Score (0–100)")
ax.set_title("Top 20 Most Underutilized Bus Routes")
ax.set_xlim(0, 100)

# label each bar with the score
for bar, score in zip(bars, top20_bus['score']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{score:.0f}", va='center', fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "top20_underutilized_bus.png"), bbox_inches='tight')
plt.close()
print("Saved: top20_underutilized_bus.png")

# ── figure 3: top 20 most underutilized rail stations ────────────────────────
top20_rail = rail_scored.head(20).sort_values('score')

fig, ax = plt.subplots(figsize=(8, 7))
bars = ax.barh(top20_rail['stationname'], top20_rail['score'], color='firebrick')
ax.set_xlabel("Underutilization Score (0–100)")
ax.set_title("Top 20 Most Underutilized Rail Stations")
ax.set_xlim(0, 100)

for bar, score in zip(bars, top20_rail['score']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{score:.0f}", va='center', fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "top20_underutilized_rail.png"), bbox_inches='tight')
plt.close()
print("Saved: top20_underutilized_rail.png")

# ── console summary ───────────────────────────────────────────────────────────
print("\n--- Top 10 Most Underutilized Bus Routes ---")
print(bus_scored[['route', 'post', 'recovery_pct', 'score', 'tier']].head(10).to_string(index=False))

print("\n--- Top 10 Most Underutilized Rail Stations ---")
print(rail_scored[['stationname', 'post', 'recovery_pct', 'score', 'tier']].head(10).to_string(index=False))

print("\n--- Bus Tier Counts ---")
print(bus_scored['tier'].value_counts().sort_index().to_string())

print("\n--- Rail Tier Counts ---")
print(rail_scored['tier'].value_counts().sort_index().to_string())

print("\nDone.")
