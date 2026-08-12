"""
N100 Platform - Performance Benchmarking & SQLite Indexing
Day 43 Implementation (Safe Indexing Fix)
"""

import os
import time
import sqlite3
import concurrent.futures
from fastapi.testclient import TestClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

from src.api.main import app

client = TestClient(app)

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, "nifty100.db")

def apply_sqlite_indexes():
    """Adds indexes to company_id and year columns for tables that exist in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch existing table names in SQLite schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {t[0].lower() for t in cursor.fetchall()}
    
    index_targets = [
        ("financial_ratios", "CREATE INDEX IF NOT EXISTS idx_ratios_cid_yr ON financial_ratios(company_id, year);"),
        ("balance_sheet", "CREATE INDEX IF NOT EXISTS idx_bs_cid_yr ON balance_sheet(company_id, year);"),
        ("cash_flow", "CREATE INDEX IF NOT EXISTS idx_cf_cid_yr ON cash_flow(company_id, year);")
    ]
    
    for table_name, idx_sql in index_targets:
        if table_name.lower() in existing_tables:
            cursor.execute(idx_sql)
        
    conn.commit()
    conn.close()
    print("[SUCCESS] SQLite performance indexes verified/created for existing tables!")

def run_screener_call(i):
    start = time.time()
    res = client.get("/api/v1/screener?min_roe=15")
    elapsed = time.time() - start
    return res.status_code, elapsed

def run_load_test():
    print("[LOAD TEST] Running 10 concurrent Screener API requests...")
    start_total = time.time()
    
    times = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_screener_call, i) for i in range(10)]
        for f in concurrent.futures.as_completed(futures):
            status, duration = f.result()
            times.append(duration)
            
    total_duration = time.time() - start_total
    avg_time = sum(times) / len(times)
    
    print(f"[SUCCESS] 10 concurrent requests finished in {total_duration:.2f}s (Avg per request: {avg_time*1000:.1f}ms)")
    
    # Save performance notes
    perf_path = os.path.join(PROJECT_ROOT, "output", "perf_notes.md")
    os.makedirs(os.path.dirname(perf_path), exist_ok=True)
    
    with open(perf_path, "w") as f:
        f.write("# Day 43 — Performance Benchmarking Notes\n\n")
        f.write(f"* **10 Concurrent API Requests Duration:** {total_duration:.2f} seconds (Target: < 10.0s)\n")
        f.write(f"* **Average Latency per Screener Call:** {avg_time*1000:.2f} ms\n")
        f.write("* **Company Profile Load Target:** < 3.0 seconds per ticker\n")
        f.write("* **Database Optimizations:** Added Composite Indexes `(company_id, year)` on existing financial tables.\n")
        
    print(f"[SUCCESS] Performance benchmarks logged to: {perf_path}")

if __name__ == "__main__":
    apply_sqlite_indexes()
    run_load_test()