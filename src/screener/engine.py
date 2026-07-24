"""
N100 Platform - Screener Engine Core
Day 15 & Day 16 Implementation (Duplicate Column Fix)
"""

import os
import yaml
import sqlite3
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")

def load_screener_data(conn=None):
    """Loads combined financial ratios and company master details cleanly."""
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
        
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(companies);")
    cols = [row[1] for row in cursor.fetchall()]

    select_cols = []
    
    if "company_name" in cols:
        select_cols.append("c.company_name")
    else:
        select_cols.append("c.company_id AS company_name")

    if "sector" in cols:
        select_cols.append("c.sector")
    else:
        select_cols.append("'General' AS sector")

    if "broad_sector" in cols:
        select_cols.append("c.broad_sector")
    else:
        select_cols.append("c.sector AS broad_sector" if "sector" in cols else "'General' AS broad_sector")

    if "market_cap" in cols:
        select_cols.append("c.market_cap")
    else:
        select_cols.append("10000.0 AS market_cap")

    if "pe_ratio" in cols:
        select_cols.append("c.pe_ratio")
    else:
        select_cols.append("15.0 AS pe_ratio")

    if "pb_ratio" in cols:
        select_cols.append("c.pb_ratio")
    else:
        select_cols.append("2.0 AS pb_ratio")

    if "dividend_yield" in cols:
        select_cols.append("c.dividend_yield")
    else:
        select_cols.append("1.5 AS dividend_yield")

    cols_sql = ", ".join(select_cols)
    query = f"""
        SELECT 
            f.*,
            {cols_sql}
        FROM financial_ratios f
        JOIN companies c ON f.company_id = c.company_id
    """
    df = pd.read_sql(query, conn)
    
    # Remove duplicate columns if any exist
    df = df.loc[:, ~df.columns.duplicated()].copy()
    
    # Latest year per company for screening
    latest_df = df.sort_values('year').groupby('company_id', as_index=False).last()
    
    if close_conn:
        conn.close()
        
    return latest_df

def apply_screener_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Applies custom dynamic threshold filters supporting all 15 KPI rules.
    """
    filtered = df.copy()

    for key, threshold in filters.items():
        if threshold is None:
            continue
            
        if key == 'de_max':
            sector_col = 'broad_sector' if 'broad_sector' in filtered.columns else 'sector'
            mask = (filtered['debt_to_equity'] <= threshold) | (filtered[sector_col].astype(str).str.lower().str.contains('financial'))
            filtered = filtered[mask]

        elif key == 'icr_min':
            mask = (filtered['interest_coverage'] >= threshold) | (filtered['interest_coverage'].isna())
            filtered = filtered[mask]

        elif key == 'roe_min':
            filtered = filtered[filtered['return_on_equity_pct'] >= threshold]
        elif key == 'fcf_min':
            filtered = filtered[filtered['free_cash_flow_cr'] >= threshold]
        elif key == 'revenue_cagr_5yr_min':
            filtered = filtered[filtered['revenue_cagr_5yr'] >= threshold]
        elif key == 'pat_cagr_5yr_min':
            filtered = filtered[filtered['pat_cagr_5yr'] >= threshold]
        elif key == 'opm_min':
            filtered = filtered[filtered['operating_profit_margin_pct'] >= threshold]
        elif key == 'pe_max':
            filtered = filtered[filtered['pe_ratio'] <= threshold]
        elif key == 'pb_max':
            filtered = filtered[filtered['pb_ratio'] <= threshold]
        elif key == 'div_yield_min':
            filtered = filtered[filtered['dividend_yield'] >= threshold]
        elif key == 'div_payout_max':
            filtered = filtered[filtered['dividend_payout_ratio_pct'] <= threshold]
        elif key == 'market_cap_min':
            filtered = filtered[filtered['market_cap'] >= threshold]
        elif key == 'net_profit_min':
            filtered = filtered[filtered['net_profit_margin_pct'] >= threshold]
        elif key == 'eps_cagr_min':
            filtered = filtered[filtered['eps_cagr_5yr'] >= threshold]
        elif key == 'asset_turnover_min':
            filtered = filtered[filtered['asset_turnover'] >= threshold]

    return filtered

def run_preset_screener(preset_name: str, config_path: str = None) -> pd.DataFrame:
    """Runs a named preset from configuration on full 92 company universe."""
    if config_path is None:
        config_path = os.path.join(PROJECT_ROOT, "config", "screener_config.yaml")
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    preset_filters = config['presets'].get(preset_name, {})
    df = load_screener_data()
    return apply_screener_filters(df, preset_filters)