"""
N100 Platform - Streamlit Annual Reports Screen
Day 25 Implementation
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_companies

st.set_page_config(page_title="Annual Reports - Nifty 100", layout="wide")
st.title("📄 Annual Reports & Regulatory Filings")

df_comps = get_companies()

if df_comps.empty:
    st.error("Companies master unavailable.")
else:
    ticker_list = df_comps['company_id'].dropna().unique().tolist()
    selected_ticker = st.selectbox("Search / Select Ticker for Filings", options=ticker_list, index=0)

    st.subheader(f"Available Filings & Annual Reports for `{selected_ticker}`")

    years = [2024, 2023, 2022, 2021, 2020]

    for yr in years:
        col1, col2, col3 = st.columns([1, 2, 2])
        col1.write(f"**FY {yr}**")
        col2.write(f"{selected_ticker} Annual Report {yr}")
        
        # Simulated BSE PDF link checking
        if yr in [2024, 2023, 2022]:
            bse_url = f"https://www.bseindia.com/bseplus/AnnualReport/{selected_ticker}_{yr}.pdf"
            col3.markdown(f"[🔗 View / Download PDF ({yr})]({bse_url})")
        else:
            col3.error("🔴 Report unavailable")