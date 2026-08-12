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

@router.get("/sectors")
def get_sectors():
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT company_id, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='inner')
    
    summary = []
    for sec, group in df.groupby('sector'):
        roe_val = group['return_on_equity_pct'].median() if 'return_on_equity_pct' in group.columns else 0.0
        pe_val = group['pe_ratio'].median() if 'pe_ratio' in group.columns else 0.0
        de_val = group['debt_to_equity'].median() if 'debt_to_equity' in group.columns else 0.0

        summary.append({
            "sector": sec,
            "company_count": len(group),
            "median_roe": round(float(roe_val or 0), 2),
            "median_pe": round(float(pe_val or 0), 2),
            "median_de": round(float(de_val or 0), 2)
        })

    return summary

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT * FROM companies WHERE LOWER(sector) = LOWER(?);", conn, params=(sector,))
    if df_comps.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")

    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='left')
    return df.fillna(0).to_dict(orient="records")