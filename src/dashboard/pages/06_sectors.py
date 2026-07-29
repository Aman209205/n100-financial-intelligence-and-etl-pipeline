"""
N100 Platform - Streamlit Sector Analysis Screen
Day 25 Implementation (Fixed Market Cap Fallback)
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_companies

st.set_page_config(page_title="Sector Analysis - Nifty 100", layout="wide")
st.title("🏭 Sector-Wide Multi-Dimensional Analysis")

df_ratios = get_ratios(year=2024)

if df_ratios.empty:
    st.error("Financial ratio data unavailable.")
else:
    sectors = df_ratios['sector'].dropna().unique().tolist() if 'sector' in df_ratios.columns else []
    
    if not sectors:
        st.info("No sector data found.")
    else:
        selected_sector = st.selectbox("Select Broad Sector", options=sectors, index=0)

        sec_df = df_ratios[df_ratios['sector'] == selected_sector].copy()

        if sec_df.empty:
            st.info("No companies found in selected sector.")
        else:
            # Safe Market Cap Series Fallback
            if 'market_cap' in sec_df.columns:
                sec_df['market_cap'] = sec_df['market_cap'].fillna(10000.0)
            else:
                sec_df['market_cap'] = 10000.0

            if 'sub_sector' not in sec_df.columns:
                sec_df['sub_sector'] = 'General'

            st.subheader(f"Bubble Analysis: Revenue vs ROE ({selected_sector})")
            
            x_col = 'revenue_cagr_5yr' if 'revenue_cagr_5yr' in sec_df.columns else ('net_profit_margin_pct' if 'net_profit_margin_pct' in sec_df.columns else 'company_id')

            fig_bubble = px.scatter(
                sec_df,
                x=x_col,
                y='return_on_equity_pct' if 'return_on_equity_pct' in sec_df.columns else sec_df.columns[0],
                size='market_cap',
                color='sub_sector',
                hover_name='company_id',
                labels={'return_on_equity_pct': 'ROE (%)', 'revenue_cagr_5yr': 'Revenue CAGR 5Y (%)'},
                title="X: Growth / Margin | Y: ROE | Size: Market Cap"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

            st.markdown("---")
            st.subheader("Sector Median KPIs Benchmark")
            
            kpi_cols = [c for c in ['return_on_equity_pct', 'net_profit_margin_pct', 'debt_to_equity', 'operating_profit_margin_pct'] if c in sec_df.columns]
            if kpi_cols:
                medians = sec_df[kpi_cols].median().reset_index()
                medians.columns = ['Metric', 'Sector Median Value']

                fig_bar = px.bar(medians, x='Metric', y='Sector Median Value', title=f"Median KPI Benchmark for {selected_sector}", color='Metric')
                st.plotly_chart(fig_bar, use_container_width=True)