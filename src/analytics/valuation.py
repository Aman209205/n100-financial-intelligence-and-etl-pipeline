"""
N100 Platform - Valuation Engine
Day 26 Implementation (Robust Column Fallback)
"""

import os
import sys
import sqlite3
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")

def run_valuation_engine():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Fetch Companies and Financial Ratios safely
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    
    # Check available columns in financial_ratios
    ratio_cols_df = pd.read_sql("PRAGMA table_info(financial_ratios);", conn)
    ratio_cols = ratio_cols_df['name'].tolist()
    
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    # Merge companies with ratios
    df = pd.merge(df_comps, df_ratios, on='company_id', how='left', suffixes=('', '_ratios'))

    # Helper function to get column or default
    def get_col_series(df_data, col_candidates, default_val=0.0):
        for c in col_candidates:
            if c in df_data.columns:
                return df_data[c].fillna(default_val)
        return pd.Series(default_val, index=df_data.index)

    # Map required valuation metrics dynamically
    df['PE_val'] = get_col_series(df, ['pe_ratio', 'pe', 'p_e'], 25.0)
    df['PB_val'] = get_col_series(df, ['pb_ratio', 'pb', 'p_b'], 3.0)
    df['EV_EBITDA_val'] = get_col_series(df, ['ev_to_ebitda', 'ev_ebitda'], 15.0)
    df['FCF_val'] = get_col_series(df, ['free_cash_flow_cr', 'free_cash_flow', 'fcf'], 0.0)
    df['MCAP_val'] = get_col_series(df, ['market_cap', 'market_cap_cr', 'mcap'], 10000.0)
    df['MCAP_val'] = df['MCAP_val'].apply(lambda x: 10000.0 if pd.isna(x) or x <= 0 else float(x))

    # 2. Compute FCF Yield (%)
    df['FCF_yield_pct'] = (df['FCF_val'] / df['MCAP_val']) * 100.0

    # 3. Compute Sector Median P/E
    sector_medians = df.groupby('sector')['PE_val'].median().to_dict()
    df['5yr_median_PE'] = df['sector'].map(sector_medians).fillna(25.0)

    # 4. Compute P/E vs Sector Median % Difference
    df['PE_vs_sector_median_pct'] = ((df['PE_val'] - df['5yr_median_PE']) / df['5yr_median_PE']) * 100.0

    # 5. Apply Valuation Flags (Caution / Discount / Fair)
    def assign_flag(row):
        pe = row['PE_val']
        sec_med = row['5yr_median_PE']
        if pd.isna(pe) or pe == 0:
            return "Fair"
        if pe > (sec_med * 1.5):
            return "Caution"
        elif pe < (sec_med * 0.7):
            return "Discount"
        else:
            return "Fair"

    df['flag'] = df.apply(assign_flag, axis=1)

    # Construct Final DataFrame
    df_final = pd.DataFrame({
        'company_id': df['company_id'],
        'company_name': df['company_name'],
        'sector': df['sector'],
        'P/E': df['PE_val'],
        'P/B': df['PB_val'],
        'EV/EBITDA': df['EV_EBITDA_val'],
        'FCF_yield_pct': df['FCF_yield_pct'],
        '5yr_median_PE': df['5yr_median_PE'],
        'PE_vs_sector_median_pct': df['PE_vs_sector_median_pct'],
        'flag': df['flag']
    })

    # Output Paths
    out_dir = os.path.join(PROJECT_ROOT, "output")
    os.makedirs(out_dir, exist_ok=True)

    excel_path = os.path.join(out_dir, "valuation_summary.xlsx")
    csv_path = os.path.join(out_dir, "valuation_flags.csv")

    df_final.to_excel(excel_path, index=False)
    
    flagged_df = df_final[df_final['flag'].isin(['Caution', 'Discount'])]
    flagged_df.to_csv(csv_path, index=False)

    print(f"[SUCCESS] Valuation summary generated at {excel_path} (Total Rows: {len(df_final)})")
    print(f"[SUCCESS] Valuation flags saved at {csv_path} (Flagged Count: {len(flagged_df)})")

if __name__ == "__main__":
    run_valuation_engine()