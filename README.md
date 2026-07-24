#  N100 Financial Intelligence Platform

An enterprise-grade, robust ETL data pipeline engineered to ingest, clean, validate, and synchronize financial market records for the Nifty 100 universe. This platform serves as the production-ready data foundation for high-throughput financial analytics, reporting, and model serving.

---

##  Project Status & Progress
* **Current Milestone:** `Sprint 1 — Data Foundation` Completed Successfully ✅
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

* **Current Milestone:** `Sprint 3 – Screener & Peer Comparison Engine` Completed Successfully ✅
* **Priority:** High
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