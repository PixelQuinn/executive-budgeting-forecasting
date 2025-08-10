import pandas as pd

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
print(len(MONTHS))      # total number of months
print(MONTHS[:3])       # first 3 months
print(MONTHS[-3:])      # last 3 months
print(MONTHS.dtype)     # should be period[M]