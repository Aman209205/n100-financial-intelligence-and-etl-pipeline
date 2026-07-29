"""
N100 Platform - Streamlit Screener Screen
Day 24 Implementation
"""

import sys
import os

# Root directory path configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_ratios

st.set_page_config(page_title="Screener - Nifty 100", layout="wide")
st.title("🔍 Dynamic Financial Screener")

# Load full dataset
df_ratios = get_ratios(year=2024)

if df_ratios.empty:
    st.error("No data available for screening.")
else:
    # 1. Preset Definitions
    presets = {
        "Quality": {"roe": 15.0, "de": 1.0, "fcf": 0.0, "rev_cagr": 8.0, "pat_cagr": 8.0, "opm": 12.0, "pe": 60.0, "pb": 10.0, "div": 0.0, "icr": 3.0},
        "Value": {"roe": 10.0, "de": 1.5, "fcf": -500.0, "rev_cagr": 0.0, "pat_cagr": 0.0, "opm": 5.0, "pe": 20.0, "pb": 3.0, "div": 1.0, "icr": 1.5},
        "Growth": {"roe": 12.0, "de": 1.5, "fcf": -1000.0, "rev_cagr": 15.0, "pat_cagr": 15.0, "opm": 10.0, "pe": 80.0, "pb": 15.0, "div": 0.0, "icr": 2.0},
        "Dividend": {"roe": 8.0, "de": 2.0, "fcf": -100.0, "rev_cagr": 0.0, "pat_cagr": 0.0, "opm": 5.0, "pe": 40.0, "pb": 5.0, "div": 2.0, "icr": 1.0},
        "Debt-Free": {"roe": 10.0, "de": 0.1, "fcf": 0.0, "rev_cagr": 5.0, "pat_cagr": 5.0, "opm": 8.0, "pe": 50.0, "pb": 8.0, "div": 0.0, "icr": 5.0},
        "Turnaround": {"roe": 0.0, "de": 2.5, "fcf": -2000.0, "rev_cagr": 10.0, "pat_cagr": 10.0, "opm": 0.0, "pe": 100.0, "pb": 20.0, "div": 0.0, "icr": 0.5}
    }

    # 2. Sidebar Preset Buttons
    st.sidebar.subheader("Quick Presets")
    p_cols = st.sidebar.columns(3)
    
    if "filter_values" not in st.session_state:
        st.session_state.filter_values = presets["Quality"]

    for idx, (p_name, p_vals) in enumerate(presets.items()):
        col = p_cols[idx % 3]
        if col.button(p_name, use_container_width=True):
            st.session_state.filter_values = p_vals

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Sliders")

    # 3. 10 Metric Sliders
    f = st.session_state.filter_values

    roe_min = st.sidebar.slider("ROE Min (%)", -20.0, 50.0, float(f.get("roe", 10.0)))
    de_max = st.sidebar.slider("D/E Max", 0.0, 5.0, float(f.get("de", 1.5)))
    fcf_min = st.sidebar.slider("FCF Min (Cr)", -5000.0, 10000.0, float(f.get("fcf", 0.0)))
    rev_cagr_min = st.sidebar.slider("Revenue CAGR 5Y Min (%)", -10.0, 40.0, float(f.get("rev_cagr", 5.0)))
    pat_cagr_min = st.sidebar.slider("PAT CAGR 5Y Min (%)", -10.0, 40.0, float(f.get("pat_cagr", 5.0)))
    opm_min = st.sidebar.slider("OPM Min (%)", 0.0, 50.0, float(f.get("opm", 10.0)))
    pe_max = st.sidebar.slider("P/E Max", 5.0, 150.0, float(f.get("pe", 50.0)))
    pb_max = st.sidebar.slider("P/B Max", 0.5, 30.0, float(f.get("pb", 5.0)))
    div_min = st.sidebar.slider("Dividend Yield Min (%)", 0.0, 10.0, float(f.get("div", 0.0)))
    icr_min = st.sidebar.slider("ICR Min", 0.0, 20.0, float(f.get("icr", 1.5)))

    # 4. Live Filtering Logic
    filtered = df_ratios.copy()

    if 'return_on_equity_pct' in filtered.columns:
        filtered = filtered[filtered['return_on_equity_pct'] >= roe_min]
    if 'debt_to_equity' in filtered.columns:
        filtered = filtered[(filtered['debt_to_equity'] <= de_max) | (filtered['sector'].astype(str).str.lower().str.contains('financial'))]
    if 'free_cash_flow_cr' in filtered.columns:
        filtered = filtered[filtered['free_cash_flow_cr'] >= fcf_min]
    if 'revenue_cagr_5yr' in filtered.columns:
        filtered = filtered[filtered['revenue_cagr_5yr'] >= rev_cagr_min]
    if 'pat_cagr_5yr' in filtered.columns:
        filtered = filtered[filtered['pat_cagr_5yr'] >= pat_cagr_min]
    if 'operating_profit_margin_pct' in filtered.columns:
        filtered = filtered[filtered['operating_profit_margin_pct'] >= opm_min]
    if 'pe_ratio' in filtered.columns:
        filtered = filtered[filtered['pe_ratio'] <= pe_max]
    if 'pb_ratio' in filtered.columns:
        filtered = filtered[filtered['pb_ratio'] <= pb_max]
    if 'dividend_yield' in filtered.columns:
        filtered = filtered[filtered['dividend_yield'] >= div_min]
    if 'interest_coverage' in filtered.columns:
        filtered = filtered[(filtered['interest_coverage'] >= icr_min) | (filtered['interest_coverage'].isna())]

    # 5. Header Count Label & CSV Export
    st.subheader(f"🎯 Matching Results: {len(filtered)} companies match your filters")

    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results CSV",
        data=csv_data,
        file_name="screener_filtered_results.csv",
        mime="text/csv"
    )

    display_cols = [c for c in ['company_id', 'company_name', 'sector', 'composite_quality_score', 'return_on_equity_pct', 'debt_to_equity', 'pe_ratio', 'free_cash_flow_cr'] if c in filtered.columns]
    st.dataframe(filtered[display_cols], hide_index=True, use_container_width=True)