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

@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT * FROM companies WHERE LOWER(sector) = LOWER(?);", conn, params=(group_name,))
    if df_comps.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Peer group/sector '{group_name}' not found")

    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='left')
    return df.fillna(0).to_dict(orient="records")

@router.get("/companies/{ticker}/peers/compare")
def compare_company_peers(ticker: str):
    conn = get_db_conn()
    df_comp = pd.read_sql("SELECT company_id, sector FROM companies WHERE LOWER(company_id) = LOWER(?);", conn, params=(ticker,))
    if df_comp.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    sector = df_comp.iloc[0]['sector']
    df_all = pd.read_sql("SELECT c.company_id, c.sector, r.return_on_equity_pct, r.return_on_capital_employed_pct, r.debt_to_equity, r.pe_ratio, r.operating_profit_margin_pct, r.revenue_cagr_5yr, r.fcf_cagr_5yr, r.dividend_yield FROM companies c JOIN financial_ratios r ON c.company_id = r.company_id WHERE r.year = 2024;", conn)
    conn.close()

    target_df = df_all[df_all['company_id'].str.lower() == ticker.lower()]
    sector_df = df_all[df_all['sector'] == sector]

    return {
        "company": target_df.fillna(0).to_dict(orient="records")[0] if not target_df.empty else {},
        "peer_group_average": sector_df.drop(columns=['company_id', 'sector']).mean().round(2).to_dict(),
        "nifty100_benchmark": df_all.drop(columns=['company_id', 'sector']).median().round(2).to_dict()
    }