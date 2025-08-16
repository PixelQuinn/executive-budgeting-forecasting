# EXECUTIVE-BUDGETING-FORECASTING
Simulated executive budgeting & forecasting suite with variance analysis, scenario modeling, and executive-ready dashboards for FP&A use cases.

-------------------------------------------------------------------------------
1) WHAT THIS REPO DOES
-------------------------------------------------------------------------------
Generates a realistic synthetic dataset (2018–2024) at monthly granularity for
five departments (Finance, HR, Sales, Operations, Marketing), plus quarterly,
yearly, and YTD rollups. Data is designed to power variance analysis, baseline
forecasting, and future scenario testing.

Signals modeled
- Baseline level by department
- Trend (dept-specific monthly growth)
- Seasonality (sinusoid with per-dept amplitude + phase)
- Noise (Gaussian, dept-specific sigma)
- Shocks (Laplace heavy-tail; Sales/Marketing mostly ↑, Ops/HR/Finance mostly ↓)
- Baseline forecast = 3-month rolling mean (per department)

-------------------------------------------------------------------------------
2) WHO IT’S FOR (PERSONAS)
-------------------------------------------------------------------------------
- CFO / Executives — want clear “Actual vs Budget vs Forecast” with drivers/risks.
- FP&A Analyst     — needs consistent data, auditability, and fast scenarios.
- Department Heads — need to understand variance and update forecast inputs.

-------------------------------------------------------------------------------
3) GOALS & SUCCESS METRICS
-------------------------------------------------------------------------------
- Transparent variance tracking across time & departments
- Fast scenario iteration to answer “what if?” questions
- Executive summaries that reduce time-to-decision

KPIs (for dashboards/notebooks):
- Burn Rate, Forecast Accuracy, Monthly Variance, Runway Estimation,
  Budget Utilization

-------------------------------------------------------------------------------
4) REPO QUICKSTART
-------------------------------------------------------------------------------
(From repo root)

    python3 -m venv .venv
    source .venv/bin/activate
    pip install pandas numpy

Optional for Parquet:

    pip install pyarrow     # or: pip install fastparquet

Run the simulator:

    python scripts/data-sim.py

Outputs land in data/:
- monthly_sim.csv   (+ monthly_sim.parquet)
- quarterly_sim.csv (+ quarterly_sim.parquet)
- yearly_sim.csv    (+ yearly_sim.parquet)

Note: Parquet requires pyarrow or fastparquet. CSVs are always written.

-------------------------------------------------------------------------------
5) HOW THE NUMBERS ARE BUILT
-------------------------------------------------------------------------------
Formulas (conceptual):

    TrendComponent = BaseLevel * ( (1 + DeptGrowth)^t - 1 )
    SeasonalityComponent = 1 + SeasonAmp * sin(2π*(month-1)/12 + SeasonPhase)

    Budget  = (BaseLevel + TrendComponent) * SeasonalityComponent
    Actual  = clip( Budget + NoiseComponent + ShockComponent, lower=0 )
    Forecast (baseline) = dept-wise 3M rolling mean of Actual

    Variance    = Actual - Budget
    PctVariance = Variance / Budget

Rollups:
- Quarterly/Yearly: sum Budget/Actual/Forecast; compute Variance, %Variance,
  and shock rates
- YTD: cumulative sums by Department × Year for Budget & Actual (+ Variance/%)

-------------------------------------------------------------------------------
6) FILE SCHEMAS (KEY COLUMNS)
-------------------------------------------------------------------------------
Monthly (monthly_sim.*)
- Keys/periods: Department, Month (CSV), MonthTS (timestamp), Year, Quarter,
  QuarterPeriod, YearlyPeriod, ShockFlag
