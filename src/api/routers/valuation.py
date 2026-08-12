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

@router.get("/market-cap/{ticker}")
def get_valuation_multiples(ticker: str):
    conn = get_db_conn()
    df = pd.read_sql("SELECT year, pe_ratio, pb_ratio, ev_to_ebitda, dividend_yield FROM financial_ratios WHERE LOWER(company_id) = LOWER(?) ORDER BY year ASC;", conn, params=(ticker,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Valuation history for {ticker} not found")

    return df.fillna(0).to_dict(orient="records")