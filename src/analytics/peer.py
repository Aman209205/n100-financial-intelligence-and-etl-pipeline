"""
N100 Platform - Peer Percentile Ranking Engine
Day 18 Implementation
"""

import os
import sqlite3
import pandas as pd
import numpy as np

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")

METRICS_TO_RANK = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'net_profit_margin_pct',
    'debt_to_equity',
    'free_cash_flow_cr',
    'pat_cagr_5yr',
    'revenue_cagr_5yr',
    'eps_cagr_5yr',
    'interest_coverage',
    'asset_turnover'
]

def calculate_peer_percentiles():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Prepare target schema
    conn.execute("DROP TABLE IF EXISTS peer_percentiles;")
    conn.execute("""
        CREATE TABLE peer_percentiles (
            company_id TEXT,
            peer_group_name TEXT,
            metric TEXT,
            value REAL,
            percentile_rank REAL,
            year INTEGER,
            PRIMARY KEY (company_id, metric, year)
        );
    """)
    conn.commit()

    # 2. Fetch combined ratios + sector peer mapping
    query = """
        SELECT 
            f.*,
            c.sector AS peer_group_name
        FROM financial_ratios f
        JOIN companies c ON f.company_id = c.company_id
    """
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("[WARNING] No financial ratios found to compute peer percentiles.")
        conn.close()
        return

    # Use latest year dataset per company for peer comparisons
    latest_year = df['year'].max()
    df_latest = df[df['year'] == latest_year].copy()

    records = []

    # 3. Compute PERCENT_RANK within each peer group
    for peer_group, group_df in df_latest.groupby('peer_group_name'):
        if pd.isna(peer_group) or not str(peer_group).strip():
            continue
            
        group_size = len(group_df)
        
        for metric in METRICS_TO_RANK:
            if metric not in group_df.columns:
                continue
                
            # Sort values
            sorted_df = group_df[['company_id', metric]].dropna().sort_values(metric)
            n = len(sorted_df)
            
            if n == 0:
                continue
                
            for idx, row in sorted_df.reset_index(drop=True).iterrows():
                cid = row['company_id']
                val = row[metric]
                
                # Formula: Percentile Rank (0.0 to 100.0)
                rank_pct = (idx / (n - 1) * 100.0) if n > 1 else 50.0
                
                # Inverse rule for Debt-to-Equity (lower D/E = better rank)
                if metric == 'debt_to_equity':
                    rank_pct = 100.0 - rank_pct
                    
                records.append((
                    cid,
                    str(peer_group),
                    metric,
                    float(val) if pd.notna(val) else None,
                    round(rank_pct, 2),
                    int(latest_year)
                ))

    # 4. Insert computed percentile ranks into SQLite
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO peer_percentiles VALUES (?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM peer_percentiles;")
    total_count = cursor.fetchone()[0]
    
    print(f"[SUCCESS] 'peer_percentiles' table populated with {total_count} calculated ranks.")
    conn.close()

if __name__ == "__main__":
    calculate_peer_percentiles()