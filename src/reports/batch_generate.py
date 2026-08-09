"""
N100 Platform - Batch PDF & Portfolio Report Generator
Day 34 & Day 35 Implementation
"""

import os
import sys
import sqlite3
import pandas as pd

# Fix module import path
PROJECT_ROOT = r"C:\N100-platform"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.reports.tearsheet import build_tearsheet_pdf
from src.reports.sector_report import run_sector_reports

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUT_DIR = os.path.join(PROJECT_ROOT, "output")
PORTFOLIO_DIR = os.path.join(PROJECT_ROOT, "reports", "portfolio")

os.makedirs(PORTFOLIO_DIR, exist_ok=True)

def run_batch_tearsheets():
    conn = sqlite3.connect(DB_PATH)
    df_comps = pd.read_sql("SELECT company_id FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT company_id, COUNT(year) as yr_count FROM financial_ratios GROUP BY company_id;", conn)
    conn.close()

    yr_map = dict(zip(df_ratios['company_id'], df_ratios['yr_count']))

    all_tickers = df_comps['company_id'].tolist()
    skipped = []
    generated = 0

    print(f"[BATCH] Processing tearsheet PDFs for {len(all_tickers)} companies...")

    for cid in all_tickers:
        yr_cnt = yr_map.get(cid, 0)
        if yr_cnt < 3:
            skipped.append({'company_id': cid, 'year_count': yr_cnt, 'reason': 'Fewer than 3 years of financial data'})
            continue

        pdf_path = build_tearsheet_pdf(cid)
        if pdf_path and os.path.exists(pdf_path):
            generated += 1

    # Save skipped tickers log
    df_skipped = pd.DataFrame(skipped)
    skipped_path = os.path.join(OUT_DIR, "skipped_tearsheets.csv")
    if df_skipped.empty:
        df_skipped = pd.DataFrame(columns=['company_id', 'year_count', 'reason'])
    df_skipped.to_csv(skipped_path, index=False)

    print(f"[SUCCESS] {generated} Tearsheet PDFs generated cleanly!")
    print(f"[SUCCESS] Skipped log saved to {skipped_path} (Skipped Count: {len(df_skipped)})")

def build_portfolio_summary_pdf():
    pdf_path = os.path.join(PORTFOLIO_DIR, "portfolio_summary.pdf")
    
    conn = sqlite3.connect(DB_PATH)
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies ORDER BY company_id ASC;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios ORDER BY company_id, year ASC;", conn)
    conn.close()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.4*inch,
        rightMargin=0.4*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('PTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)
    sec_style = ParagraphStyle('PSec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#0B2545"), spaceAfter=6)
    body_style = ParagraphStyle('PBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)

    story = []

    for idx, c_row in df_comps.iterrows():
        cid = c_row['company_id']
        cname = c_row['company_name']
        sec = c_row['sector']

        c_ratios = df_ratios[df_ratios['company_id'] == cid].sort_values('year')
        r_latest = c_ratios.iloc[-1] if not c_ratios.empty else pd.Series()
        r_prev = c_ratios.iloc[-2] if len(c_ratios) >= 2 else pd.Series()

        def trend_arrow(val_latest, val_prev):
            if pd.isna(val_latest) or pd.isna(val_prev):
                return "➡️"
            diff = val_latest - val_prev
            if abs(diff) <= 0.02 * abs(val_prev if val_prev != 0 else 1):
                return "➡️"
            return "⬆️" if diff > 0 else "⬇️"

        roe_curr = float(r_latest.get('return_on_equity_pct', 0) or 0)
        roe_prev = float(r_prev.get('return_on_equity_pct', 0) or 0)
        roe_arrow = trend_arrow(roe_curr, roe_prev)

        roce_curr = float(r_latest.get('return_on_capital_employed_pct', 0) or 0)
        roce_prev = float(r_prev.get('return_on_capital_employed_pct', 0) or 0)
        roce_arrow = trend_arrow(roce_curr, roce_prev)

        header_data = [[
            Paragraph(f"<b>{cname} ({cid})</b>", title_style),
            Paragraph(f"Sector: <b>{sec}</b> | Portfolio Executive Summary", ParagraphStyle('Sub', parent=title_style, fontSize=9, fontName='Helvetica'))
        ]]
        header_table = Table(header_data, colWidths=[4.5*inch, 2.7*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B2545")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Latest Key Performance Indicators & Trend Signals", sec_style))

        kpis_data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Latest Value</b>", body_style), Paragraph("<b>Trend Signal</b>", body_style)],
            [Paragraph("Return on Equity (ROE)", body_style), Paragraph(f"{roe_curr:.1f}%", body_style), Paragraph(f"{roe_arrow}", body_style)],
            [Paragraph("Return on Capital Employed (ROCE)", body_style), Paragraph(f"{roce_curr:.1f}%", body_style), Paragraph(f"{roce_arrow}", body_style)],
            [Paragraph("Debt to Equity (D/E)", body_style), Paragraph(f"{float(r_latest.get('debt_to_equity',0) or 0):.2f}", body_style), Paragraph("—", body_style)],
            [Paragraph("Operating Margin (OPM)", body_style), Paragraph(f"{float(r_latest.get('operating_profit_margin_pct',0) or 0):.1f}%", body_style), Paragraph("—", body_style)],
            [Paragraph("Price to Earnings (P/E)", body_style), Paragraph(f"{float(r_latest.get('pe_ratio',0) or 0):.1f}x", body_style), Paragraph("—", body_style)],
            [Paragraph("Free Cash Flow (FCF)", body_style), Paragraph(f"₹{float(r_latest.get('free_cash_flow_cr',0) or 0):,.0f} Cr", body_style), Paragraph("—", body_style)],
        ]
        kpi_table = Table(kpis_data, colWidths=[3.2*inch, 2.0*inch, 2.0*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D0D0")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(kpi_table)

        if idx < len(df_comps) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"[SUCCESS] Portfolio Summary PDF created at: {pdf_path}")

if __name__ == "__main__":
    run_batch_tearsheets()
    run_sector_reports()
    build_portfolio_summary_pdf()