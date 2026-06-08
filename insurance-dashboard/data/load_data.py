"""
load_data.py — Load dashboard data from sample Parquet files.
Cached with Streamlit so data loads once per session.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

SAMPLE_DIR = Path(__file__).parent / "sample"

@st.cache_data
def load_claims_fact() -> pd.DataFrame:
    df = pd.read_parquet(SAMPLE_DIR / "claims_fact.parquet")
    for col in ["date_filed", "date_of_death", "date_approved", "date_denied", "date_paid",
                "issue_date", "date_of_birth", "policyholder_since"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

@st.cache_data
def load_policies() -> pd.DataFrame:
    df = pd.read_parquet(SAMPLE_DIR / "policies.parquet")
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
    return df

@st.cache_data
def load_policyholders() -> pd.DataFrame:
    df = pd.read_parquet(SAMPLE_DIR / "policyholders.parquet")
    df["policyholder_since"] = pd.to_datetime(df["policyholder_since"], errors="coerce")
    return df

@st.cache_data
def load_agents() -> pd.DataFrame:
    return pd.read_parquet(SAMPLE_DIR / "agents.parquet")
