"""
N100 Platform - Peer Radar Chart Visualizer Engine
Day 19 Implementation
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "radar_charts")

RADAR_METRICS = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'net_profit_margin_pct',
    'debt_to_equity',
    'free_cash_flow_cr',
    'pat_cagr_5yr',
    'revenue_cagr_5yr',
    'composite_quality_score'
]

METRIC_LABELS = ['ROE', 'ROCE', 'NPM', 'D/E', 'FCF', 'PAT CAGR', 'Rev CAGR', 'Quality']

def normalize_0_100(series):
    """Min-max scaler to normalize metrics onto a uniform 0-100 radar scale."""
    min_val, max_val = series.min(), series.max()
    if max_val == min_val or pd.isna(max_val):
        return pd.Series(50.0, index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100.0

def generate_radar_charts():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            f.*,
            c.company_name,
            c.sector AS peer_group_name
        FROM financial_ratios f
        JOIN companies c ON f.company_id = c.company_id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("[ERROR] No ratio data found for radar charts.")
        return

    latest_year = df['year'].max()
    df_latest = df[df['year'] == latest_year].copy()

    # Fallback score if composite missing
    if 'composite_quality_score' not in df_latest.columns:
        df_latest['composite_quality_score'] = 50.0

    # Scale all metrics onto 0-100 uniform polar scale
    scaled_df = df_latest.copy()
    for m in RADAR_METRICS:
        if m in scaled_df.columns:
            scaled_df[m] = normalize_0_100(scaled_df[m].fillna(0))
        else:
            scaled_df[m] = 50.0

    num_vars = len(RADAR_METRICS)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] # Close the circular polygon loop

    charts_count = 0

    for idx, row in scaled_df.iterrows():
        cid = row['company_id']
        cname = str(row['company_name'])
        group_name = row['peer_group_name']

        # Company Values
        comp_values = [row[m] for m in RADAR_METRICS]
        comp_values += comp_values[:1]

        # Peer Group Mean Calculation
        group_mask = scaled_df['peer_group_name'] == group_name
        if group_mask.sum() > 1:
            group_mean = scaled_df[group_mask][RADAR_METRICS].mean().tolist()
            legend_label = f"{group_name} Avg"
        else:
            group_mean = scaled_df[RADAR_METRICS].mean().tolist() # Nifty 100 fallback
            legend_label = "Nifty 100 Avg"
            
        group_mean += group_mean[:1]

        # Plot Setup
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Company Polygon (Solid)
        ax.plot(angles, comp_values, color='#1f77b4', linewidth=2, label=cname)
        ax.fill(angles, comp_values, color='#1f77b4', alpha=0.25)

        # Peer Average Overlay (Dashed)
        ax.plot(angles, group_mean, color='#ff7f0e', linewidth=1.5, linestyle='--', label=legend_label)

        # Labels & Aesthetics
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(METRIC_LABELS, size=9)
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color="grey", size=7)
        plt.ylim(0, 100)
        plt.title(f"{cid} - Peer Comparison Radar", size=11, weight='bold', y=1.08)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=8)

        # Save to PNG
        file_path = os.path.join(OUTPUT_DIR, f"{cid}_radar.png")
        plt.tight_layout()
        plt.savefig(file_path, dpi=120)
        plt.close()

        charts_count += 1

    print(f"[SUCCESS] {charts_count} Radar Charts exported to: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_radar_charts()