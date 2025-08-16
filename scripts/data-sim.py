import pandas as pd
import numpy as np
import itertools
import os

# -----------------------------------------
# Executive Budgeting + Forecasting Project
# Step 1: Config and monthly index setup
# This script builds the skeleton for synthetic finance data simulation.
# -----------------------------------------

# --- Configuration ---
SEED = 42 # Random number generator seed to reproduce the data.
START_MONTH = "2018-01" # First month in simmed data
END_MONTH = "2024-12" # Last month in simmed data

# Departments to simulate for data
DEPARTMENTS = ["Finance", "HR", "Sales", "Operations", "Marketing"]

OUTPUT_DIR = "./data" 
KEEP_QA_COMPONENTS = True # Change to keep intermediate QA columns(True) or not(False) for debugging

# --- Index ---
MONTHS = pd.period_range(start = START_MONTH, end = END_MONTH, freq = "M")

# Test for period_range
# print(len(MONTHS))      # total number of months
# print(MONTHS[:3])       # first 3 months
# print(MONTHS[-3:])      # last 3 months
# print(MONTHS.dtype)     # should be period[M]S

# --- Skeleton of rows ---
pairs = itertools.product(DEPARTMENTS, MONTHS) # Cartesian join to give all the months to each department
df = pd.DataFrame(pairs, columns=["Department", "Month"]) # Move the new columns to a df

df["Department"] = df["Department"].astype("category")
df["Month"] = df["Month"].astype("period[M]")

# Test for column skeleton
# Quick counts for sanity check
# print("months:", len(MONTHS), "depts:", len(DEPARTMENTS), "rows:", df.shape[0])
# print(df.head())

# Unique and row checks
# assert df.shape[0] == len(DEPARTMENTS) * len(MONTHS), "Row count != departments × months"
# g = df.groupby("Department")["Month"].nunique()
# print(g.to_string())  # peek counts per dept
# assert (g == len(MONTHS)).all(), "Some departments are missing months"

# --- QA (silver) component columns (placeholder: Float64(nullable), Shock Flag: Boolean) ---
df["BaseLevel"] = pd.NA
df["BaseLevel"] = df["BaseLevel"].astype("Float64")

df["TrendComponent"] = pd.NA
df["TrendComponent"] = df["TrendComponent"].astype("Float64")

df["SeasonalityComponent"] = pd.NA
df["SeasonalityComponent"] = df["SeasonalityComponent"].astype("Float64")

df["NoiseComponent"] = pd.NA
df["NoiseComponent"] = df["NoiseComponent"].astype("Float64")

df["ShockComponent"] = pd.NA
df["ShockComponent"] = df["ShockComponent"].astype("Float64")

df["ShockFlag"] = pd.NA
df["ShockFlag"] = df["ShockFlag"].astype("boolean") # Nullable bool

# # Tests for QA Comp
# qa_float = ["BaseLevel","TrendComponent","SeasonalityComponent","NoiseComponent","ShockComponent"]
# print(df.dtypes.loc[qa_float + ["ShockFlag"]])

# # All QA components are float64
# assert all(str(df[c].dtype) == "Float64" for c in qa_float), "QA components must be float64"
# # ShockFlag is pandas nullable boolean
# assert str(df["ShockFlag"].dtype) == "boolean", "ShockFlag must be nullable boolean"
# # All NA for now
# na_counts = df[qa_float + ["ShockFlag"]].isna().sum()
# print(na_counts.to_string())
# assert (na_counts == len(df)).all(), "Placeholders should be NA initially"

# --- Final(Gold) Measure Column (Float64 placeholder) ---
df["Actual"] = pd.NA
df["Actual"] = df["Actual"].astype("Float64")

df["Budget"] = pd.NA
df["Budget"] = df["Budget"].astype("Float64")

df["Forecast"] = pd.NA
df["Forecast"] = df["Forecast"].astype("Float64")

df["Variance"] = pd.NA
df["Variance"] = df["Variance"].astype("Float64")

df["PctVariance"] = pd.NA
df["PctVariance"] = df["PctVariance"].astype("Float64")

# # Column tests for Gold columns
# # 1) Columns present
# expected = {"Actual","Budget","Forecast","Variance","PctVariance"}
# assert expected.issubset(df.columns), "Missing one or more final measure columns"

# # 2) Dtypes are nullable Float64
# print(df[list(expected)].dtypes.to_string())
# assert all(str(t) == "Float64" for t in df[list(expected)].dtypes), "Final measures must be Float64"

