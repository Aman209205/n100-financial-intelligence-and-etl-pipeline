"""
N100 Platform - Screener Engine Module
"""

import os
import sys
import sqlite3
import yaml
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, "nifty100.db")

def run_preset_screener(preset_name: str, config_path: str = None) -> pd.DataFrame:
    """Runs a named preset from configuration on full 92 company universe."""
    if config_path is None:
        config_path = os.path.join(PROJECT_ROOT, "config", "screener_config.yaml")

    if not os.path.exists(config_path):
        return pd.DataFrame()

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    presets = config.get("presets", {})
    if preset_name not in presets:
        return pd.DataFrame()

    preset_rules = presets[preset_name]

    conn = sqlite3.connect(DB_PATH)
    df_comps = pd.read_sql("SELECT * FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on="company_id", how="inner")

    # Map broad_sector alias if not present
    if "broad_sector" not in df.columns and "sector" in df.columns:
        df["broad_sector"] = df["sector"]

    # Filter logic
    if "min_roe" in preset_rules:
        df = df[df["return_on_equity_pct"] >= preset_rules["min_roe"]]
    if "max_de" in preset_rules:
        df = df[df["debt_to_equity"] <= preset_rules["max_de"]]
    if "min_fcf" in preset_rules:
        df = df[df["free_cash_flow_cr"] >= preset_rules["min_fcf"]]

    return df