- Core: Budget, Actual, Forecast, Variance, PctVariance
- YTD:  YTD_Budget, YTD_Actual, YTD_Variance, YTD_PctVariance
- QA (toggle with KEEP_QA_COMPONENTS):
  BaseLevel, DeptGrowth, TrendComponent, SeasonAmp, SeasonPhase, NoiseSigma,
  NoiseComponent, ShockComponent

Note: For Parquet compatibility, QuarterPeriod / YearlyPeriod are strings.
CSV also includes Month (Period) and MonthTS (month-end timestamp).

Quarterly (quarterly_sim.*)
- Department, QuarterPeriod, QuarterBudget, QuarterActual, QuarterForecast,
  QuarterVariance, QuarterPctVariance, ShockCount, Months, ShockRate

Yearly (yearly_sim.*)
- Department, YearlyPeriod, YearlyBudget, YearlyActual, YearlyForecast,
  YearlyVariance, YearlyPctVariance, ShockCount, MonthsInYear, ShockRate

-------------------------------------------------------------------------------
7) CONFIGURATION (EDIT scripts/data-sim.py)
-------------------------------------------------------------------------------
- SEED (default 42)
- START_MONTH, END_MONTH (default “2018-01” → “2024-12”)
- DEPARTMENTS (default 5 standard departments)
- OUTPUT_DIR (default ../data)
- KEEP_QA_COMPONENTS (include/exclude intermediate columns)

-------------------------------------------------------------------------------
8) ROUNDING / FORMATTING TIPS
-------------------------------------------------------------------------------
Prefer to keep full precision internally. For exports:

CSV only:
    df_out.to_csv(..., float_format="%.2f")

CSV & Parquet (round before writing):
    money_cols = ["Budget","Actual","Forecast","Variance",
                  "YTD_Budget","YTD_Actual","YTD_Variance"]
    pct_cols   = ["PctVariance","YTD_PctVariance"]
    df_out[money_cols] = df_out[money_cols].round(2)
    df_out[pct_cols]   = df_out[pct_cols].round(4)

-------------------------------------------------------------------------------
9) ROADMAP
-------------------------------------------------------------------------------
- Forecasting models: ARIMA/ETS/Prophet baselines; compare to 3M roll
- Scenario toggles: volatility up/down, shock rates, growth changes
- Dashboards: Power BI (primary), optional Plotly notebook
- Category layer: add expense categories (Salaries, Travel, etc.) on top of dept
- CLI flags: date window, seed, departments, output dir

-------------------------------------------------------------------------------
10) PROJECT STATUS & MILESTONES
-------------------------------------------------------------------------------
Milestones:
- Planning finalized:           2025-08-02  (DONE)
- Pre-learning/brush-up:        2025-08-06  (DONE on 08-05)
- Synthetic data created:       2025-08-16  (DONE)
- Forecasting model implemented: TBD        (PENDING)
- Dashboard built:              TBD        (PENDING)
- Final report & portfolio:     TBD        (PENDING)

-------------------------------------------------------------------------------
11) LOAD IN PANDAS (SNIPPETS)
-------------------------------------------------------------------------------
CSV:

    import pandas as pd
    m = pd.read_csv("data/monthly_sim.csv", parse_dates=["MonthTS"])
    q = pd.read_csv("data/quarterly_sim.csv")
    y = pd.read_csv("data/yearly_sim.csv")

Parquet (requires pyarrow or fastparquet):

    import pandas as pd
    m = pd.read_parquet("data/monthly_sim.parquet")

-------------------------------------------------------------------------------
12) REPO STRUCTURE
-------------------------------------------------------------------------------
```text
/executive-budgeting-forecasting
├── README.md
├── data/                 # outputs (created by script)
├── scripts/
│   └── data-sim.py       # synthetic data generator
├── notebooks/            # analysis/forecasting (TBD)
└── dashboard/            # Power BI / assets (TBD)
```

Notes:
- Planning initially mentioned a 24‑month window & categories; the current
  simulator ships department-level data for 2018–2024. Category layer is on
  the roadmap.