# # 3) Currently all NA
# na_counts = df[list(expected)].isna().sum()
# print(na_counts.to_string())
# assert (na_counts == len(df)).all(), "Final measures should be NA initially"

# --- Adding Baseline Data ---
rng = np.random.default_rng(SEED) # Initialize a reproducible NumPy Generator

# Per department, monthly, base-level ranges per month, lo/hi are fixed bounds per department.
BASE_RANGES = {"Sales": (400_000, 700_000), 
               "Operations": (250_000, 450_000), 
               "Marketing": (120_000, 250_000), 
               "HR": (80_000, 150_000), 
               "Finance": (60_000, 120_000)} 

# Draws one base level per department within the lo/hi range. 
# Rng seeded for reproducibility
BASE_VALUES = {
    dept: rng.uniform(lo, hi)
    for dept, (lo, hi) in BASE_RANGES.items()
}

# Map per department base level ranges (lo, hi)
df["BaseLevel"] = df["Department"].map(BASE_VALUES).astype("Float64")

# ---Simming realistic trends ---
# Trend component to sim real life trends
TREND_RANGES = {"Sales": (0.002, 0.008),
               "Operations": (0.001, 0.005),
               "Marketing": (0.001, 0.006),
               "HR": (-0.001, 0.003),
               "Finance": (-0.001, 0.003)
}

# Per department monthly growth rates drawn with rng(reproducible)
GROWTH_RATES = {
    dept: rng.uniform(lo, hi)
    for dept, (lo, hi) in TREND_RANGES.items()
}

# Build a position map once, then map Period -> 0..N-1
pos = {p: i for i, p in enumerate(MONTHS)}
df["MonthIndex"] = df["Month"].map(pos).astype("Int64")

# Map per department growth rates, staying within our trend ranges
df["DeptGrowth"] = df["Department"].map(GROWTH_RATES).astype("Float64")

# Trend = BaseLevel * ((1 + growth)^t-1), keep Float64 nullable
df["TrendComponent"] = (
    df["BaseLevel"] * (((1 + df["DeptGrowth"]) ** df["MonthIndex"]) - 1)
).astype("Float64")

# # Test for growth trends
# # t=0 → trend must be 0
# assert (df.loc[df["MonthIndex"] == 0, "TrendComponent"].fillna(0) == 0).all()

# # dtype sanity
# assert str(df["TrendComponent"].dtype) == "Float64"

# # quick first/last view
# print(
#     df.sort_values(["Department","MonthIndex"])
#       .groupby("Department")["TrendComponent"]
#       .agg(["first","last"])
#       .round(2)
# )

# --- Setting Seasonality ---
# Setting the month
df["MonthNum"] = df["Month"].dt.month.astype("Int64")

# Defining boundaries for department amplitude (lo, hi)
SEASON_AMP_RANGES = {"Sales": (0.08, 0.12),
                     "Operations": (0.05, 0.08),
                     "Marketing": (0.06, 0.10),
                     "HR": (0.02, 0.04),
                     "Finance": (0.02, 0.04)
}

SEASON_AMPLITUDES = {
    dept: rng.uniform(lo, hi)
    for dept, (lo, hi) in SEASON_AMP_RANGES.items()
}

# Involve random phase shift to make it realistic
SEASON_PHASES = { dept: rng.uniform(0, 2*np.pi) for dept in DEPARTMENTS}
df["SeasonPhase"] = df["Department"].map(SEASON_PHASES).astype("Float64")

# Map per department season amp ranges (lo, hi)
df["SeasonAmp"] = df["Department"].map(SEASON_AMPLITUDES).astype("Float64")

# Build the multiplicative factor around 1.0 for sin
angle = 2 * np.pi * (df["MonthNum"] - 1) / 12
df["SeasonalityComponent"] = (
    1 + df["SeasonAmp"] * np.sin(angle + df["SeasonPhase"])
).astype("Float64")

# # Tests for seasonality
# assert str(df["SeasonalityComponent"].dtype) == "Float64"
# assert df["SeasonalityComponent"].isna().sum() == 0

# m = df.groupby("Department")["SeasonalityComponent"].mean()
# print(m.round(4))   # expect ~1.0000 for each dept

# mm = df.groupby("Department")["SeasonalityComponent"].agg(["min","max"])
# print(mm.round(4))  # expect min ≈ 1 - amp, max ≈ 1 + amp


# --- Formulas for Measures ---
# Put it together to calculate budget
df["Budget"] =(
     (df["BaseLevel"] + df["TrendComponent"]) * df["SeasonalityComponent"]
).astype("Float64")

