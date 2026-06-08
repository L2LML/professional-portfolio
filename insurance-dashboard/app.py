"""
app.py — Executive Summary dashboard page.
Entry point for the Insurance Claims BI Dashboard.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact
from data.colors import STATUS_COLORS, BLUE, NAVY, GRID, RISK_SCALE

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Insurance Claims Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ────────────────────────────────────────────────────
st.title("🏦 Insurance Claims Dashboard")
st.caption("Life Insurance Operations · Built with PostgreSQL → Python ETL → Streamlit")
st.divider()

# ── Load data ─────────────────────────────────────────────────
df = load_claims_fact()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")
years = sorted(df["claim_year"].dropna().unique().tolist())
sel_years = st.sidebar.multiselect("Year Filed", years, default=years)

pol_types = sorted(df["policy_type"].dropna().unique().tolist())
sel_types = st.sidebar.multiselect("Policy Type", pol_types, default=pol_types)

states = sorted(df["address_state"].dropna().unique().tolist())
sel_states = st.sidebar.multiselect("State", states, default=states)

filtered = df[
    df["claim_year"].isin(sel_years) &
    df["policy_type"].isin(sel_types) &
    df["address_state"].isin(sel_states)
]

st.sidebar.divider()
st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(df):,} claims")

# ── KPI Cards ─────────────────────────────────────────────────
total_claims   = len(filtered)
total_payouts  = filtered[filtered["claim_status"] == "paid"]["claim_amount"].sum()
denial_rate    = (filtered["claim_status"] == "denied").sum() / max(len(filtered), 1) * 100
avg_processing = filtered["days_to_decision"].dropna().mean()
open_claims    = (filtered["claim_status"].isin(["pending","under_review"])).sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Claims",      f"{total_claims:,}")
c2.metric("Total Paid Out",    f"${total_payouts/1_000_000:.2f}M")
c3.metric("Denial Rate",       f"{denial_rate:.1f}%")
c4.metric("Avg Decision Time", f"{avg_processing:.0f} days" if pd.notna(avg_processing) else "—")
c5.metric("Open Claims",       f"{open_claims:,}")

st.divider()

# ── Charts row ────────────────────────────────────────────────
left, right = st.columns([1, 2])

# Claims by status — donut
with left:
    st.subheader("Claims by Status")
    status_counts = filtered["claim_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    COLOR_MAP = STATUS_COLORS
    fig_donut = px.pie(
        status_counts, values="Count", names="Status",
        hole=0.55,
        color="Status",
        color_discrete_map=COLOR_MAP,
    )
    fig_donut.update_traces(textposition="outside", textinfo="percent+label")
    fig_donut.update_layout(
        showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
        height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Monthly trend — line
with right:
    st.subheader("Monthly Claims Filed")
    monthly = (
        filtered.groupby(["claim_year","claim_month"])
        .agg(count=("claim_id","count"), value=("claim_amount","sum"))
        .reset_index()
    )
    monthly["date"] = pd.to_datetime(monthly[["claim_year","claim_month"]].rename(
        columns={"claim_year":"year","claim_month":"month"}
    ).assign(day=1))
    monthly = monthly.sort_values("date").tail(30)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly["date"], y=monthly["count"],
        fill="tozeroy", fillcolor="rgba(2,132,199,0.15)",
        line=dict(color=BLUE, width=2.5),
        name="Claims Filed",
    ))
    fig_line.update_layout(
        height=320, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"),
        showlegend=False,
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ── Open high-value claims table ──────────────────────────────
st.subheader("⚠️ Open High-Value Claims (> $250K)")
high_open = filtered[
    filtered["claim_status"].isin(["pending","under_review"]) &
    (filtered["claim_amount"] > 250_000)
][["claim_number","claim_status","policyholder_name","policy_type",
   "cause_of_death","claim_amount","date_filed","days_open","aging_flag",
   "assigned_examiner"]].sort_values("claim_amount", ascending=False)

if high_open.empty:
    st.success("No open high-value claims matching current filters.")
else:
    st.dataframe(
        high_open.rename(columns={
            "claim_number":"Claim #", "claim_status":"Status",
            "policyholder_name":"Policyholder", "policy_type":"Product",
            "cause_of_death":"Cause", "claim_amount":"Amount",
            "date_filed":"Filed", "days_open":"Days Open",
            "aging_flag":"Aging", "assigned_examiner":"Examiner"
        }).style.format({"Amount": "${:,.0f}", "Days Open": "{:.0f}"}),
        use_container_width=True, hide_index=True,
    )
