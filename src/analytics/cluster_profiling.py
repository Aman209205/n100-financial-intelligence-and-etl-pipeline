"""
N100 Platform - Cluster Profiling, Correlation Heatmap & Outlier Analysis
Day 37 Implementation
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, "nifty100.db")

OUT_DIR = os.path.join(PROJECT_ROOT, "output")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

CORE_KPIS = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'debt_to_equity',
    'pe_ratio',
    'pb_ratio',
    'operating_profit_margin_pct',
    'revenue_cagr_5yr',
    'pat_cagr_5yr',
    'fcf_cagr_5yr',
    'dividend_yield'
]

def run_day37_profiling():
    conn = sqlite3.connect(DB_PATH)
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='left')

    # Ensure all core KPI columns exist and are numeric
    for kpi in CORE_KPIS:
        if kpi not in df.columns:
            df[kpi] = np.nan
        df[kpi] = pd.to_numeric(df[kpi], errors='coerce')
        df[kpi] = df[kpi].fillna(df[kpi].median()).fillna(0.0)

    # ---------------- 1. Cluster Profiling ----------------
    clusters_csv = os.path.join(OUT_DIR, "cluster_labels.csv")
    if os.path.exists(clusters_csv):
        df_clusters = pd.read_csv(clusters_csv)
        df_merged_clusters = pd.merge(df, df_clusters, on='company_id', how='inner')
        
        cluster_profile = df_merged_clusters.groupby(['cluster_id', 'cluster_name'])[[
            'return_on_equity_pct', 'debt_to_equity', 'revenue_cagr_5yr', 'fcf_cagr_5yr', 'operating_profit_margin_pct'
        ]].agg(['mean', 'median']).round(2)

        profile_path = os.path.join(OUT_DIR, "cluster_profile_summary.csv")
        cluster_profile.to_csv(profile_path)
        print(f"[SUCCESS] Cluster profile summary saved to: {profile_path}")

    # ---------------- 2. Correlation Matrix Heatmap ----------------
    df_kpis = df[CORE_KPIS].copy()
    # Friendly labels for plot
    friendly_labels = [
        'ROE (%)', 'ROCE (%)', 'D/E Ratio', 'P/E Ratio', 'P/B Ratio',
        'OPM (%)', 'Rev CAGR 5Y', 'PAT CAGR 5Y', 'FCF CAGR 5Y', 'Div Yield (%)'
    ]
    df_kpis.columns = friendly_labels
    corr_matrix = df_kpis.corr(method='pearson').round(2)

    plt.figure(figsize=(10, 8), dpi=150)
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title("Nifty 100 Core Financial KPIs Correlation Heatmap (2024)", fontsize=12, fontweight='bold', pad=12)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    heatmap_path = os.path.join(REPORTS_DIR, "correlation_heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"[SUCCESS] Correlation heatmap saved to: {heatmap_path}")

    # ---------------- 3. Outlier Detection (|Z-score| > 3) ----------------
    outlier_rows = []
    for sector_name, group in df.groupby('sector'):
        if len(group) < 3:
            continue
        for kpi in CORE_KPIS:
            vals = group[kpi].values
            std = np.std(vals)
            if std > 0:
                z_scores = (vals - np.mean(vals)) / std
                for idx, z in enumerate(z_scores):
                    if abs(z) > 3.0:
                        outlier_rows.append({
                            'company_id': group.iloc[idx]['company_id'],
                            'sector': sector_name,
                            'metric': kpi,
                            'metric_value': round(group.iloc[idx][kpi], 2),
                            'sector_mean': round(np.mean(vals), 2),
                            'z_score': round(z, 2),
                            'outlier_type': 'High Outlier' if z > 3 else 'Low Outlier'
                        })

    df_outliers = pd.DataFrame(outlier_rows)
    outlier_csv = os.path.join(OUT_DIR, "outlier_report.csv")
    if df_outliers.empty:
        df_outliers = pd.DataFrame(columns=['company_id', 'sector', 'metric', 'metric_value', 'sector_mean', 'z_score', 'outlier_type'])
    df_outliers.to_csv(outlier_csv, index=False)
    print(f"[SUCCESS] Outlier report saved to: {outlier_csv} (Total Outliers Flagged: {len(df_outliers)})")

    # ---------------- 4. Portfolio Statistics (P10 to P90, Mean, Std) ----------------
    stats_data = []
    for kpi, label in zip(CORE_KPIS, friendly_labels):
        s = df[kpi].dropna()
        stats_data.append({
            'metric': label,
            'P10': round(np.percentile(s, 10), 2),
            'P25': round(np.percentile(s, 25), 2),
            'P50': round(np.percentile(s, 50), 2),
            'P75': round(np.percentile(s, 75), 2),
            'P90': round(np.percentile(s, 90), 2),
            'Mean': round(np.mean(s), 2),
            'Std': round(np.std(s), 2)
        })

    df_stats = pd.DataFrame(stats_data)
    stats_csv = os.path.join(OUT_DIR, "portfolio_stats.csv")
    df_stats.to_csv(stats_csv, index=False)
    print(f"[SUCCESS] Portfolio statistics saved to: {stats_csv}")

if __name__ == "__main__":
    run_day37_profiling()