# # Sanity tests for budget
# # 1) Basic integrity
# assert df["Budget"].notna().all()
# assert str(df["Budget"].dtype) == "Float64"
# assert (df["Budget"] > 0).all()

# # 2) YoY growth ≈ annualized DeptGrowth (allow wobble from seasonality)
# tmp = df.assign(Year=df["Month"].dt.year)
# yoy = tmp.groupby(["Department","Year"], observed=False)["Budget"].mean().unstack().pct_change(axis=1)

# expected_yoy = pd.Series({d: (1 + g)**12 - 1 for d, g in GROWTH_RATES.items()}, name="expected")
# check = yoy.mean(axis=1).to_frame("yoy_avg").join(expected_yoy)
# print(check.round(3))

# Simulation for department noise
NOISE_SIGMA = {"Sales": 0.08,
               "Operations": 0.06,
               "Marketing": 0.09,
               "HR": 0.04,
               "Finance": 0.03
}

df["NoiseSigma"] = df["Department"].map(NOISE_SIGMA).astype("Float64")

# Normal scaled by Budget
df["NoiseComponent"] = (rng.normal(0, 1, size=len(df)) * df["NoiseSigma"] * df["Budget"]).astype("Float64")

# Rare shocks, Sales/Marketing mostly positive(think promos and launches), Ops/HR/Finance mostly negative(Unplanned costs)
# Probability for a shock
P_SHOCK = {"Sales": 0.06,
            "Operations": 0.05,
            "Marketing": 0.06,
            "HR": 0.04,
            "Finance": 0.04
}

# Shock locations, signs added for clarity on directional bias
SHOCK_LOC = {"Sales": +0.03,
             "Marketing": +0.035,
             "Operations": -0.02,
             "HR": -0.015,
             "Finance": -0.01
}

# Shock scale to set heaviness of tails
SHOCK_SCALE = {"Sales": 0.06,
               "Marketing": 0.07,
               "Operations": 0.05,
               "HR": 0.04,
               "Finance": 0.03
}

# Map our params to departments
P = df["Department"].map(P_SHOCK).astype("Float64")
ShockLocation = df["Department"].map(SHOCK_LOC).astype("Float64")
ShockScale = df["Department"].map(SHOCK_SCALE).astype("Float64")

# Bernoullli draw for flags
df["ShockFlag"] = (rng.random(len(df)) < P).astype("boolean")

# Laplace-heavy tail draw, then scale/bias by Budget
lap = rng.laplace(0.0, 1.0, size=len(df))
shock_raw = (ShockLocation * df["Budget"]) + (lap * ShockScale * df["Budget"])
df["ShockComponent"] = np.where(df["ShockFlag"], shock_raw, 0.0)
df["ShockComponent"] = df["ShockComponent"].astype("Float64")

# Formula for Actuals
df["Actual"] = (df["Budget"] + df["NoiseComponent"] + df["ShockComponent"]).clip(lower=0).astype("Float64")

# Baseline forecast to start
# Sort by department then month
df = df.sort_values(["Department", "Month"])

df["Forecast"] = (
    df.groupby("Department", observed=False)["Actual"]
    .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    .astype("Float64")
)

# Calculation for variance & percent variance
df["Variance"]    = (df["Actual"] - df["Budget"]).astype("Float64")
df["PctVariance"] = (df["Variance"] / df["Budget"]).astype("Float64")

# Checking Quarter and Yearly periods
df["Year"]          = df["Month"].dt.year
df["Quarter"]       = df["Month"].dt.quarter
df["QuarterPeriod"] = df["Month"].dt.to_timestamp().dt.to_period("Q")
df["YearlyPeriod"]  = df["Month"].dt.to_timestamp().dt.to_period("Y")

# Aggregate for quarter
quarterly_totals = (
    df.groupby(["Department", "QuarterPeriod"], observed=False)
    .agg(
        QuarterBudget   = ("Budget", "sum"),
        QuarterActual   = ("Actual", "sum"),
        QuarterForecast = ("Forecast", "sum"),
        ShockCount      = ("ShockFlag", "sum"),
        Months          = ("Month", "size")
    )
    .reset_index()
)

# Recalc for quarters
quarterly_totals["QuarterVariance"]    = (quarterly_totals["QuarterActual"] - quarterly_totals["QuarterBudget"]).astype("Float64")
quarterly_totals["QuarterPctVariance"] = (quarterly_totals["QuarterVariance"] / quarterly_totals["QuarterBudget"]).astype("Float64")
quarterly_totals["ShockRate"]          = (quarterly_totals["ShockCount"] / quarterly_totals["Months"]).astype("Float64")

