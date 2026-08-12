import os
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

@router.get("/portfolio/stats")
def get_portfolio_stats():
    csv_path = os.path.join(PROJECT_ROOT, "output", "portfolio_stats.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Portfolio stats file not found. Run Day 37 script first.")
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")