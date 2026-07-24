"""load_data.py — Cached parquet loaders shared by every page."""

from pathlib import Path
import pandas as pd
import streamlit as st

SAMPLE_DIR = Path(__file__).parent / "sample"


@st.cache_data
def load_projects():
    return pd.read_parquet(SAMPLE_DIR / "projects.parquet")


@st.cache_data
def load_schedule():
    return pd.read_parquet(SAMPLE_DIR / "schedule.parquet")


@st.cache_data
def load_milestones():
    return pd.read_parquet(SAMPLE_DIR / "milestones.parquet")


@st.cache_data
def load_budget():
    return pd.read_parquet(SAMPLE_DIR / "budget.parquet")


@st.cache_data
def load_risks():
    return pd.read_parquet(SAMPLE_DIR / "risks.parquet")


@st.cache_data
def load_issues():
    return pd.read_parquet(SAMPLE_DIR / "issues.parquet")


@st.cache_data
def load_vendors():
    return pd.read_parquet(SAMPLE_DIR / "vendors.parquet")


@st.cache_data
def load_stakeholders():
    return pd.read_parquet(SAMPLE_DIR / "stakeholders.parquet")


@st.cache_data
def load_monthly_progress():
    return pd.read_parquet(SAMPLE_DIR / "monthly_progress.parquet")


@st.cache_data
def load_quality():
    return pd.read_parquet(SAMPLE_DIR / "quality.parquet")


@st.cache_data
def load_final_summary():
    return pd.read_parquet(SAMPLE_DIR / "final_summary.parquet")


@st.cache_data
def load_lessons_learned():
    return pd.read_parquet(SAMPLE_DIR / "lessons_learned.parquet")