# Yearly Calcs
# Aggregate for year
yearly_totals = (
    df.groupby(["Department", "YearlyPeriod"], observed=False)
    .agg(
        YearlyBudget   = ("Budget", "sum"),
        YearlyActual   = ("Actual", "sum"),
        YearlyForecast = ("Forecast", "sum"),
        ShockCount     = ("ShockFlag", "sum"),
        MonthsInYear   = ("Year", "size")
    )
    .reset_index()
)

# Calculations for yearly measures
yearly_totals["YearlyVariance"]    = (yearly_totals["YearlyActual"] - yearly_totals["YearlyBudget"]).astype("Float64")
yearly_totals["YearlyPctVariance"] = (yearly_totals["YearlyVariance"] / yearly_totals["YearlyBudget"]).astype("Float64")
yearly_totals["ShockRate"]         = (yearly_totals["ShockCount"] /  yearly_totals["MonthsInYear"]).astype("Float64")

# Ensure the order
df = df.sort_values(["Department", "Year", "Month"])

# YTD calculations
df["YTD_Budget"]      = df.groupby(["Department", "Year"], observed=False)["Budget"].cumsum().astype("Float64")
df["YTD_Actual"]      = df.groupby(["Department", "Year"], observed=False)["Actual"].cumsum().astype("Float64")
df["YTD_Variance"]    = (df["YTD_Actual"] - df["YTD_Budget"]).astype("Float64")
df["YTD_PctVariance"] = (df["YTD_Variance"] / df["YTD_Budget"]).astype("Float64")

# --- Organize Columns ---
core = ["Department", "Month", "Budget", "Actual", "Forecast", "Variance", "PctVariance", "ShockFlag",
        "Year", "Quarter", "QuarterPeriod", "YearlyPeriod", "YTD_Budget", "YTD_Actual", "YTD_Variance",
        "YTD_PctVariance"]

qa = ["BaseLevel", "DeptGrowth", "TrendComponent", "SeasonAmp", "SeasonPhase", "NoiseSigma", "NoiseComponent", "ShockComponent"]

df = df.loc[:, core + (qa if KEEP_QA_COMPONENTS else [])]
# --- Export Simmed Data as .csv ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Monthly
df_out = df.copy()

# === ROUNDING (export formatting only) ===
money_cols_monthly = ["Budget","Actual","Forecast","Variance","YTD_Budget","YTD_Actual","YTD_Variance"]
pct_cols_monthly   = ["PctVariance","YTD_PctVariance"]
df_out[money_cols_monthly] = df_out[money_cols_monthly].round(2)
df_out[pct_cols_monthly]   = df_out[pct_cols_monthly].round(2)
# ========================================

df_out["MonthTS"] = df_out["Month"].dt.to_timestamp("M")
df_out["QuarterPeriod"] = df_out["QuarterPeriod"].astype(str)
df_out["YearlyPeriod"]  = df_out["YearlyPeriod"].astype(str)
df_out.to_csv(os.path.join(OUTPUT_DIR, "monthly_sim.csv"), index=False)
df_out.drop(columns=["Month"]).to_parquet(os.path.join(OUTPUT_DIR, "monthly_sim.parquet"), index=False)

# Quarterly
qt = quarterly_totals.copy()

# === ROUNDING (quarterly) ===
money_cols_qt = ["QuarterBudget","QuarterActual","QuarterForecast","QuarterVariance"]
pct_cols_qt   = ["QuarterPctVariance"]
qt[money_cols_qt] = qt[money_cols_qt].round(2)
qt[pct_cols_qt]   = qt[pct_cols_qt].round(2)
# ============================

qt["QuarterPeriod"] = qt["QuarterPeriod"].astype(str)
qt.to_csv(os.path.join(OUTPUT_DIR, "quarterly_sim.csv"), index=False)
qt.to_parquet(os.path.join(OUTPUT_DIR, "quarterly_sim.parquet"), index=False)

# Yearly
yt = yearly_totals.copy()

# === ROUNDING (yearly) ===
money_cols_yr = ["YearlyBudget","YearlyActual","YearlyForecast","YearlyVariance"]
pct_cols_yr   = ["YearlyPctVariance"]
yt[money_cols_yr] = yt[money_cols_yr].round(2)
yt[pct_cols_yr]   = yt[pct_cols_yr].round(2)
# =========================

yt["YearlyPeriod"] = yt["YearlyPeriod"].astype(str)
yt.to_csv(os.path.join(OUTPUT_DIR, "yearly_sim.csv"), index=False)
yt.to_parquet(os.path.join(OUTPUT_DIR, "yearly_sim.parquet"), index=False)