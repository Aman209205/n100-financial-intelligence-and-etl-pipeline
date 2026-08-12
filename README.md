#  N100 Financial Intelligence Platform

An enterprise-grade, robust ETL data pipeline engineered to ingest, clean, validate, and synchronize financial market records for the Nifty 100 universe. This platform serves as the production-ready data foundation for high-throughput financial analytics, reporting, and model serving.

---

##  Project Status & Progress
* **Current Milestone:** `Sprint 1 — Data Foundation` Completed Successfully 
* **Priority:** Medium
* **Database Engine:** SQLite 3

---

##  Architecture & Data Pipeline Overview

The framework processes raw unformatted financial dataset streams through an automated, constraint-enforced ingestion cycle.
[12 Raw Source Files]
│
▼
[safe_load_excel()] ───► (Drops Title Banners & Sanitizes Duplicated Columns)
│
▼
[Data Normaliser] ────► (Ticker Canonicalization & Year Standardization)
│
▼
[Data Validator] ─────► (Checks 16 DQ Rules: PK, FK, OPM Mismatches, Balance Equation)
│                 │
│                 └──► [validation_failures.csv] (Telemetry Report)
▼
[SQLite Production DB] ───► [load_audit.csv] (Telemetry Row Execution Metrics)

##  Sprint 1 Ingestion Matrix (Telemetry Logs)

The pipeline maps records with absolute relational integrity (`PRAGMA foreign_keys = ON`), executing seamlessly with **zero CRITICAL rejections**:

| Target Database Table | Ingested Records Count | Ingestion Validation Status |
| :--- | :---: | :--- |
|  **companies** (Core Master) | **92** | Ingested & Verified (`SELECT COUNT(*) = 92`) |
|  **profitandloss** | **1,165** | Synchronized (Composite Keys Secured) |
|  **balancesheet** | **1,058** | Processed (Asset-Equity Equation Verified) |
|  **cashflow** | **1,058** | Operational Liquidity Records Loaded |
|  **financial_ratios** | **1,041** | Operational Valuations Aligned |
|  **stock_prices** | **5,520** | High-Throughput EOD Records Synced |
|  **analysis** | **5** | Qualitative Investment Summaries Synced |
|  **documents** | **1,585** | Filings & PDF URLs Ingested |
|  **prosandcons** | **5** | Formatted Analytical Points |
|  **peer_groups** | **56** | Competitive Relational Matrix Populated |

   **Exit Criteria Status:** `PRAGMA foreign_key_check` ➔ **0 rows detected**. (Relational database consistency is 100% verified and locked).

---

##  Project Directory Structure

```markdown directory
N100-platform/
│
├── database/
│   ├── nifty100.db                  # Fully populated production database
│   └── schema.sql                   # 10-table relational schema definition
│
├── src/
│   └── etl/
│       ├── loader.py                # Main ETL pipeline core execution engine
│       ├── validator.py             # Strict scalar evaluation logic (16 DQ Rules)
│       └── normaliser.py            # Financial data formats normalizer
│
├── notebooks/
│   └── exploratory_queries.sql      # 10 advanced exploratory analytical SQL queries
│
├── output/
│   ├── load_audit.csv               # Row telemetry and runtime metadata logs
│   └── validation_failures.csv      # Automatically isolated Data Quality violations
│
└── README.md                        # Project documentation
```
##  Team & Acknowledgments
* **Lead Engineer:** Aman Kumar
* **Assigned To:** vaishnavikhandelwal1781, gauravsinha9182


## Project Status & Progress
* **Current Milestone:** `Sprint 2 — Financial Ratio Engine` Completed Successfully 
* **Priority:** Medium
* **Database Engine:** SQLite 3
* **Target Delivery:** 17 Jul 2026

 **Exit Criteria Status (Sprint 2):** `SELECT COUNT(*) FROM financial_ratios` ➔ **1,165 rows generated** (Exceeds target baseline of >= 1,100 rows). 28 Automated Unit Tests completed with **0 failures**.

---

##  Analytical Engines & Features (Sprint 2)

###  1. Profitability & Efficiency Framework (`ratios.py`)
Computes core financial benchmarks with defensive mathematical boundaries:
* **Net Profit Margin (NPM) & ROA:** Automatically drops calculation and returns `None` if denominators (`sales`, `total_assets`) equal zero.
* **Return on Equity (ROE):** Evaluates asset-liability health, isolating broken corporate structures by returning `None` if `Equity + Reserves <= 0`.
* **ROCE Carve-Out:** Applies relative context benchmarking for `Financials` broad-sector companies instead of absolute thresholds.

