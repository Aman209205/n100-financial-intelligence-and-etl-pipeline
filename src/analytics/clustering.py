"""
N100 Platform - KMeans Clustering Module
Day 36 Implementation (Dynamic Root Directory Fix)
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Dynamically set PROJECT_ROOT to 2 levels up from src/analytics/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUT_DIR = os.path.join(PROJECT_ROOT, "output")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

FEATURES = [
    'return_on_equity_pct',
    'debt_to_equity',
    'revenue_cagr_5yr',
    'fcf_cagr_5yr',
    'operating_profit_margin_pct'
]

def run_kmeans_clustering():
    if not os.path.exists(DB_PATH):
        # Fallback check for root database
        alt_db = os.path.join(PROJECT_ROOT, "nifty100.db")
        if os.path.exists(alt_db):
            db_to_use = alt_db
        else:
            raise FileNotFoundError(f"Database file not found at {DB_PATH} or {alt_db}")
    else:
        db_to_use = DB_PATH

    conn = sqlite3.connect(db_to_use)
    
    # 1. Fetch Companies and Financial Ratios (Latest year 2024)
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='left')

    # Ensure all required feature columns exist
    for f in FEATURES:
        if f not in df.columns:
            df[f] = np.nan

    # 2. Missing Value Imputation with Sector Median
    for f in FEATURES:
        df[f] = pd.to_numeric(df[f], errors='coerce')
        sector_medians = df.groupby('sector')[f].transform('median')
        df[f] = df[f].fillna(sector_medians).fillna(df[f].median()).fillna(0.0)

    X = df[FEATURES].values

    # 3. Standard Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Generate Elbow Plot (k from 2 to 10)
    inertias = []
    k_range = range(2, 11)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    plt.figure(figsize=(7, 4), dpi=150)
    plt.plot(k_range, inertias, 'bo-', linewidth=2, markersize=6)
    plt.axvline(x=5, color='r', linestyle='--', label='Selected k=5')
    plt.xlabel('Number of Clusters (k)', fontsize=9)
    plt.ylabel('Inertia (Sum of Squared Distances)', fontsize=9)
    plt.title('KMeans Elbow Plot for Nifty 100 Archetypes', fontsize=11, fontweight='bold')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    elbow_path = os.path.join(REPORTS_DIR, "elbow_plot.png")
    plt.savefig(elbow_path)
    plt.close()
    print(f"[SUCCESS] Elbow plot saved to: {elbow_path}")

    # 5. Final KMeans Execution with k=5
    kmeans5 = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_labels = kmeans5.fit_predict(X_scaled)
    centroids = kmeans5.cluster_centers_

    # Calculate distance to assigned centroid
    distances = []
    for i, label in enumerate(cluster_labels):
        dist = np.linalg.norm(X_scaled[i] - centroids[label])
        distances.append(round(dist, 4))

    archetype_names = {
        0: "High-Quality Compounders",
        1: "Defensive Dividend Payers",
        2: "Value Cyclicals",
        3: "Emerging Growth",
        4: "Distressed or Turnaround"
    }

    df['cluster_id'] = cluster_labels
    df['cluster_name'] = df['cluster_id'].map(archetype_names)
    df['distance_from_centroid'] = distances

    # Export cluster_labels.csv
    out_df = df[['company_id', 'cluster_id', 'cluster_name', 'distance_from_centroid']]
    out_csv = os.path.join(OUT_DIR, "cluster_labels.csv")
    out_df.to_csv(out_csv, index=False)

    print(f"[SUCCESS] Cluster labels saved to: {out_csv} (Total Rows: {len(out_df)})")

if __name__ == "__main__":
    run_kmeans_clustering()