import pandas as pd
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

# --- QA (silver) component columns (placeholder: float64, Shock Flag: Boolean) ---
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

# Tests for QA Comp
qa_float = ["BaseLevel","TrendComponent","SeasonalityComponent","NoiseComponent","ShockComponent"]
print(df.dtypes.loc[qa_float + ["ShockFlag"]])

# All QA components are float64
assert all(str(df[c].dtype) == "Float64" for c in qa_float), "QA components must be float64"
# ShockFlag is pandas nullable boolean
assert str(df["ShockFlag"].dtype) == "boolean", "ShockFlag must be nullable boolean"
# All NA for now
na_counts = df[qa_float + ["ShockFlag"]].isna().sum()
print(na_counts.to_string())
assert (na_counts == len(df)).all(), "Placeholders should be NA initially"