# analyze.py
# Breakdown-risk analysis for Vossberg Mobility fleet (fleet_history.csv, 120 cars).
#
# KEY FINDING:
#   km_since_service is the strongest single predictor of breakdown (correlation 0.40).
#   load_factor and avg_daily_km add meaningful signal on top of it.
#   odometer_km (total mileage) and age_years show virtually zero gap between groups —
#   the data does NOT support the "older or higher-mileage cars break more" assumption.
#   Risk is about HOW a car is being used right now, not how old it is.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --------------------------------------------------------------------------
# Step 1 – Compare the two outcome groups column by column
# --------------------------------------------------------------------------
broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

feature_cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print("=" * 65)
print("GROUP COMPARISON  (broke down vs did not)")
print("=" * 65)
print(f"{'Column':<22} {'Broke median':>14} {'OK median':>12} {'Gap':>10}")
print("-" * 65)
for col in feature_cols:
    bm  = broke[col].median()
    om  = ok[col].median()
    gap = bm - om
    print(f"  {col:<20} {bm:>14.2f} {om:>12.2f} {gap:>+10.2f}")

print()
print("Pearson correlation with broke_down:")
corr = df[feature_cols + ["broke_down"]].corr()["broke_down"].drop("broke_down")
for col, r in corr.sort_values(key=abs, ascending=False).items():
    bar = "#" * int(abs(r) * 30)
    print(f"  {col:<22}  r={r:+.3f}  {bar}")

# --------------------------------------------------------------------------
# Step 2 – Build a 0-100 risk score from the three columns that DO separate
#
#   The three columns that matter:
#     km_since_service  (r=+0.40) — how close to the service window ceiling
#     avg_daily_km      (r=+0.25) — how hard the car is driven daily
#     load_factor       (r=+0.22) — how heavily loaded it runs
#
#   Columns that do NOT matter (gap ≈ 0):
#     odometer_km  (r=+0.002)  — total mileage tells us almost nothing
#     age_years    (r=-0.001)  — age tells us almost nothing
#
#   Each column is min-max scaled to [0, 1], then combined with weights that
#   mirror their correlations: 50% km_since_service, 30% avg_daily_km,
#   20% load_factor.  Multiply by 100 → integer score 0-100.
# --------------------------------------------------------------------------

WEIGHTS = {
    "km_since_service": 0.50,
    "avg_daily_km":     0.30,
    "load_factor":      0.20,
}


def minmax(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo) if hi > lo else series * 0


df["risk_score"] = sum(
    df[col].pipe(minmax) * weight
    for col, weight in WEIGHTS.items()
) * 100

df["risk_score"] = df["risk_score"].round(1)

# --------------------------------------------------------------------------
# Step 3 – Print cars ranked by risk, highest first
# --------------------------------------------------------------------------
ranked = df.sort_values("risk_score", ascending=False).reset_index(drop=True)

print()
print("=" * 65)
print("FLEET RISK RANKING  (highest risk first)")
print("=" * 65)
print(f"{'#':<4} {'car_id':<12} {'score':>6}  {'km_since':>9}  "
      f"{'daily_km':>9}  {'load':>6}  {'broke?':>7}")
print("-" * 65)
for i, row in ranked.iterrows():
    flag = "  YES" if row["broke_down"] == 1 else ""
    print(
        f"  {i+1:<3} {row['car_id']:<12} {row['risk_score']:>6.1f}"
        f"  {row['km_since_service']:>9.0f}"
        f"  {row['avg_daily_km']:>9.0f}"
        f"  {row['load_factor']:>6.2f}"
        f"{flag}"
    )

# --------------------------------------------------------------------------
# Step 4 – Quick sanity check: do the known breakdowns cluster near the top?
# --------------------------------------------------------------------------
top_25_pct = ranked.head(30)
breakdowns_in_top_30 = top_25_pct["broke_down"].sum()
total_breakdowns = df["broke_down"].sum()

print()
print("=" * 65)
print("SANITY CHECK")
print("=" * 65)
print(f"  Total breakdowns in dataset      : {int(total_breakdowns)}")
print(f"  Breakdowns in top 30 by risk     : {int(breakdowns_in_top_30)}"
      f"  ({breakdowns_in_top_30/total_breakdowns*100:.0f}% of all breakdowns)")
print(f"  Expected if score were random    : ~{total_breakdowns * 30 / len(df):.1f}")
print()
print("  A score that clusters known breakdowns near the top")
print("  is catching real signal, not just noise.")
