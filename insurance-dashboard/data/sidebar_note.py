"""
sidebar_note.py — Shared sidebar sample-data disclaimer.
Import and call show() at the top of every page.
"""
import streamlit as st

def show():
    st.sidebar.divider()
    st.sidebar.warning(
        "**⚠️ Sample Data**\n\n"
        "All figures are synthetically generated. "
        "No real claims, policyholders, or financials are shown."
    )
    st.sidebar.caption(
        "In production, this connects to the PostgreSQL "
        "claims database via the Python ETL pipeline.\n\n"
        "[View full portfolio →](https://github.com/L2LML/professional-portfolio)"
    )
