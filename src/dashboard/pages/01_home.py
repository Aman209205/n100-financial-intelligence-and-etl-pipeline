"""
N100 Platform - Streamlit Home Screen
Day 23 Implementation
"""

import sys
import os

# Root directory path configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_companies

st.set_page_config(page_title="Home - Nifty 100", layout="wide")
st.title("📊 Nifty 100 Overview Dashboard")

# 1. Sidebar Year Selector
year_selected = st.sidebar.selectbox("Select Financial Year", options=[2024, 2023, 2022, 2021, 2020, 2019], index=0)

# Fetch Data
df_ratios = get_ratios(year=year_selected)
df_companies = get_companies()

if df_ratios.empty:
    st.warning(f"No financial data available for year {year_selected}")
else:
    # 2. Compute 6 KPI Metrics
    avg_roe = df_ratios['return_on_equity_pct'].mean() if 'return_on_equity_pct' in df_ratios.columns else 0.0
    med_pe = df_ratios['pe_ratio'].median() if 'pe_ratio' in df_ratios.columns else 0.0
    med_de = df_ratios['debt_to_equity'].median() if 'debt_to_equity' in df_ratios.columns else 0.0
    total_comps = len(df_ratios['company_id'].unique())
    med_rev_cagr = df_ratios['revenue_cagr_5yr'].median() if 'revenue_cagr_5yr' in df_ratios.columns else 0.0
    
    if 'debt_to_equity' in df_ratios.columns:
        debt_free_count = (df_ratios['debt_to_equity'] == 0.0).sum()
    else:
        debt_free_count = 0

    # Display 6 KPI Tiles
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Avg ROE", f"{avg_roe:.2f}%")
    col2.metric("Median P/E", f"{med_pe:.2f}x")
    col3.metric("Median D/E", f"{med_de:.2f}")
    col4.metric("Total Companies", f"{total_comps}")
    col5.metric("Median Rev CAGR 5Y", f"{med_rev_cagr:.2f}%")
    col6.metric("Debt-Free Count", f"{debt_free_count}")

    st.markdown("---")

    # 3. Sector Breakdown Donut Chart & Top Companies Layout
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Sector Breakdown")
        if 'sector' in df_companies.columns:
            sec_counts = df_companies['sector'].value_counts().reset_index()
            sec_counts.columns = ['Sector', 'Count']
            fig_donut = px.pie(sec_counts, names='Sector', values='Count', hole=0.4, title="Company Distribution by Sector")
            fig_donut.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Sector details not available.")

    with c2:
        st.subheader("Top 5 Companies by Performance")
        score_col = 'composite_quality_score' if 'composite_quality_score' in df_ratios.columns else 'return_on_equity_pct'
        
        display_cols = [c for c in ['company_id', 'company_name', 'sector', score_col, 'return_on_equity_pct', 'debt_to_equity'] if c in df_ratios.columns]
        top_5 = df_ratios.sort_values(score_col, ascending=False).head(5)[display_cols]
        st.dataframe(top_5, hide_index=True, use_container_width=True)