"""
N100 Platform - Streamlit Capital Allocation Map Screen
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
from src.dashboard.utils.db import get_ratios

st.set_page_config(page_title="Capital Allocation - Nifty 100", layout="wide")
st.title("🗺️ Capital Allocation Treemap")

df_ratios = get_ratios(year=2024)

if df_ratios.empty:
    st.error("No data available for capital allocation map.")
else:
    def classify_pattern(row):
        fcf = row.get('free_cash_flow_cr', 0) or 0
        roe = row.get('return_on_equity_pct', 0) or 0
        div = row.get('dividend_yield', 0) or 0
        de = row.get('debt_to_equity', 0) or 0

        if roe > 18 and fcf > 500:
            return "Cash Compounders"
        elif div > 2.0:
            return "High Dividend Payers"
        elif de < 0.2 and roe > 12:
            return "Conservative Reinvestors"
        elif de > 1.2:
            return "Leveraged Expansion"
        elif fcf < 0 and roe > 15:
            return "Aggressive Growth CapEx"
        elif roe < 8:
            return "Capital Preservers / Laggards"
        elif fcf > 0:
            return "Balanced Allocators"
        else:
            return "Restructuring Watch"

    df_ratios['capital_pattern'] = df_ratios.apply(classify_pattern, axis=1)

    # Safe Market Cap Series Fallback
    if 'market_cap' in df_ratios.columns:
        df_ratios['market_cap_sim'] = df_ratios['market_cap'].fillna(10000.0)
    else:
        df_ratios['market_cap_sim'] = 10000.0

    st.subheader("Nifty 100 Treemap by Allocation Pattern")
    fig_tree = px.treemap(
        df_ratios,
        path=['capital_pattern', 'company_id'],
        values='market_cap_sim',
        color='return_on_equity_pct' if 'return_on_equity_pct' in df_ratios.columns else None,
        color_continuous_scale='Viridis',
        title="Grouped by Capital Allocation Strategy (Size = Market Cap, Color = ROE)"
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")
    st.subheader("Filter Companies by Allocation Strategy")
    pattern_selected = st.selectbox("Select Capital Pattern", options=df_ratios['capital_pattern'].unique().tolist())
    
    filtered_p = df_ratios[df_ratios['capital_pattern'] == pattern_selected]
    display_cols = [c for c in ['company_id', 'company_name', 'sector', 'return_on_equity_pct', 'free_cash_flow_cr', 'debt_to_equity'] if c in filtered_p.columns]
    st.dataframe(filtered_p[display_cols], hide_index=True, use_container_width=True)