###  2. Leverage & Efficiency Engine
* **Debt-to-Equity (D/E):** Suppresses generic risk flags for banking and financial institutions where high leverage is structurally normal, while flagging non-financial firms if `D/E > 5`.
* **Interest Coverage Ratio (ICR):** Identifies debt-free corporate frameworks (`interest = 0`) and assigns a custom `Debt Free` label, while raising risk warnings if `ICR < 1.5`.

###  3. Advanced 6-Case CAGR Engine (`cagr.py`)
Processes 3-year, 5-year, and 10-year compound growth for Revenue, PAT, and EPS by catching 6 critical business scenario edge-cases:
* `NORMAL`: Positive to positive growth tracking.
* `DECLINE_TO_LOSS`: Positive baseline transitioning into negative horizons.
* `TURNAROUND`: Negative initial baseline shifting to a positive outcome.
* `BOTH_NEGATIVE` / `ZERO_BASE`: Handles structural zero and sub-zero calculation blocks.
* `INSUFFICIENT`: Automatically flags periods with partial or missing historical records.

###  4. Capital Allocation 8-Pattern Classifier (`cashflow_kpis.py`)
Categorizes corporate management strategies by monitoring the numeric algebraic signs (+ / -) of Cash Flow from Operations (CFO), Investing (CFI), and Financing (CFF):
* `(+, -, -)` + High CFO/PAT ➔ **Shareholder Returns**
* `(+, -, -)` Generic ➔ **Reinvestor**
* `(+, +, -)` ➔ **Liquidating Assets**
* `(-, +, +)` ➔ **Distress Signal**
* `(-, -, +)` ➔ **Growth Funded by Debt**
* `(+, +, +)` ➔ **Cash Accumulator**
* `(-, -, -)` ➔ **Pre-Revenue**
* `(+, -, +)` ➔ **Mixed**

Outputs are compiled automatically into `output/capital_allocation.csv` and mathematical variances are routed into `output/ratio_edge_cases.log`.

## Project Status & Progress

* **Current Milestone:** `Sprint 3 – Screener & Peer Comparison Engine` Completed Successfully 
* **Target Delivery:** 24 Jul 2026

> **Exit Criteria Status (Sprint 3):** All **14/14 Data Quality Unit Tests** Passed (0 Failures) ➔ `output/screener_output.xlsx` (6 sheets) & `output/peer_comparison.xlsx` (11 sheets) generated cleanly.

---

## Analytical Engines & Features (Sprint 3)

### 1. Dynamic Screener Filter Engine (`src/screener/engine.py` & `screener_config.yaml`)
* **15-KPI Threshold Filters:** Supports analyst-configurable filters across ROE, D/E, FCF, Revenue CAGR, PAT CAGR, OPM, P/E, P/B, Dividend Yield, ICR, Market Cap, NPM, EPS CAGR, Asset Turnover, and Sales.
* **Defensive Boundary Rules:** Automatically bypasses D/E limits for the `Financials` sector and treats `Debt Free` flags as infinite Interest Coverage Ratio (ICR).
* **6 Preset Screeners:** `Quality Compounder`, `Value Pick`, `Growth Accelerator`, `Dividend Champion`, `Debt-Free Blue Chip`, and `Turnaround Watch`.

### 2. Composite Quality Scoring & Screener Export (`src/screener/exporter.py`)
* **Winsorised 0–100 Quality Score:** Applies P10/P90 Winsorisation to cap extreme outliers before calculating weighted scores across 4 core dimensions:
  * **35% Profitability:** ROE (15%) + ROCE (10%) + NPM (10%)
  * **30% Cash Quality:** FCF CAGR (15%) + CFO/PAT Ratio (10%) + Positive FCF Flag (5%)
  * **20% Growth:** Revenue CAGR (10%) + PAT CAGR (10%)
  * **15% Leverage:** D/E Score (10%) + ICR Score (5%)
* **Screener Excel Exporter:** Generates `output/screener_output.xlsx` with 6 sheets (one per preset) featuring 20 KPI columns and condition-based green/red cell highlights.

### 3. Peer Percentile Engine & Visualizations (`src/analytics/peer.py` & `radar.py`)
* **SQLite Peer Percentiles:** Computes `PERCENT_RANK` across 10 key metrics within each peer group and populates **828 percentile records** into the SQLite `peer_percentiles` table (with inverted percentile scoring for D/E).
* **8-Axis Radar Chart Visualizer:** Generates polar radar charts comparing company performance against peer group averages, exporting **92 PNG charts** to `reports/radar_charts/`.

