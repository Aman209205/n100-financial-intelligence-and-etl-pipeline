"""
N100 Platform - Sector Report PDF Generator
Day 34 Implementation
"""

import os
import sqlite3
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
SECTOR_DIR = os.path.join(PROJECT_ROOT, "reports", "sector")

os.makedirs(SECTOR_DIR, exist_ok=True)

def build_sector_pdf(sector_name, df_sec):
    safe_sec_filename = str(sector_name).replace('/', '_').replace(' ', '_')
    pdf_filename = os.path.join(SECTOR_DIR, f"{safe_sec_filename}_report.pdf")

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=0.4*inch,
        rightMargin=0.4*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('SecHead', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)
    sub_style = ParagraphStyle('SecSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.lightgrey)
    section_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#0B2545"), spaceAfter=6)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    head_cell = ParagraphStyle('HeadCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)

    story = []

    # Header
    header_data = [[
        Paragraph(f"<b>Sector Executive Report: {sector_name}</b>", title_style),
        Paragraph(f"Total Companies: <b>{len(df_sec)}</b>", sub_style)
    ]]
    header_table = Table(header_data, colWidths=[5.2*inch, 2.0*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B2545")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Sector Median KPIs
    story.append(Paragraph("Sector Median Benchmarks (2024)", section_style))
    
    med_roe = df_sec['return_on_equity_pct'].median() if 'return_on_equity_pct' in df_sec.columns else 0.0
    med_pe = df_sec['pe_ratio'].median() if 'pe_ratio' in df_sec.columns else 0.0
    med_de = df_sec['debt_to_equity'].median() if 'debt_to_equity' in df_sec.columns else 0.0
    med_opm = df_sec['operating_profit_margin_pct'].median() if 'operating_profit_margin_pct' in df_sec.columns else 0.0

    kpi_data = [
        [Paragraph("<b>Median ROE</b>", cell_style), Paragraph("<b>Median P/E</b>", cell_style), Paragraph("<b>Median D/E</b>", cell_style), Paragraph("<b>Median OPM</b>", cell_style)],
        [Paragraph(f"{med_roe:.1f}%", cell_style), Paragraph(f"{med_pe:.1f}x", cell_style), Paragraph(f"{med_de:.2f}", cell_style), Paragraph(f"{med_opm:.1f}%", cell_style)]
    ]
    kpi_table = Table(kpi_data, colWidths=[1.8*inch]*4)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.white),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # Company Breakdown Table
    story.append(Paragraph("Constituent Companies Benchmark", section_style))

    table_data = [[
        Paragraph("Ticker", head_cell),
        Paragraph("Company Name", head_cell),
        Paragraph("ROE (%)", head_cell),
        Paragraph("ROCE (%)", head_cell),
        Paragraph("D/E", head_cell),
        Paragraph("P/E", head_cell),
        Paragraph("OPM (%)", head_cell),
        Paragraph("FCF (Cr)", head_cell)
    ]]

    for _, r in df_sec.iterrows():
        table_data.append([
            Paragraph(str(r.get('company_id', '')), cell_style),
            Paragraph(str(r.get('company_name', ''))[:20], cell_style),
            Paragraph(f"{float(r.get('return_on_equity_pct', 0) or 0):.1f}", cell_style),
            Paragraph(f"{float(r.get('return_on_capital_employed_pct', 0) or 0):.1f}", cell_style),
            Paragraph(f"{float(r.get('debt_to_equity', 0) or 0):.2f}", cell_style),
            Paragraph(f"{float(r.get('pe_ratio', 0) or 0):.1f}", cell_style),
            Paragraph(f"{float(r.get('operating_profit_margin_pct', 0) or 0):.1f}", cell_style),
            Paragraph(f"{float(r.get('free_cash_flow_cr', 0) or 0):,.0f}", cell_style)
        ])

    comp_table = Table(table_data, colWidths=[0.8*inch, 1.8*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.8*inch, 1.1*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B2545")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D0D0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(comp_table)

    doc.build(story)
    return pdf_filename

def run_sector_reports():
    conn = sqlite3.connect(DB_PATH)
    df_comps = pd.read_sql("SELECT company_id, company_name, sector FROM companies;", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024;", conn)
    conn.close()

    df_merged = pd.merge(df_comps, df_ratios, on='company_id', how='left')

    sectors = df_merged['sector'].dropna().unique()
    print(f"[BATCH] Generating sector reports for {len(sectors)} sectors...")

    generated = 0
    for sec in sectors:
        df_sec = df_merged[df_merged['sector'] == sec]
        pdf_path = build_sector_pdf(sec, df_sec)
        if os.path.exists(pdf_path):
            generated += 1

    print(f"[SUCCESS] {generated} Sector PDF reports saved to: {SECTOR_DIR}")

if __name__ == "__main__":
    run_sector_reports()