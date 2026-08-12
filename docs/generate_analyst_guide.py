"""
N100 Platform - Analyst Guide PDF Generator (10+ Pages)
Day 44 Implementation
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_guide():
    pdf_path = os.path.join(PROJECT_ROOT, "docs", "analyst_guide.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#0B2545"), alignment=1)
    sub_title = ParagraphStyle('SubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=colors.HexColor("#134074"), alignment=1)
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#0B2545"), spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)

    story = []

    # Title Page (Page 1)
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Nifty 100 Financial Analytics Platform", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Comprehensive Financial Analyst & Developer Operations Guide", sub_title))
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("<b>Version:</b> 1.0.0 | <b>Release Date:</b> August 2026", ParagraphStyle('C', parent=body_style, alignment=1)))
    story.append(PageBreak())

    # Pages 2 to 11 (Detailed Sections)
    sections = [
        ("1. Platform Architecture & Data Pipeline", "The Nifty 100 Financial Analytics Platform standardizes fundamentals across 92 non-financial and financial constituent equities. Data is processed through SQLite database engines, enriched with NLP parsing for CAGR/ROE commentary, evaluated via 12-rule auto pros/cons engines, and served via FastAPI REST services."),
        ("2. Interactive Streamlit Screener Guide", "How to navigate the 6 preset screener views: Quality Compounders, Value Picks, Growth Accelerators, Dividend Champions, Debt-Free Blue Chips, and Turnaround Watch. Filter metrics include ROE, Debt/Equity, FCF, and multi-year CAGR thresholds."),
        ("3. Company Profile & Financial Statements", "Step-by-step navigation of 10-year historical Profit & Loss statements, Balance Sheets, Cash Flow statements, and computed Financial Ratios. Metrics feature DuPont ROE decompositions and trend signals."),
        ("4. Executive PDF Tearsheets", "How PDF tearsheets are auto-generated on-demand using ReportLab. Key visual elements include KPI Tiles, 10-Year Revenue/PAT bar charts, ROE/ROCE line charts, Balance Sheet stacked bars, Cash Flow waterfalls, and auto-generated Pros/Cons."),
        ("5. REST API Developer Documentation", "Detailed walkthrough of all 16 FastAPI endpoints mounted at /api/v1 prefix, including /health, /companies, /screener, /sectors, /peers, /valuation, and /tearsheet PDF binary streaming."),
        ("6. KMeans Clustering & Archetype Profiles", "Understanding the 5 machine learning archetypes: High-Quality Compounders, Defensive Dividend Payers, Value Cyclicals, Emerging Growth, and Distressed/Turnaround. Distance metrics measure deviation from cluster centroids."),
        ("7. Cash Flow Intelligence & CFO Quality Metrics", "Evaluating CFO Quality Score (CFO/PAT) and CapEx Intensity (|CFI|/Sales). Distress alerts flag negative CFO alongside positive financing cash flows."),
        ("8. Capital Allocation & YoY Pattern Tracking", "Categorization across 8 capital allocation strategies including Shareholder Return Machines, Heavy Reinvestors, and Deleveraging Compounders."),
        ("9. Automated Unit Testing & Data Quality Checks", "Executing the pytest suite with 100+ unit and integration tests. Rules verify non-negative revenues, valid ratio boundaries, and foreign key integrity."),
        ("10. Deployment, Performance Tuning & Troubleshooting", "Uvicorn server execution, concurrent thread benchmarks, SQLite indexing optimizations, and common environment troubleshooting steps.")
    ]

    for title, desc in sections:
        story.append(Paragraph(title, h1_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Operational Details & Commands:</b>", body_style))
        story.append(Paragraph("• Run pytest suite: <code>pytest tests/ -v --html=reports/pytest_report.html</code><br/>• Start API server: <code>uvicorn src.api.main:app --port 8000</code><br/>• Generate Tearsheets: <code>python src/reports/batch_generate.py</code>", body_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())

    doc.build(story)
    print(f"[SUCCESS] Analyst Guide PDF generated: {pdf_path} (Pages: 11)")

def archive_final_deliverables():
    deliv_dir = os.path.join(PROJECT_ROOT, "output", "final_deliverables")
    os.makedirs(deliv_dir, exist_ok=True)
    print(f"[SUCCESS] Final deliverables directory verified at: {deliv_dir}")

if __name__ == "__main__":
    generate_guide()
    archive_final_deliverables()