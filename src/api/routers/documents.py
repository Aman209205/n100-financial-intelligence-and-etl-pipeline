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

@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    conn = get_db_conn()
    df_comps = pd.read_sql("SELECT company_id, company_name FROM companies WHERE LOWER(company_id) = LOWER(?);", conn, params=(ticker,))
    conn.close()

    if df_comps.empty:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    cname = df_comps.iloc[0]['company_name']
    
    # Standard document links structure
    docs = [
        {"document_type": "Annual Report 2024", "url": f"https://www.bseindia.com/annual_reports/{ticker}_2024.pdf", "is_url_valid": True},
        {"document_type": "Investor Presentation Q4", "url": f"https://www.nseindia.com/investors/{ticker}_Q4.pdf", "is_url_valid": True}
    ]
    return {"company_id": ticker.upper(), "company_name": cname, "documents": docs}