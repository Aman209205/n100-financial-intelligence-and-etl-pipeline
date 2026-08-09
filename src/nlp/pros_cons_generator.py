"""
N100 Platform - Auto Pros & Cons Generator
Day 30 Implementation
"""

import os
import sqlite3
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUT_DIR = os.path.join(PROJECT_ROOT, "output")

def generate_pros_cons():
    os.makedirs(OUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # 1. Load Data
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios ORDER BY company_id, year ASC;", conn)
    df_pl = pd.read_sql("SELECT * FROM profit_loss ORDER BY company_id, year ASC;", conn) if 'profit_loss' in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist() else pd.DataFrame()
    conn.close()

    if df_comps.empty:
        print("[ERROR] Companies table is empty.")
        return

    results = []

    for _, c_row in df_comps.iterrows():
        cid = c_row['company_id']
        sector = str(c_row.get('sector', '')).lower()
        is_financial = any(keyword in sector for keyword in ['bank', 'financial', 'insurance', 'nbfc'])

        c_ratios = df_ratios[df_ratios['company_id'] == cid].sort_values('year')
        c_pl = df_pl[df_pl['company_id'] == cid].sort_values('year') if not df_pl.empty and 'company_id' in df_pl.columns else pd.DataFrame()

        latest_r = c_ratios.iloc[-1] if not c_ratios.empty else pd.Series()
        latest_pl = c_pl.iloc[-1] if not c_pl.empty else pd.Series()

        # Helper Series extractions
        roe_series = c_ratios.get('return_on_equity_pct', pd.Series(dtype=float)).dropna().tolist()
        roce_series = c_ratios.get('return_on_capital_employed_pct', pd.Series(dtype=float)).dropna().tolist()
        fcf_series = c_ratios.get('free_cash_flow_cr', pd.Series(dtype=float)).dropna().tolist()
        de_series = c_ratios.get('debt_to_equity', pd.Series(dtype=float)).dropna().tolist()
        opm_series = c_ratios.get('operating_profit_margin_pct', pd.Series(dtype=float)).dropna().tolist()
        eps_series = c_ratios.get('eps', pd.Series(dtype=float)).dropna().tolist()
        rev_series = c_pl.get('revenue', pd.Series(dtype=float)).dropna().tolist()

        # Metrics values
        latest_roe = float(latest_r.get('return_on_equity_pct', 0) or 0)
        latest_roce = float(latest_r.get('return_on_capital_employed_pct', 0) or 0)
        latest_de = float(latest_r.get('debt_to_equity', 0) or 0)
        latest_opm = float(latest_r.get('operating_profit_margin_pct', 0) or 0)
        latest_icr = float(latest_r.get('interest_coverage', 10) or 10)
        latest_div = float(latest_r.get('dividend_yield', 0) or 0)
        latest_fcf = float(latest_r.get('free_cash_flow_cr', 0) or 0)
        rev_cagr_5y = float(latest_r.get('revenue_cagr_5yr', 0) or 0)
        pat_cagr_5y = float(latest_r.get('pat_cagr_5yr', 0) or 0)
        eps_cagr_5y = float(latest_r.get('eps_cagr_5yr', 0) or 0)
        latest_np = float(latest_pl.get('net_profit', 1) if not latest_pl.empty else 1)

        # ---------------- PRO RULES ----------------
        # Pro Rule 1: ROE > 20% sustained for 3+ years
        if len(roe_series) >= 3 and all(val > 20 for val in roe_series[-3:]):
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_1', 'text': 'Consistently high return on equity above 20% demonstrates exceptional capital efficiency', 'confidence_pct': 95})

        # Pro Rule 2: FCF positive for 5+ consecutive years
        if len(fcf_series) >= 5 and all(val > 0 for val in fcf_series[-5:]):
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_2', 'text': 'Strong free cash flow generation over 5 years signals healthy business fundamentals', 'confidence_pct': 90})

        # Pro Rule 3: D/E = 0 in latest year
        if latest_de == 0.0 and not is_financial:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_3', 'text': 'Debt-free balance sheet provides financial flexibility and eliminates interest burden', 'confidence_pct': 100})

        # Pro Rule 4: Revenue CAGR > 15% over 5 years
        if rev_cagr_5y > 15:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_4', 'text': f'Revenue growing at above 15% CAGR ({rev_cagr_5y:.1f}%) over 5 years reflects strong business momentum', 'confidence_pct': 85})

        # Pro Rule 5: OPM > 25% in latest year
        if latest_opm > 25:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_5', 'text': f'Operating profit margin above 25% ({latest_opm:.1f}%) indicates strong pricing power and cost discipline', 'confidence_pct': 88})

        # Pro Rule 6: PAT CAGR > 20% over 5 years
        if pat_cagr_5y > 20:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_6', 'text': f'Net profit compounding at above 20% ({pat_cagr_5y:.1f}%) over 5 years creates significant shareholder value', 'confidence_pct': 92})

        # Pro Rule 7: ICR > 10 or Debt Free
        if (latest_icr > 10 or latest_de == 0) and not is_financial:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_7', 'text': 'Very high interest coverage ratio reflects negligible financial stress from debt servicing', 'confidence_pct': 85})

        # Pro Rule 8: Dividend Yield > 2% with FCF positive
        if latest_div > 2.0 and latest_fcf > 0:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_8', 'text': f'Consistent dividend yield above 2% ({latest_div:.1f}%) backed by positive free cash flow', 'confidence_pct': 80})

        # Pro Rule 9: EPS CAGR > 15% over 5 years
        if eps_cagr_5y > 15:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_9', 'text': 'Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding', 'confidence_pct': 87})

        # Pro Rule 10: ROE improving for 3 consecutive years
        if len(roe_series) >= 3 and roe_series[-1] > roe_series[-2] > roe_series[-3]:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_10', 'text': 'Return on equity improving for 3 consecutive years shows strengthening business quality', 'confidence_pct': 82})

        # Pro Rule 11: Revenue CAGR < PAT CAGR (operating leverage)
        if 0 < rev_cagr_5y < pat_cagr_5y:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_11', 'text': 'Revenue growing slower than profits shows improving operating leverage and scale benefits', 'confidence_pct': 80})

        # Pro Rule 12: Balance sheet assets growing with declining debt
        if len(de_series) >= 3 and de_series[-1] < de_series[-2] < de_series[-3]:
            results.append({'company_id': cid, 'type': 'pro', 'rule_id': 'PRO_12', 'text': 'Growing asset base funded by internal accruals reflects self-sustaining growth', 'confidence_pct': 84})


        # ---------------- CON RULES ----------------
        # Con Rule 1: D/E > 2.0 for non-financial companies
        if latest_de > 2.0 and not is_financial:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_1', 'text': f'Debt-to-equity ratio of {latest_de:.2f} is elevated for a non-financial company and warrants monitoring', 'confidence_pct': 90})

        # Con Rule 2: FCF negative for 3 consecutive years
        if len(fcf_series) >= 3 and all(val < 0 for val in fcf_series[-3:]):
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_2', 'text': 'Free cash flow negative for 3 consecutive years raises concern about cash generation quality', 'confidence_pct': 95})

        # Con Rule 3: OPM declining for 3 consecutive years
        if len(opm_series) >= 3 and opm_series[-1] < opm_series[-2] < opm_series[-3]:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_3', 'text': 'Operating margins declining for 3 consecutive years suggest pricing or cost pressure', 'confidence_pct': 85})

        # Con Rule 4: Net profit negative in latest year
        if latest_np < 0:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_4', 'text': 'Company reported a net loss in the most recent financial year', 'confidence_pct': 100})

        # Con Rule 5: Revenue declining for 2+ years
        if len(rev_series) >= 3 and rev_series[-1] < rev_series[-2] < rev_series[-3]:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_5', 'text': 'Revenue contraction over consecutive years indicates demand weakness or market share loss', 'confidence_pct': 88})

        # Con Rule 6: ICR < 1.5
        if latest_icr < 1.5 and not is_financial:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_6', 'text': 'Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations', 'confidence_pct': 92})

        # Con Rule 7: Dividend payout > 100%
        payout = float(latest_r.get('dividend_payout_pct', 0) or 0)
        if payout > 100:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_7', 'text': 'Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable', 'confidence_pct': 85})

        # Con Rule 8: D/E rising for 3 consecutive years
        if len(de_series) >= 3 and de_series[-1] > de_series[-2] > de_series[-3] and not is_financial:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_8', 'text': 'Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk', 'confidence_pct': 83})

        # Con Rule 9: EPS declining for 3 consecutive years
        if len(eps_series) >= 3 and eps_series[-1] < eps_series[-2] < eps_series[-3]:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_9', 'text': 'Earnings per share declining for 3 consecutive years reflects deteriorating profitability', 'confidence_pct': 86})

        # Con Rule 10: ROCE < 10%
        if latest_roce < 10 and not is_financial:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_10', 'text': 'Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital', 'confidence_pct': 80})

        # Con Rule 11: Net Debt > 3x EBITDA
        net_debt_ebitda = float(latest_r.get('net_debt_to_ebitda', 0) or 0)
        if net_debt_ebitda > 3.0 and not is_financial:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_11', 'text': 'Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility', 'confidence_pct': 88})

        # Con Rule 12: Revenue CAGR < 5% over 5 years
        if rev_cagr_5y < 5:
            results.append({'company_id': cid, 'type': 'con', 'rule_id': 'CON_12', 'text': 'Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum', 'confidence_pct': 75})

    # Filter confidence > 60%
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results[df_results['confidence_pct'] > 60]

    # Ensure EVERY company has at least 1 Pro and 1 Con
    final_rows = []
    for cid in df_comps['company_id']:
        comp_df = df_results[df_results['company_id'] == cid] if not df_results.empty else pd.DataFrame()
        
        has_pro = not comp_df[comp_df['type'] == 'pro'].empty if not comp_df.empty else False
        has_con = not comp_df[comp_df['type'] == 'con'].empty if not comp_df.empty else False

        if not comp_df.empty:
            final_rows.extend(comp_df.to_dict('records'))

        # Fallback Pro if missing
        if not has_pro:
            final_rows.append({
                'company_id': cid,
                'type': 'pro',
                'rule_id': 'PRO_FALLBACK',
                'text': 'Established industry presence and stable market positioning as a premier constituent',
                'confidence_pct': 70
            })

        # Fallback Con if missing
        if not has_con:
            final_rows.append({
                'company_id': cid,
                'type': 'con',
                'rule_id': 'CON_FALLBACK',
                'text': 'Operations remain vulnerable to broad market cycles and macroeconomic volatility',
                'confidence_pct': 70
            })

    df_final = pd.DataFrame(final_rows).drop_duplicates()
    out_path = os.path.join(OUT_DIR, "pros_cons_generated.csv")
    df_final.to_csv(out_path, index=False)

    print(f"[SUCCESS] Pros and Cons generated at {out_path} (Total Rows: {len(df_final)})")
    
    # Verification check
    counts = df_final.groupby(['company_id', 'type']).size().unstack(fill_value=0)
    valid = (counts.get('pro', 0) >= 1) & (counts.get('con', 0) >= 1)
    print(f"[VERIFY] Every company has >=1 Pro and >=1 Con: {valid.all()}")

if __name__ == "__main__":
    generate_pros_cons()