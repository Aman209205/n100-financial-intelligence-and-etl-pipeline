"""
N100 Platform - Streamlit Peer Comparison Screen
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
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios

st.set_page_config(page_title="Peer Comparison - Nifty 100", layout="wide")
st.title("⚔️ Peer Comparison & Benchmarking")

df_comps = get_companies()

if df_comps.empty:
    st.error("Companies database unavailable.")
else:
    # 1. Peer Group Dropdown
    peer_groups = df_comps['sector'].dropna().unique().tolist()
    selected_group = st.selectbox("Select Peer Group Sector", options=peer_groups, index=0)

    df_ratios = get_ratios(year=2024)
    group_ratios = df_ratios[df_ratios['sector'] == selected_group]

    if group_ratios.empty:
        st.info("No companies found in selected peer group.")
    else:
        # Company Selector
        comp_list = group_ratios['company_id'].unique().tolist()
        selected_comp = st.selectbox("Select Target Company", options=comp_list, index=0)

        target_row = group_ratios[group_ratios['company_id'] == selected_comp].iloc[0]
        
        # 2. Polar Radar Chart (8 Metrics)
        radar_metrics = ['return_on_equity_pct', 'return_on_capital_employed_pct', 'net_profit_margin_pct', 'debt_to_equity', 'free_cash_flow_cr', 'pat_cagr_5yr', 'revenue_cagr_5yr', 'operating_profit_margin_pct']
        labels = ['ROE', 'ROCE', 'NPM', 'D/E', 'FCF', 'PAT CAGR', 'Rev CAGR', 'OPM']

        comp_vals = [float(target_row.get(m, 0) or 0) for m in radar_metrics]
        mean_vals = [float(group_ratios[m].mean() or 0) if m in group_ratios.columns else 0 for m in radar_metrics]

        # Normalize values to 0-100 scale for clean polar display
        comp_norm = [min(max((v + 50) / 2, 0), 100) for v in comp_vals]
        mean_norm = [min(max((v + 50) / 2, 0), 100) for v in mean_vals]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=comp_norm + [comp_norm[0]], theta=labels + [labels[0]], fill='toself', name=selected_comp))
        fig_radar.add_trace(go.Scatterpolar(r=mean_norm + [mean_norm[0]], theta=labels + [labels[0]], line=dict(dash='dash'), name=f"{selected_group} Avg"))

        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, title=f"{selected_comp} vs {selected_group} Peer Average")
        
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")
        # 3. Side-by-Side KPI Table
        st.subheader(f"Peer Group Comparison Table ({selected_group})")
        display_cols = [c for c in ['company_id', 'company_name', 'return_on_equity_pct', 'net_profit_margin_pct', 'debt_to_equity', 'free_cash_flow_cr', 'pe_ratio'] if c in group_ratios.columns]
        
        st.dataframe(group_ratios[display_cols], hide_index=True, use_container_width=True)