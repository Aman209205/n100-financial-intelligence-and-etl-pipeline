"""
N100 Platform - Streamlit Trend Analysis Screen
Day 25 Implementation
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_companies, get_ratios

st.set_page_config(page_title="Trend Analysis - Nifty 100", layout="wide")
st.title("📈 Multi-Metric Financial Trend Analysis")

df_comps = get_companies()

if df_comps.empty:
    st.error("Companies database unavailable.")
else:
    ticker_list = df_comps['company_id'].dropna().unique().tolist()
    selected_ticker = st.selectbox("Select Company Ticker", options=ticker_list, index=0)

    df_ratios = get_ratios(ticker=selected_ticker)

    if df_ratios.empty:
        st.info("No historical ratio trends found for this ticker.")
    else:
        df_ratios_sorted = df_ratios.sort_values('year')

        numeric_cols = [c for c in df_ratios_sorted.select_dtypes(include=['float64', 'int64']).columns if c != 'year']
        selected_metrics = st.multiselect("Select Up to 3 Metrics to Overlay", options=numeric_cols, default=numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols, max_selections=3)

        if not selected_metrics:
            st.warning("Please select at least one metric to plot.")
        else:
            fig = px.line(df_ratios_sorted, x='year', y=selected_metrics, markers=True, title=f"Historical Trend Overlay for {selected_ticker}")
            fig.update_layout(xaxis=dict(dtick=1), yaxis_title="Metric Value", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # Data Table
            st.subheader("Historical Data Table")
            st.dataframe(df_ratios_sorted[['year'] + selected_metrics], hide_index=True, use_container_width=True)