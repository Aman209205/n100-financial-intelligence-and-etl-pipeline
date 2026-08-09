"""
N100 Platform - Capital Allocation Report & Pattern Shifts
Day 32 Implementation
"""

import os
import sqlite3
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUT_DIR = os.path.join(PROJECT_ROOT, "output")

PATTERNS = [
    "Cash Compounders",
    "High Dividend Payers",
    "Conservative Reinvestors",
    "Leveraged Expansion",
    "Aggressive Growth CapEx",
    "Capital Preservers / Laggards",
    "Balanced Allocators",
    "Restructuring Watch"
]

def classify_row_pattern(row):
    fcf = row.get('free_cash_flow_cr', 0) or 0
    roe = row.get('return_on_equity_pct', 0) or 0
    div = row.get('dividend_yield', 0) or 0
    de = row.get('debt_to_equity', 0) or 0

    if roe > 18 and fcf > 500:
        return "Cash Compounders"
    elif div > 2.0:
        return "High Dividend Payers"
    elif de < 0.2 and roe > 12:
        return "Conservative Reinvestors"
    elif de > 1.2:
        return "Leveraged Expansion"
    elif fcf < 0 and roe > 15:
        return "Aggressive Growth CapEx"
    elif roe < 8:
        return "Capital Preservers / Laggards"
    elif fcf > 0:
        return "Balanced Allocators"
    else:
        return "Restructuring Watch"

def run_capital_allocation_report():
    os.makedirs(OUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios ORDER BY company_id, year ASC;", conn)
    conn.close()

    if df_ratios.empty:
        print("[ERROR] Financial ratios table is empty.")
        return

    # Apply classification across all company-years
    df_ratios['capital_pattern'] = df_ratios.apply(classify_row_pattern, axis=1)

    # 1. Year-over-Year Pattern Shift Tracking
    df_ratios_sorted = df_ratios.sort_values(['company_id', 'year'])
    
    changes = []
    for cid, group in df_ratios_sorted.groupby('company_id'):
        group_records = group.to_dict('records')
        for i in range(1, len(group_records)):
            prev_yr = group_records[i-1]
            curr_yr = group_records[i]
            
            if prev_yr['capital_pattern'] != curr_yr['capital_pattern']:
                changes.append({
                    'company_id': cid,
                    'year_from': prev_yr['year'],
                    'year_to': curr_yr['year'],
                    'pattern_from': prev_yr['capital_pattern'],
                    'pattern_to': curr_yr['capital_pattern'],
                    'shift_summary': f"Shifted from {prev_yr['capital_pattern']} in {prev_yr['year']} to {curr_yr['capital_pattern']} in {curr_yr['year']}"
                })

    df_changes = pd.DataFrame(changes)
    changes_path = os.path.join(OUT_DIR, "pattern_changes.csv")
    df_changes.to_csv(changes_path, index=False)
    print(f"[SUCCESS] Pattern YoY shifts saved to: {changes_path} (Shift Events Count: {len(df_changes)})")

    # 2. Latest Year Pattern Distribution & Update `cashflow_intelligence.xlsx`
    latest_ratios = df_ratios[df_ratios['year'] == 2024]
    latest_pattern_map = dict(zip(latest_ratios['company_id'], latest_ratios['capital_pattern']))

    intel_xlsx_path = os.path.join(OUT_DIR, "cashflow_intelligence.xlsx")
    if os.path.exists(intel_xlsx_path):
        df_intel = pd.read_excel(intel_xlsx_path)
        df_intel['capital_allocation'] = df_intel['company_id'].map(latest_pattern_map).fillna("Balanced Allocators")
        df_intel.to_excel(intel_xlsx_path, index=False)
        print(f"[SUCCESS] Updated 'capital_allocation' column in {intel_xlsx_path}")
    else:
        print(f"[INFO] {intel_xlsx_path} not found. Ensure cashflow_kpis.py has run.")

    # Print Latest Pattern Distribution
    dist = latest_ratios['capital_pattern'].value_counts()
    print("\n--- Latest Year (2024) Capital Allocation Distribution ---")
    for pat in PATTERNS:
        print(f" * {pat}: {dist.get(pat, 0)} companies")

if __name__ == "__main__":
    run_capital_allocation_report()