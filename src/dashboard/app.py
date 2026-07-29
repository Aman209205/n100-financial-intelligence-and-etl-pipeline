"""
N100 Platform - Streamlit Main Entry Point
Day 22-25 Implementation
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Explicit Navigation setup for Streamlit
pages = {
    "Analytics Dashboard": [
        st.Page("pages/01_home.py", title="Home", icon="🏠"),
        st.Page("pages/02_profile.py", title="Company Profile", icon="🏢"),
        st.Page("pages/03_screener.py", title="Dynamic Screener", icon="🔍"),
        st.Page("pages/04_peers.py", title="Peer Comparison", icon="⚔️"),
        st.Page("pages/05_trends.py", title="Trend Analysis", icon="📈"),
        st.Page("pages/06_sectors.py", title="Sector Analysis", icon="🏭"),
        st.Page("pages/07_capital.py", title="Capital Allocation", icon="🗺️"),
        st.Page("pages/08_reports.py", title="Annual Reports", icon="📄"),
    ]
}

pg = st.navigation(pages)
pg.run()