import pandas as pd
import numpy as np
import itertools

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

OUTPUT_DIR = "../data" 
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

# Tests for seasonality
assert str(df["SeasonalityComponent"].dtype) == "Float64"
assert df["SeasonalityComponent"].isna().sum() == 0

m = df.groupby("Department")["SeasonalityComponent"].mean()
print(m.round(4))   # expect ~1.0000 for each dept

mm = df.groupby("Department")["SeasonalityComponent"].agg(["min","max"])
print(mm.round(4))  # expect min ≈ 1 - amp, max ≈ 1 + amp