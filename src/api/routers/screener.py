import os
import sqlite3
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

def get_db_conn():
    db1 = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
    db_path = db1 if os.path.exists(db1) else os.path.join(PROJECT_ROOT, "nifty100.db")
    return sqlite3.connect(db_path)

@router.get("/screener")
def run_screener(
    min_roe: float = None,
    max_de: float = None,
    min_fcf: float = None,
    sector: str = None,
    min_rev_cagr_5yr: float = None,
    min_pat_cagr_5yr: float = None,
    max_pe: float = None
):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='inner')

    if min_roe is not None:
        df = df[df['return_on_equity_pct'] >= min_roe]
    if max_de is not None:
        df = df[df['debt_to_equity'] <= max_de]
    if min_fcf is not None:
        df = df[df['free_cash_flow_cr'] >= min_fcf]
    if sector:
        df = df[df['sector'].str.lower() == sector.lower()]
    if min_rev_cagr_5yr is not None:
        df = df[df['revenue_cagr_5yr'] >= min_rev_cagr_5yr]
    if min_pat_cagr_5yr is not None:
        df = df[df['pat_cagr_5yr'] >= min_pat_cagr_5yr]
    if max_pe is not None:
        df = df[df['pe_ratio'] <= max_pe]

    return df.fillna(0).to_dict(orient="records")