### 4. Peer Comparison Workbook Exporter (`src/analytics/peer_report.py`)
* Generates `output/peer_comparison.xlsx` containing **11 distinct peer group worksheets**.
* Highlights benchmark companies in gold, applies green/yellow/red color-coding to percentile ranks, and appends a peer group median summary row at the bottom of each sheet.

## Project Status & Progress

* **Current Milestone:** `Sprint 4 – Dashboard & Valuation Module` Completed Successfully 
* **Priority:** Medium
* **Target Delivery:** 29 Jul 2026

> **Exit Criteria Status (Sprint 4):** All 8 Streamlit Screens running on `localhost:8501` without errors across all 92 tickers. `output/valuation_summary.xlsx` (92 rows) and `output/valuation_flags.csv` generated cleanly.

---

## Interactive Dashboard & Valuation Deliverables (Sprint 4)

### 1. Multi-Page Streamlit Dashboard (`src/dashboard/app.py` & `src/dashboard/pages/`)
* **8 Interactive Screens:**
  * **01_home.py:** Top 6 KPI tiles, Plotly sector breakdown donut chart, and top 5 composite quality score table.
  * **02_profile.py:** Company search box, 10-year Revenue/Profit bar charts, ROE/ROCE line charts, and Pros/Cons badges.
  * **03_screener.py:** 10 metric sliders, 6 quick preset buttons, live results table, and CSV exporter.
  * **04_peers.py:** Peer sector selection, 8-axis Plotly Polar Radar chart, and benchmark comparison table.
  * **05_trends.py:** Multi-metric overlay 10-year historical trend chart.
  * **06_sectors.py:** Revenue vs ROE bubble chart (sized by Market Cap) and sector median KPI bar chart.
  * **07_capital.py:** Capital allocation strategy treemap across 8 distinct allocation patterns.
  * **08_reports.py:** Searchable BSE annual report links and availability badges.

### 2. Cached Database Data Loader (`src/dashboard/utils/db.py`)
* Implements `@st.cache_data(ttl=600)` across all SQLite query functions to ensure all screen transitions load in under 3 seconds.

### 3. Valuation Engine (`src/analytics/valuation.py`)
* **FCF Yield & Valuation Flags:** Calculates FCF Yield ($\frac{\text{FCF}}{\text{Market Cap}} \times 100$) and evaluates P/E against Sector Median P/E:
  * $\text{P/E} > 1.5 \times \text{Sector Median} \implies$ **Caution**
  * $\text{P/E} < 0.7 \times \text{Sector Median} \implies$ **Discount**
  * Otherwise $\implies$ **Fair**
* **Outputs Generated:** `output/valuation_summary.xlsx` and `output/valuation_flags.csv`.

---

## How to Run the Application

To launch the Streamlit dashboard locally:

```powershell
streamlit run src/dashboard/app.py
```

## Sprint 5 — Intelligence, NLP & PDF Reports Completed 

* **Status:** Fully Executed & Verified
* **Completion Date:** 08 Aug 2026

---

## Deliverables & Modules (Sprint 5)

### 1. NLP Analysis Parser (`src/nlp/parser.py`)
* Regex engine (`(\d+)\s*Years?:?\s*(-?[\d.]+)%`) to parse structured CAGR and ROE text data from analysis fields.
* **Outputs Generated:**
  * `output/analysis_parsed.csv` — Structured metric values across 1, 3, 5, and 10-year horizons.
  * `output/parse_failures.csv` — Non-matching text logs.
  * `output/cagr_divergence_flagged.csv` — Cross-validation report flagging >5% variance between parsed text and Ratio Engine metrics.

### 2. Auto Pros & Cons Generator (`src/nlp/pros_cons_generator.py`)
* Rule-based engine implementing 12 Pro Rules and 12 Con Rules based on financial fundamentals (ROE, FCF, D/E, ICR, OPM, EPS CAGR, etc.).
* Assigns confidence scores (60%–100%) and enforces a fallback mechanism to guarantee at least 1 Pro and 1 Con for all 92 companies.
* **Output Generated:** `output/pros_cons_generated.csv` (487 rules generated).

