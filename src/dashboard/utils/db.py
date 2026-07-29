"""
N100 Platform - Streamlit Cached Database Utility
Day 22 Implementation
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM companies;", conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    conn = get_connection()
    query = "SELECT f.*, c.company_name, c.sector FROM financial_ratios f JOIN companies c ON f.company_id = c.company_id"
    conditions = []
    if ticker:
        conditions.append(f"f.company_id = '{ticker}'")
    if year:
        conditions.append(f"f.year = {year}")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_pl(ticker=None):
    conn = get_connection()
    query = "SELECT * FROM profit_loss"
    if ticker:
        query += f" WHERE company_id = '{ticker}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_bs(ticker=None):
    conn = get_connection()
    query = "SELECT * FROM balance_sheet"
    if ticker:
        query += f" WHERE company_id = '{ticker}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_cf(ticker=None):
    conn = get_connection()
    query = "SELECT * FROM cash_flow"
    if ticker:
        query += f" WHERE company_id = '{ticker}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_sectors():
    df = get_companies()
    if 'sector' in df.columns:
        return df['sector'].dropna().unique().tolist()
    return []

@st.cache_data(ttl=600)
def get_peers(group_name):
    conn = get_connection()
    query = f"SELECT * FROM peer_percentiles WHERE peer_group_name = '{group_name}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_valuation(ticker=None):
    conn = get_connection()
    query = "SELECT * FROM companies"
    if ticker:
        query += f" WHERE company_id = '{ticker}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df