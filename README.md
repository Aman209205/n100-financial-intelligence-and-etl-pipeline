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

>  **Exit Criteria Status:** `PRAGMA foreign_key_check` ➔ **0 rows detected**. (Relational database consistency is 100% verified and locked).

---

##  Project Directory Structure

```directory
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

##  Team & Acknowledgments
* **Lead Engineer:** Aman Kumar
* **Assigned To:** vaishnavikhandelwal1781, gauravsinha9182