"""
N100 Platform - Streamlit Company Profile Screen
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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.dashboard.utils.db import get_companies, get_ratios, get_pl
st.set_page_config(page_title="Company Profile - Nifty 100", layout="wide")
st.title("🏢 Company Deep-Dive Profile")

# Load Companies Master
df_comps = get_companies()

if df_comps.empty:
    st.error("Company database unavailable.")
else:
    # 1. Search Box / Autocomplete Dropdown
    ticker_list = df_comps['company_id'].dropna().unique().tolist()
    selected_ticker = st.selectbox("Search / Select Company Ticker", options=ticker_list, index=0)

    # Fetch Specific Company Data
    comp_info = df_comps[df_comps['company_id'] == selected_ticker]

    if comp_info.empty:
        st.warning("Ticker not found — please try another")
    else:
        c_row = comp_info.iloc[0]
        c_name = c_row.get('company_name', selected_ticker)
        c_sec = c_row.get('sector', 'General')
        c_sub = c_row.get('sub_sector', 'N/A')

        # 2. Company Card
        st.markdown(f"### **{c_name}** (`{selected_ticker}`)")
        st.caption(f"**Sector:** {c_sec} | **Sub-Sector:** {c_sub}")
        st.write("Leading Nifty 100 constituent tracking core financial performance metrics and historical performance trends.")
        st.markdown("---")

        # Fetch Ratios & Financials
        df_r = get_ratios(ticker=selected_ticker)
        
        if not df_r.empty:
            latest_r = df_r.sort_values('year').iloc[-1]

            # 3. 6 KPI Tiles
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("ROE", f"{latest_r.get('return_on_equity_pct', 0):.2f}%")
            col2.metric("ROCE", f"{latest_r.get('return_on_capital_employed_pct', 0):.2f}%")
            col3.metric("Net Profit Margin", f"{latest_r.get('net_profit_margin_pct', 0):.2f}%")
            col4.metric("D/E", f"{latest_r.get('debt_to_equity', 0):.2f}")
            col5.metric("Revenue CAGR 5Y", f"{latest_r.get('revenue_cagr_5yr', 0):.2f}%")
            col6.metric("FCF (Latest)", f"₹{latest_r.get('free_cash_flow_cr', 0):.1f} Cr")

            st.markdown("---")

            # 4. 10-Year Historical Charts Layout
            ch1, ch2 = st.columns(2)

            # Revenue & Profit Bar Chart
            with ch1:
                st.subheader("10-Year Revenue & Net Profit Trend")
                df_pl = get_pl(ticker=selected_ticker)
                if not df_pl.empty and 'revenue' in df_pl.columns and 'net_profit' in df_pl.columns:
                    fig_bar = px.bar(df_pl.sort_values('year'), x='year', y=['revenue', 'net_profit'],
                                     barmode='group', labels={'value': 'Crores (₹)', 'year': 'Year'},
                                     title="Revenue vs Net Profit")
                    fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Historical P&L data unavailable for chart.")

            # Dual Axis Line Chart for ROE & ROCE
            with ch2:
                st.subheader("ROE & ROCE Trajectory")
                df_r_sorted = df_r.sort_values('year')
                fig_line = make_subplots(specs=[[{"secondary_y": True}]])
                fig_line.add_trace(go.Scatter(x=df_r_sorted['year'], y=df_r_sorted.get('return_on_equity_pct', [0]), name="ROE (%)", mode='lines+markers'), secondary_y=False)
                fig_line.add_trace(go.Scatter(x=df_r_sorted['year'], y=df_r_sorted.get('return_on_capital_employed_pct', [0]), name="ROCE (%)", mode='lines+markers', line=dict(dash='dash')), secondary_y=True)
                fig_line.update_layout(title_text="ROE vs ROCE (%) Over Time", margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_line, use_container_width=True)

            # 5. Pros & Cons Badges
            st.markdown("### 🟢 Pros & 🔴 Cons Analysis")
            p_col, c_col = st.columns(2)
            
            de_val = latest_r.get('debt_to_equity', 0)
            roe_val = latest_r.get('return_on_equity_pct', 0)

            with p_col:
                if roe_val > 15:
                    st.success("✅ Strong return on equity (ROE > 15%)")
                if de_val < 0.5:
                    st.success("✅ Healthy low-debt balance sheet (D/E < 0.5)")
                st.success("✅ Part of premier Nifty 100 universe")

            with c_col:
                if de_val > 1.5:
                    st.error("❌ Higher financial leverage (D/E > 1.5)")
                if roe_val < 10:
                    st.error("❌ Subdued profitability (ROE < 10%)")
                st.error("❌ Subject to sector-wide macroeconomic volatility")