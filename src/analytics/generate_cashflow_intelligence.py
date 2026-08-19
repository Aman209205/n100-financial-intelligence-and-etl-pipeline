"""
N100 Platform - Cashflow Intelligence Workbook Generator
Generates output/cashflow_intelligence.xlsx (D-13)
"""

import os
import sqlite3
import pandas as pd
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, "nifty100.db")

OUT_FILE = os.path.join(PROJECT_ROOT, "output", "cashflow_intelligence.xlsx")
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)

def generate_cashflow_workbook():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Fetch tables
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios;", conn)
    conn.close()

    # 2. Build Quality & Patterns Summary (Latest Year available or 2024)
    latest_year = df_ratios['year'].max() if 'year' in df_ratios.columns and not df_ratios.empty else 2024
    df_latest_ratios = df_ratios[df_ratios['year'] == latest_year] if 'year' in df_ratios.columns else df_ratios
    df_merged = pd.merge(df_comps, df_latest_ratios, on='company_id', how='left')

    summary_rows = []
    for _, row in df_merged.iterrows():
        cid = row['company_id']
        cname = row['company_name']
        sec = row['sector']
        
        roe = row.get('return_on_equity_pct', 0) or 0
        fcf = row.get('free_cash_flow_cr', 0) or 0
        cagr_rev = row.get('revenue_cagr_5yr', 0) or 0
        cagr_fcf = row.get('fcf_cagr_5yr', 0) or 0
        
        # Classification
        if fcf > 1000 and roe > 15:
            pattern = "Shareholder Return Machine"
        elif fcf > 0:
            pattern = "Steady Cash Generator"
        elif fcf < 0 and cagr_rev > 12:
            pattern = "Aggressive Growth Reinvestor"
        else:
            pattern = "Turnaround / Cash Watch"

        summary_rows.append({
            "Company ID": cid,
            "Company Name": cname,
            "Sector": sec,
            "ROE (%)": round(float(roe or 0), 2),
            "FCF (Cr)": round(float(fcf or 0), 2),
            "Rev CAGR 5Y (%)": round(float(cagr_rev or 0), 2),
            "FCF CAGR 5Y (%)": round(float(cagr_fcf or 0), 2),
            "Cash Flow Classification": pattern
        })

    df_summary = pd.DataFrame(summary_rows)

    # 3. Sector Median Cash Flow Aggregates
    df_sec_stats = df_summary.groupby("Sector").agg({
        "Company ID": "count",
        "FCF (Cr)": ["median", "mean", "sum"],
        "ROE (%)": "median"
    }).round(2)
    df_sec_stats.columns = ['_'.join(c).strip() for c in df_sec_stats.columns.values]
    df_sec_stats.reset_index(inplace=True)

    # 4. Safe dynamic column selection for Historical FCF
    hist_cols = ['company_id', 'year', 'free_cash_flow_cr', 'operating_profit_margin_pct', 'fcf_cagr_5yr']
    available_hist_cols = [col for col in hist_cols if col in df_ratios.columns]

    # 5. Write to multi-sheet Excel
    with pd.ExcelWriter(OUT_FILE, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name="CF_Quality_Summary", index=False)
        df_sec_stats.to_excel(writer, sheet_name="Sector_CF_Aggregates", index=False)
        if not df_ratios.empty and available_hist_cols:
            df_ratios[available_hist_cols].to_excel(writer, sheet_name="Historical_FCF", index=False)

    print(f"[SUCCESS] Cashflow Intelligence Excel generated at: {OUT_FILE}")

if __name__ == "__main__":
    generate_cashflow_workbook()