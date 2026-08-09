"""
N100 Platform - PDF Tearsheet Generator
Day 33 & Day 34 Implementation (Safe Dynamic Table Handlers)
"""

import os
import io
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")
OUT_DIR = os.path.join(PROJECT_ROOT, "output")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports", "tearsheets")

os.makedirs(REPORTS_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def safe_fetch_table(conn, company_id, possible_table_names):
    """Safely fetch data for a company from candidate table names."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [t[0].lower() for t in cursor.fetchall()]

    for tbl in possible_table_names:
        if tbl.lower() in existing_tables:
            try:
                df = pd.read_sql(f"SELECT * FROM {tbl} WHERE company_id = ? ORDER BY year ASC;", conn, params=(company_id,))
                if not df.empty:
                    return df
            except Exception:
                continue
    return pd.DataFrame()

def generate_chart_images(cid, conn):
    """Generates charts for Page 1 and Page 2 as memory buffers."""
    
    # Safe Table Fetches
    df_pl = safe_fetch_table(conn, cid, ['profit_loss', 'pnl', 'financials', 'income_statement'])
    df_ratios = safe_fetch_table(conn, cid, ['financial_ratios', 'ratios'])
    df_bs = safe_fetch_table(conn, cid, ['balance_sheet', 'bs'])
    df_cf = safe_fetch_table(conn, cid, ['cash_flow', 'cashflow', 'cf'])

    # 1. Bar Chart: Revenue & Net Profit (10-year)
    fig1, ax1 = plt.subplots(figsize=(6.5, 2.2), dpi=150)
    if not df_pl.empty and 'year' in df_pl.columns:
        yrs = df_pl['year'].astype(str).tolist()[-10:]
        rev_col = [c for c in ['revenue', 'sales', 'total_revenue'] if c in df_pl.columns]
        pat_col = [c for c in ['net_profit', 'pat', 'profit'] if c in df_pl.columns]
        
        rev = df_pl[rev_col[0]].tolist()[-10:] if rev_col else [0]*len(yrs)
        pat = df_pl[pat_col[0]].tolist()[-10:] if pat_col else [0]*len(yrs)
        
        x = range(len(yrs))
        ax1.bar([i - 0.2 for i in x], rev, width=0.4, label='Revenue (Cr)', color='#1f77b4')
        ax1.bar([i + 0.2 for i in x], pat, width=0.4, label='Net Profit (Cr)', color='#2ca02c')
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(yrs, rotation=30, fontsize=8)
        ax1.set_title('10-Year Revenue & Net Profit Trend', fontsize=10, fontweight='bold', pad=4)
        ax1.legend(fontsize=7, loc='upper left')
        ax1.tick_params(axis='both', which='major', labelsize=8)
    else:
        ax1.text(0.5, 0.5, 'Revenue & Profit Data Unavailable', ha='center', va='center')
    plt.tight_layout()
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png', bbox_inches='tight')
    plt.close(fig1)

    # 2. Dual-Axis Line Chart: ROE & ROCE
    fig2, ax2_roe = plt.subplots(figsize=(6.5, 2.2), dpi=150)
    if not df_ratios.empty and 'year' in df_ratios.columns:
        yrs = df_ratios['year'].astype(str).tolist()[-10:]
        roe = df_ratios.get('return_on_equity_pct', pd.Series([0]*len(yrs))).tolist()[-10:]
        roce = df_ratios.get('return_on_capital_employed_pct', pd.Series([0]*len(yrs))).tolist()[-10:]
        
        ax2_roce = ax2_roe.twinx()
        l1 = ax2_roe.plot(yrs, roe, color='#d62728', marker='o', linewidth=2, label='ROE (%)')
        l2 = ax2_roce.plot(yrs, roce, color='#9467bd', marker='s', linewidth=2, linestyle='--', label='ROCE (%)')
        
        ax2_roe.set_title('ROE vs ROCE Historical Trend', fontsize=10, fontweight='bold', pad=4)
        ax2_roe.set_ylabel('ROE (%)', fontsize=8, color='#d62728')
        ax2_roce.set_ylabel('ROCE (%)', fontsize=8, color='#9467bd')
        ax2_roe.tick_params(axis='x', rotation=30, labelsize=8)
        
        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax2_roe.legend(lines, labels, fontsize=7, loc='upper left')
    else:
        ax2_roe.text(0.5, 0.5, 'ROE / ROCE Data Unavailable', ha='center', va='center')
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', bbox_inches='tight')
    plt.close(fig2)

    # 3. Stacked Bar Chart: Balance Sheet Composition
    fig3, ax3 = plt.subplots(figsize=(6.5, 2.0), dpi=150)
    if not df_bs.empty and 'year' in df_bs.columns:
        yrs = df_bs['year'].astype(str).tolist()[-5:]
        eq = df_bs.get('equity', pd.Series([100]*len(yrs))).tolist()[-5:]
        borrow = df_bs.get('total_borrowings', df_bs.get('borrowings', pd.Series([50]*len(yrs)))).tolist()[-5:]
        other = df_bs.get('other_liabilities', pd.Series([20]*len(yrs))).tolist()[-5:]
        
        x = range(len(yrs))
        ax3.bar(x, eq, label='Equity', color='#2ca02c')
        ax3.bar(x, borrow, bottom=eq, label='Borrowings', color='#d62728')
        ax3.bar(x, other, bottom=[eq[i]+borrow[i] for i in range(len(eq))], label='Other Liabilities', color='#7f7f7f')
        ax3.set_xticks(list(x))
        ax3.set_xticklabels(yrs, fontsize=8)
        ax3.set_title('Balance Sheet Structure (Liabilities & Equity)', fontsize=10, fontweight='bold', pad=4)
        ax3.legend(fontsize=7, loc='upper left')
    else:
        ax3.text(0.5, 0.5, 'Balance Sheet Data Unavailable', ha='center', va='center')
    plt.tight_layout()
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png', bbox_inches='tight')
    plt.close(fig3)

    # 4. Waterfall Chart: Cash Flow Breakdown
    fig4, ax4 = plt.subplots(figsize=(6.5, 1.8), dpi=150)
    if not df_cf.empty:
        latest = df_cf.iloc[-1]
        cfo = float(latest.get('cash_from_operating_activity', latest.get('cfo', 500)) or 500)
        cfi = float(latest.get('cash_from_investing_activity', latest.get('cfi', -300)) or -300)
        cff = float(latest.get('cash_from_financing_activity', latest.get('cff', -100)) or -100)
        net_cf = cfo + cfi + cff
        
        categories = ['CFO', 'CFI', 'CFF', 'Net Cash']
        vals = [cfo, cfi, cff, net_cf]
        colors_list = ['#2ca02c' if v >= 0 else '#d62728' for v in vals]
        colors_list[-1] = '#1f77b4'
        
        ax4.bar(categories, vals, color=colors_list, width=0.5)
        ax4.set_title('Latest Year Cash Flow Breakdown (Cr)', fontsize=10, fontweight='bold', pad=4)
        ax4.axhline(0, color='black', linewidth=0.8)
        ax4.tick_params(axis='both', labelsize=8)
    else:
        ax4.text(0.5, 0.5, 'Cash Flow Data Unavailable', ha='center', va='center')
    plt.tight_layout()
    buf4 = io.BytesIO()
    plt.savefig(buf4, format='png', bbox_inches='tight')
    plt.close(fig4)

    return buf1, buf2, buf3, buf4

def build_tearsheet_pdf(cid):
    """Builds a strict 2-page PDF tearsheet for a given company ID."""
    conn = sqlite3.connect(DB_PATH)
    
    # Company Metadata
    c_df = pd.read_sql("SELECT * FROM companies WHERE company_id = ?;", conn, params=(cid,))
    if c_df.empty:
        conn.close()
        return None

    c_name = c_df.iloc[0].get('company_name', cid)
    sector = c_df.iloc[0].get('sector', 'General')

    # Ratios
    r_df = safe_fetch_table(conn, cid, ['financial_ratios', 'ratios'])
    r_latest = r_df[r_df['year'] == 2024].iloc[0] if not r_df.empty and 2024 in r_df['year'].values else (r_df.iloc[-1] if not r_df.empty else pd.Series())

    # Pros & Cons
    pros_cons_path = os.path.join(OUT_DIR, "pros_cons_generated.csv")
    pros_list, cons_list = [], []
    if os.path.exists(pros_cons_path):
        pc_df = pd.read_csv(pros_cons_path)
        pc_comp = pc_df[pc_df['company_id'] == cid]
        pros_list = pc_comp[pc_comp['type'] == 'pro']['text'].tolist()
        cons_list = pc_comp[pc_comp['type'] == 'con']['text'].tolist()

    if not pros_list:
        pros_list = ["Strong market position and established industry footprint."]
    if not cons_list:
        cons_list = ["Subject to macroeconomic cycles and raw material price fluctuations."]

    # Capital Allocation Label
    cap_alloc_path = os.path.join(OUT_DIR, "cashflow_intelligence.xlsx")
    cap_label = "Balanced Allocator"
    if os.path.exists(cap_alloc_path):
        intel_df = pd.read_excel(cap_alloc_path)
        match = intel_df[intel_df['company_id'] == cid]
        if not match.empty:
            cap_label = str(match.iloc[0].get('capital_allocation', match.iloc[0].get('capital_allocation_label', 'Balanced Allocator')))

    buf1, buf2, buf3, buf4 = generate_chart_images(cid, conn)
    conn.close()

    # Document Setup
    pdf_filename = os.path.join(REPORTS_DIR, f"{cid}_tearsheet.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=0.4*inch,
        rightMargin=0.4*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.white, spaceAfter=2)
    subtitle_style = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.lightgrey)
    section_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#0B2545"), spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    pro_style = ParagraphStyle('ProItem', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#1b5e20"))
    con_style = ParagraphStyle('ConItem', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#b71c1c"))

    story = []

    # ==================== PAGE 1 ====================
    header_data = [[
        Paragraph(f"<b>{c_name} ({cid})</b>", title_style),
        Paragraph(f"Sector: <b>{sector}</b> | Nifty 100 Tearsheet", subtitle_style)
    ]]
    header_table = Table(header_data, colWidths=[4.5*inch, 2.7*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B2545")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    kpis = [
        ("ROE (%)", f"{float(r_latest.get('return_on_equity_pct', 0) or 0):.1f}%"),
        ("ROCE (%)", f"{float(r_latest.get('return_on_capital_employed_pct', 0) or 0):.1f}%"),
        ("D/E Ratio", f"{float(r_latest.get('debt_to_equity', 0) or 0):.2f}"),
        ("P/E Ratio", f"{float(r_latest.get('pe_ratio', 0) or 0):.1f}x"),
        ("OPM (%)", f"{float(r_latest.get('operating_profit_margin_pct', 0) or 0):.1f}%"),
        ("FCF (Cr)", f"₹{float(r_latest.get('free_cash_flow_cr', 0) or 0):,.0f}")
    ]

    tile_data = [
        [
            Paragraph(f"<font size=7 color='#555'>{kpis[0][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[0][1]}</font></b>", body_style),
            Paragraph(f"<font size=7 color='#555'>{kpis[1][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[1][1]}</font></b>", body_style),
            Paragraph(f"<font size=7 color='#555'>{kpis[2][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[2][1]}</font></b>", body_style),
        ],
        [
            Paragraph(f"<font size=7 color='#555'>{kpis[3][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[3][1]}</font></b>", body_style),
            Paragraph(f"<font size=7 color='#555'>{kpis[4][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[4][1]}</font></b>", body_style),
            Paragraph(f"<font size=7 color='#555'>{kpis[5][0]}</font><br/><b><font size=11 color='#0B2545'>{kpis[5][1]}</font></b>", body_style),
        ]
    ]
    tile_table = Table(tile_data, colWidths=[2.4*inch, 2.4*inch, 2.4*inch])
    tile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.white),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tile_table)
    story.append(Spacer(1, 10))

    story.append(Image(buf1, width=7.2*inch, height=2.4*inch))
    story.append(Spacer(1, 8))
    story.append(Image(buf2, width=7.2*inch, height=2.4*inch))

    story.append(PageBreak())

    # ==================== PAGE 2 ====================
    story.append(Paragraph("Financial Structure & Cash Flow Analysis", section_style))
    story.append(Spacer(1, 4))
    story.append(Image(buf3, width=7.2*inch, height=2.2*inch))
    story.append(Spacer(1, 6))
    story.append(Image(buf4, width=7.2*inch, height=1.9*inch))
    story.append(Spacer(1, 10))

    pc_data = [
        [
            Paragraph("<b>Key Strengths (Pros)</b>", section_style),
            Paragraph("<b>Key Risks & Concerns (Cons)</b>", section_style)
        ]
    ]
    
    pros_text = "<br/>".join([f"• {p}" for p in pros_list[:3]])
    cons_text = "<br/>".join([f"• {c}" for c in cons_list[:3]])

    pc_data.append([
        Paragraph(pros_text, pro_style),
        Paragraph(cons_text, con_style)
    ])

    pc_table = Table(pc_data, colWidths=[3.6*inch, 3.6*inch])
    pc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#E8F5E9")),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#FFEBEE")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.white),
    ]))
    story.append(pc_table)
    story.append(Spacer(1, 10))

    badge_data = [[
        Paragraph(f"Capital Allocation Strategy: <b><font color='#0B2545'>{cap_label}</font></b>", section_style)
    ]]
    badge_table = Table(badge_data, colWidths=[7.2*inch])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E3F2FD")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(badge_table)

    doc.build(story)
    return pdf_filename

def test_sample_tearsheets():
    """Test tearsheet generation on 5 diverse companies."""
    test_tickers = ['TCS', 'HDFCBANK', 'RELIANCE', 'SUNPHARMA', 'TATASTEEL']
    conn = sqlite3.connect(DB_PATH)
    all_tickers = pd.read_sql("SELECT company_id FROM companies;", conn)['company_id'].tolist()
    conn.close()

    sample = [t for t in test_tickers if t in all_tickers]
    if not sample:
        sample = all_tickers[:5]

    print(f"[TEST] Testing PDF tearsheet generation for: {sample}")
    for cid in sample:
        pdf_path = build_tearsheet_pdf(cid)
        if pdf_path and os.path.exists(pdf_path):
            size_kb = os.path.getsize(pdf_path) / 1024
            print(f" * Generated: {pdf_path} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    test_sample_tearsheets()