### 3. Cash Flow Intelligence Module (`src/analytics/cashflow_kpis.py`)
* Computes 5-year average **CFO Quality Score** ($\text{CFO/PAT}$) labeled as *High Quality*, *Moderate*, or *Accrual Risk*.
* Calculates **CapEx Intensity** ($\frac{|\text{CFI}|}{\text{Sales}} \times 100$) labeled as *Asset Light*, *Moderate*, or *Capital Intensive*.
* Flags distress signals ($\text{CFO} < 0 \text{ and } \text{CFF} > 0$) and deleveraging trends ($\text{CFF} < 0 \text{ with declining debt}$).
* **Outputs Generated:**
  * `output/cashflow_intelligence.xlsx` (92 rows with complete cash flow KPIs).
  * `output/distress_alerts.csv` (High-risk flagged tickers).

### 4. Capital Allocation Report & Strategy Tracking (`src/analytics/capital_allocation_report.py`)
* Classifies all companies across 8 distinct capital allocation strategies and logs year-over-year pattern shifts.
* **Output Generated:** `output/pattern_changes.csv` (69 YoY strategy transitions tracked).

### 5. ReportLab Executive PDF Engine (`src/reports/`)
* **Company Tearsheets (`src/reports/tearsheet.py`):** 2-page executive PDF tearsheets for all 92 companies with navy headers, KPI tiles, 10-year revenue/profit bar charts, ROE/ROCE line charts, balance sheet stacked bars, cash flow waterfalls, Pros/Cons bullet points, and strategy badges.
* **Sector Reports (`src/reports/sector_report.py`):** Executive PDF summaries per sector featuring median benchmarks and constituent peer comparison tables.
* **Batch Generator (`src/reports/batch_generate.py`):** Batch processing engine generating all PDFs cleanly with zero text overflow.
* **Outputs Generated:**
  * `reports/tearsheets/*.pdf` — 92 individual company tearsheet PDFs (~100 KB each).
  * `reports/sector/*_report.pdf` — Sector benchmark PDF reports.
  * `reports/portfolio/portfolio_summary.pdf` — Alphabetically ordered portfolio summary PDF with KPI trend arrows.
  * `output/skipped_tearsheets.csv` — Execution log for companies with insufficient data.


  ## Sprint 6 — API Server, Clustering & Final QA Completed 

* **Status:** Fully Executed & Verified (100% Sign-Off)
* **Completion Date:** 13 Aug 2026

---

## Deliverables & Modules (Sprint 6)

### 1. KMeans Clustering Engine (`src/analytics/clustering.py`)
* Implemented KMeans with $k=5$ (`random_state=42`) using sector-median missing value imputation and `StandardScaler`.
* Features: ROE, Debt/Equity, Revenue CAGR 5Y, FCF CAGR 5Y, OPM.
* **Outputs Generated:**
  * `reports/elbow_plot.png` — Inertia elbow curve confirming optimal $k=5$.
  * `output/cluster_labels.csv` — All 92 companies assigned to 5 archetypes with centroid distance metrics.

### 2. Cluster Profiling & Outlier Analytics (`src/analytics/cluster_profiling.py`)
* Mean/median metric profiling across all 5 clusters (`output/cluster_profile_summary.csv`).
* Pearson correlation matrix heatmap saved to `reports/correlation_heatmap.png`.
* Z-score outlier detection ($|Z| > 3$) logged to `output/outlier_report.csv`.
* Percentile distribution table (P10 through P90) generated at `output/portfolio_stats.csv`.

### 3. FastAPI REST Service Architecture (`src/api/`)
* Modular router setup across 8 endpoints with CORS and request-duration logging middleware (`src/api/main.py`).
* Full coverage across `/health`, `/companies`, `/screener`, `/sectors`, `/peers`, `/valuation`, `/portfolio`, `/documents`, and `/tearsheet` binary streaming.
* Exported OpenAPI 3.0 Specification: `docs/openapi.json`.

### 4. Comprehensive Pytest Suite (`tests/`)
* **Test Count:** 102 Tests Collected | **0 Failures | 0 Errors** 
* HTML Execution Report saved to `reports/pytest_report.html` (Satisfies Acceptance Gate AC-18).

### 5. Benchmarking & Sign-Off Documentation (`docs/`)
* **Load Benchmarking (`output/perf_notes.md`):** 10 concurrent thread calls completed cleanly.
* **Analyst Guide (`docs/analyst_guide.pdf`):** 11-page operational guide for financial analysts and developers.
* **Acceptance Sign-Off (`docs/acceptance_checklist.pdf`):** Formal PASS verification across all 20 Acceptance Gates (AC-01 through AC-20).