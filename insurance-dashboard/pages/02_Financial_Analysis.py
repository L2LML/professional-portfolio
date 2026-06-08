"""Financial Analysis — payouts, revenue vs exposure, running totals."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact, load_policies

st.set_page_config(page_title="Financial Analysis", page_icon="💰", layout="wide")
st.title("💰 Financial Analysis")
st.divider()

df  = load_claims_fact()
pol = load_policies()

paid = df[df["claim_status"] == "paid"]
approved = df[df["claim_status"].isin(["paid","approved"])]

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Paid",       f"${paid['claim_amount'].sum()/1e6:.2f}M")
c2.metric("Avg Claim (Paid)", f"${paid['claim_amount'].mean():,.0f}")
c3.metric("Largest Claim",    f"${df['claim_amount'].max():,.0f}")
c4.metric("Annual Premiums",  f"${pol['annual_premium'].sum()/1e6:.2f}M")
st.divider()

left, right = st.columns(2)

# ── Payout by policy type ─────────────────────────────────────
with left:
    st.subheader("Total Payouts by Policy Type")
    by_type = (
        paid.groupby("policy_type")["claim_amount"]
        .sum().reset_index().sort_values("claim_amount")
    )
    fig1 = go.Figure(go.Bar(
        x=by_type["claim_amount"] / 1000,
        y=by_type["policy_type"],
        orientation="h",
        marker_color=["#1E2761","#0284C7","#047857","#D97706","#7C3AED"][:len(by_type)],
        text=[f"${v/1000:,.0f}K" for v in by_type["claim_amount"]],
        textposition="outside",
    ))
    fig1.update_layout(height=300, xaxis_title="Total Paid ($K)",
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig1, use_container_width=True)

# ── Premium revenue vs claim exposure by product ──────────────
with right:
    st.subheader("Premium Revenue vs Claim Exposure")
    rev = pol.groupby("policy_type")["annual_premium"].sum().reset_index()
    exp = df.groupby("policy_type")["claim_amount"].sum().reset_index()
    combined = rev.merge(exp, on="policy_type", how="outer").fillna(0)
    combined.columns = ["Policy Type","Premium Revenue","Claim Exposure"]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Premium Revenue", x=combined["Policy Type"],
                          y=combined["Premium Revenue"]/1000, marker_color="#047857"))
    fig2.add_trace(go.Bar(name="Claim Exposure",  x=combined["Policy Type"],
                          y=combined["Claim Exposure"]/1000,  marker_color="#DC2626", opacity=0.8))
    fig2.update_layout(barmode="group", height=300, yaxis_title="Amount ($K)",
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"),
                       legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig2, use_container_width=True)

# ── Running total of payouts ──────────────────────────────────
st.subheader("Cumulative Payouts Over Time")
timeline = (
    paid[paid["date_paid"].notna()]
    .sort_values("date_paid")
    [["date_paid","claim_amount"]]
    .copy()
)
timeline["running_total"] = timeline["claim_amount"].cumsum()

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=timeline["date_paid"], y=timeline["running_total"] / 1_000_000,
    fill="tozeroy", fillcolor="rgba(30,39,97,0.15)",
    line=dict(color="#1E2761", width=2.5),
    name="Cumulative Paid ($M)",
))
fig3.update_layout(
    height=300, yaxis_title="Cumulative Paid ($M)",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"),
    showlegend=False,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Denial analysis ───────────────────────────────────────────
st.subheader("Denial Analysis")
col1, col2 = st.columns(2)

with col1:
    decided = df[df["claim_status"].isin(["paid","approved","denied"])]
    denial_rate = (decided["claim_status"] == "denied").sum() / max(len(decided), 1) * 100
    st.metric("Overall Denial Rate", f"{denial_rate:.1f}%")
    st.metric("Total Denied Value",
              f"${df[df['claim_status']=='denied']['claim_amount'].sum():,.0f}")

with col2:
    by_reason = (
        df[df["denial_reason"].notna()]
        .groupby("denial_reason")["claim_id"]
        .count().reset_index()
        .rename(columns={"claim_id":"Count"})
    )
    if not by_reason.empty:
        st.dataframe(by_reason, use_container_width=True, hide_index=True)
