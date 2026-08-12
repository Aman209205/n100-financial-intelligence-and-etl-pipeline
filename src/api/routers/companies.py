import os
import sqlite3
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

def get_db_conn():
    db1 = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
    db_path = db1 if os.path.exists(db1) else os.path.join(PROJECT_ROOT, "nifty100.db")
    return sqlite3.connect(db_path)

@router.get("/companies")
def get_companies(sector: str = None, search: str = None):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT * FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df = pd.merge(df_comps, df_ratios, on='company_id', how='left')

    if sector:
        df = df[df['sector'].str.lower() == sector.lower()]
    if search:
        s = search.lower()
        df = df[df['company_id'].str.lower().str.contains(s) | df['company_name'].str.lower().str.contains(s)]

    return df.fillna("").to_dict(orient="records")

@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT * FROM companies WHERE LOWER(company_id) = LOWER(?);", conn, params=(ticker,))
    if df_comps.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE LOWER(company_id) = LOWER(?) ORDER BY year DESC;", conn, params=(ticker,))
    conn.close()

    comp_dict = df_comps.iloc[0].to_dict()
    comp_dict['latest_ratios'] = df_ratios.iloc[0].to_dict() if not df_ratios.empty else {}
    return comp_dict

@router.get("/companies/{ticker}/pl")
def get_company_pl(ticker: str, from_year: int = None, to_year: int = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0].lower() for t in cursor.fetchall()]

    tbl_name = "profit_loss" if "profit_loss" in tables else "pnl" if "pnl" in tables else None
    if not tbl_name:
        conn.close()
        return []

    df = pd.read_sql(f"SELECT * FROM {tbl_name} WHERE LOWER(company_id) = LOWER(?) ORDER BY year ASC;", conn, params=(ticker,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No P&L records for {ticker}")

    if from_year:
        df = df[df['year'] >= from_year]
    if to_year:
        df = df[df['year'] <= to_year]

    return df.fillna(0).to_dict(orient="records")

@router.get("/companies/{ticker}/bs")
def get_company_bs(ticker: str, from_year: int = None, to_year: int = None):
    conn = get_db_conn()
    df = pd.read_sql("SELECT * FROM balance_sheet WHERE LOWER(company_id) = LOWER(?) ORDER BY year ASC;", conn, params=(ticker,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Balance Sheet records for {ticker}")

    if from_year:
        df = df[df['year'] >= from_year]
    if to_year:
        df = df[df['year'] <= to_year]

    return df.fillna(0).to_dict(orient="records")

@router.get("/companies/{ticker}/cashflow")
def get_company_cashflow(ticker: str, from_year: int = None, to_year: int = None):
    conn = get_db_conn()
    df = pd.read_sql("SELECT * FROM cash_flow WHERE LOWER(company_id) = LOWER(?) ORDER BY year ASC;", conn, params=(ticker,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Cash Flow records for {ticker}")

    if from_year:
        df = df[df['year'] >= from_year]
    if to_year:
        df = df[df['year'] <= to_year]

    return df.fillna(0).to_dict(orient="records")

@router.get("/companies/{ticker}/ratios")
def get_company_ratios(ticker: str, year: int = None):
    conn = get_db_conn()
    df = pd.read_sql("SELECT * FROM financial_ratios WHERE LOWER(company_id) = LOWER(?) ORDER BY year ASC;", conn, params=(ticker,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No Ratios records for {ticker}")

    if year:
        df = df[df['year'] == year]

    return df.fillna(0).to_dict(orient="records")

@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet_pdf(ticker: str):
    pdf_path = os.path.join(PROJECT_ROOT, "reports", "tearsheets", f"{ticker.upper()}_tearsheet.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Tearsheet PDF for {ticker} not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{ticker.upper()}_tearsheet.pdf")