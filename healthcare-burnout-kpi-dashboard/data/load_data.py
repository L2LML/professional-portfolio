"""load_data.py — Cached parquet loaders shared by every page."""

from pathlib import Path
import pandas as pd
import streamlit as st

SAMPLE_DIR = Path(__file__).parent / "sample"


@st.cache_data
def load_survey():
    return pd.read_parquet(SAMPLE_DIR / "survey_responses.parquet")


@st.cache_data
def load_adherence_log():
    return pd.read_parquet(SAMPLE_DIR / "adherence_log.parquet")


@st.cache_data
def load_initiatives():
    return pd.read_parquet(SAMPLE_DIR / "initiatives.parquet")
