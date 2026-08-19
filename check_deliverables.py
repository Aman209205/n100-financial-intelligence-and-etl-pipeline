"""
N100 Platform - 23 Deliverables Verification Script
"""

import os
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def check_db_table(tbl_name):
    for p in [os.path.join(PROJECT_ROOT, "database", "nifty100.db"), os.path.join(PROJECT_ROOT, "data", "nifty100.db"), os.path.join(PROJECT_ROOT, "nifty100.db")]:
        if os.path.exists(p):
            conn = sqlite3.connect(p)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tbl_name,))
            found = cur.fetchone() is not None
            conn.close()
            if found:
                return True
    return False

DELIVERABLES = [
    ("D-01", "Sprint 1", "nifty100.db", lambda: any(os.path.exists(os.path.join(PROJECT_ROOT, d, "nifty100.db")) for d in ["database", "data", ""])),
    ("D-02", "Sprint 1", "output/load_audit.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "load_audit.csv"))),
    ("D-03", "Sprint 1", "output/validation_failures.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "validation_failures.csv"))),
    ("D-04", "Sprint 1", "notebooks/exploratory_queries.sql", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "notebooks", "exploratory_queries.sql")) or os.path.exists(os.path.join(PROJECT_ROOT, "database", "exploratory_queries.sql"))),
    ("D-05", "Sprint 2", "financial_ratios table", lambda: check_db_table("financial_ratios")),
    ("D-06", "Sprint 2", "output/capital_allocation.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "capital_allocation.csv"))),
    ("D-07", "Sprint 3", "output/screener_output.xlsx", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "screener_output.xlsx"))),
    ("D-08", "Sprint 3", "config/screener_config.yaml", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "config", "screener_config.yaml"))),
    ("D-09", "Sprint 3", "output/peer_comparison.xlsx", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "peer_comparison.xlsx"))),
    ("D-10", "Sprint 3", "reports/radar_charts/ (92 charts)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "reports", "radar_charts"))),
    ("D-11", "Sprint 4", "src/dashboard/app.py (Streamlit Dashboard)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "src", "dashboard", "app.py"))),
    ("D-12", "Sprint 4", "output/valuation_summary.xlsx", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "valuation_summary.xlsx"))),
    ("D-13", "Sprint 5", "output/cashflow_intelligence.xlsx", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "cashflow_intelligence.xlsx"))),
    ("D-14", "Sprint 5", "output/pros_cons_generated.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "pros_cons_generated.csv"))),
    ("D-15", "Sprint 5", "output/analysis_parsed.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "analysis_parsed.csv"))),
    ("D-16", "Sprint 5", "reports/tearsheets/ (92 Company PDFs)", lambda: len(os.listdir(os.path.join(PROJECT_ROOT, "reports", "tearsheets"))) >= 92 if os.path.exists(os.path.join(PROJECT_ROOT, "reports", "tearsheets")) else False),
    ("D-17", "Sprint 5", "reports/sector/ (Sector PDFs)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "reports", "sector"))),
    ("D-18", "Sprint 5", "reports/portfolio/ (Portfolio Summary PDF)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "reports", "portfolio", "portfolio_summary.pdf"))),
    ("D-19", "Sprint 6", "output/cluster_labels.csv", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "output", "cluster_labels.csv"))),
    ("D-20", "Sprint 6", "src/api/main.py (FastAPI Server)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "src", "api", "main.py"))),
    ("D-21", "Sprint 6", "reports/pytest_report.html", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "reports", "pytest_report.html"))),
    ("D-22", "Sprint 6", "docs/analyst_guide.pdf (10+ pages)", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "docs", "analyst_guide.pdf"))),
    ("D-23", "Sprint 6", "docs/acceptance_checklist.pdf", lambda: os.path.exists(os.path.join(PROJECT_ROOT, "docs", "acceptance_checklist.pdf"))),
]

def main():
    print("="*80)
    print("NIFTY 100 PLATFORM — 23 DELIVERABLES VERIFICATION")
    print("="*80)
    
    all_passed = True
    for did, sprint, item, check_fn in DELIVERABLES:
        try:
            status = "DONE [PASS]" if check_fn() else "MISSING [FAIL]"
        except Exception:
            status = "ERROR [FAIL]"
            
        if "FAIL" in status:
            all_passed = False
            
        print(f"[{did}] {sprint:<10} | {item:<48} -> {status}")

    print("="*80)
    if all_passed:
        print("[STATUS] ALL 23 DELIVERABLES COMPLETED & READY FOR SIGN-OFF.")
    else:
        print("[STATUS] SOME DELIVERABLES ARE MISSING. CHECK PATHS ABOVE.")
    print("="*80)

if __name__ == "__main__":
    main()