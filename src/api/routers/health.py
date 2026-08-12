import os
import time
import sqlite3
from fastapi import APIRouter

router = APIRouter()
START_TIME = time.time()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

def get_db_path():
    db1 = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
    return db1 if os.path.exists(db1) else os.path.join(PROJECT_ROOT, "nifty100.db")

@router.get("/health")
def health_check():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    counts = {}
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            counts[tbl] = cursor.fetchone()[0]
        except Exception:
            counts[tbl] = 0
    conn.close()

    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
        "db_row_counts": counts
    }