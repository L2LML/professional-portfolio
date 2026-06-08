"""Financial Analysis — payouts, revenue vs exposure, running totals."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.sidebar_note import show as _sidebar_note
from data.load_data import load_claims_fact, load_policies
from data.colors import PRODUCT_COLORS, NAVY, SKY, GREEN, RED, AMBER, GRAY, GRID

st.set_page_config(page_title="Financial Analysis", page_icon="💰", layout="wide")
st.title("💰 Financial Analysis")
st.info(
    "**Financial Analysis** shows whether the insurance operation is profitable. "
    "The key question: are we collecting enough in premiums to cover what we pay in claims? "
    "The **Loss Ratio** is the primary answer — and breaking it down by product shows *which* "
    "policies are driving profit or loss."
)
st.divider()
_sidebar_note()

df  = load_claims_fact()
pol = load_policies()

# Compute lifetime premiums once — used throughout this page
pol["total_collected"] = pol["annual_premium"] * pol["years_in_force"].clip(lower=1)

paid     = df[df["claim_status"] == "paid"]
approved = df[df["claim_status"].isin(["paid","approved"])]

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Paid",       f"${paid['claim_amount'].sum()/1e6:.2f}M")
c2.metric("Avg Claim (Paid)", f"${paid['claim_amount'].mean():,.0f}")
c3.metric("Largest Claim",    f"${df['claim_amount'].max():,.0f}")
overall_lr = paid["claim_amount"].sum() / max(pol["total_collected"].sum(), 1)
lr_zone = "🟢 Healthy" if overall_lr < 0.70 else ("🟡 Watch" if overall_lr < 0.85 else "🔴 High Risk")
c4.metric("Portfolio Loss Ratio", f"{overall_lr:.2f}",
          delta=lr_zone, delta_color="off",
          help="Total claims paid ÷ total premiums collected. Below 0.70 is healthy.")
st.divider()

left, right = st.columns(2)

# ── Payout by policy type ─────────────────────────────────────
with left:
    st.subheader("Total Paid Out by Policy Type")
    st.caption("How much the company has paid to beneficiaries, broken down by product. "
               "Colors match the product palette used throughout the dashboard.")
    by_type = (
        paid.groupby("policy_type")["claim_amount"]
        .sum().reset_index().sort_values("claim_amount")
    )
    # Smart formatter: M for millions, K for thousands
    def fmt_dollars(v):
        if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
        if v >= 1_000:     return f"${v/1_000:,.0f}K"
        return f"${v:,.0f}"

    fig1 = go.Figure(go.Bar(
        x=by_type["claim_amount"],
        y=by_type["policy_type"],
        orientation="h",
        marker_color=[PRODUCT_COLORS.get(t, NAVY) for t in by_type["policy_type"]],
        text=[fmt_dollars(v) for v in by_type["claim_amount"]],
        textposition="outside",
    ))
    fig1.update_layout(
        height=300,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Total Paid Out ($)",
                   tickformat="$,.0f"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig1, use_container_width=True)

# ── Loss Ratio by Product ─────────────────────────────────────
with right:
    st.subheader("Loss Ratio by Product")
    st.caption(
        "**Loss Ratio** = Claims Paid ÷ Premiums Collected over policy lifetime. "
        "🟢 Below 0.70 = healthy (company keeps 30¢+ per premium dollar). "
        "🟡 0.70–0.85 = watch zone. 🔴 Above 0.85 = high risk. "
        "Dashed line = industry benchmark at 0.70."
    )
    rev2  = pol.groupby("policy_type")["total_collected"].sum()
    exp2  = df[df["claim_status"]=="paid"].groupby("policy_type")["claim_amount"].sum()
    lr_rt = (exp2 / rev2).dropna().reset_index()
    lr_rt.columns = ["Policy Type","Loss Ratio"]
    lr_rt = lr_rt.sort_values("Loss Ratio", ascending=True)
    lr_rt["color"] = lr_rt["Loss Ratio"].apply(
        lambda r: GREEN if r < 0.70 else (AMBER if r < 0.85 else RED)
    )
    lr_rt["zone"] = lr_rt["Loss Ratio"].apply(
        lambda r: "🟢 Healthy" if r < 0.70 else ("🟡 Watch" if r < 0.85 else "🔴 High Risk")
    )

    max_lr = max(lr_rt["Loss Ratio"].max() * 1.4, 1.0)
    fig2 = go.Figure(go.Bar(
        x=lr_rt["Loss Ratio"],
        y=lr_rt["Policy Type"],
        orientation="h",
        marker_color=lr_rt["color"].tolist(),
        text=[f"{row['Loss Ratio']:.2f}  {row['zone']}" for _, row in lr_rt.iterrows()],
        textposition="outside",
    ))
    fig2.add_vline(x=0.70, line_dash="dash", line_color=AMBER, line_width=2,
                   annotation_text="0.70 Benchmark",
                   annotation_position="top right",
                   annotation_font_color=AMBER)
    fig2.update_layout(
        height=300,
        xaxis=dict(title="Loss Ratio", range=[0, max_lr], showgrid=False),
        yaxis=dict(showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
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
    line=dict(color=NAVY, width=2.5),
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

# ── Unit Economics by Product ─────────────────────────────────
st.divider()
st.subheader("📊 Unit Economics by Product Line")
st.caption(
    "**Avg Annual Premium** = what a typical policy of this type earns per year. "
    "**Avg Claim When Filed** = what the company typically pays out when a claim is made. "
    "The gap between them shows the revenue relationship per policy type."
)
unit = pol.groupby("policy_type").agg(
    avg_premium=("annual_premium","mean"),
    policy_count=("policy_id","count"),
).reset_index()
claim_unit = df[df["claim_status"]=="paid"].groupby("policy_type")["claim_amount"].mean().reset_index()
claim_unit.columns = ["policy_type","avg_claim"]
unit = unit.merge(claim_unit, on="policy_type", how="left").fillna(0)

fig_unit = go.Figure()
fig_unit.add_trace(go.Bar(
    name="Avg Annual Premium",
    x=unit["policy_type"],
    y=unit["avg_premium"],
    marker_color=GREEN,
    text=[f"${v:,.0f}" for v in unit["avg_premium"]],
    textposition="outside",
))
fig_unit.add_trace(go.Bar(
    name="Avg Claim When Filed",
    x=unit["policy_type"],
    y=unit["avg_claim"],
    marker_color=RED,
    opacity=0.8,
    text=[f"${v:,.0f}" for v in unit["avg_claim"]],
    textposition="outside",
))
fig_unit.update_layout(
    barmode="group", height=340,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor=GRID, title="Amount ($)"),
    legend=dict(orientation="h", y=1.12),
)
st.plotly_chart(fig_unit, use_container_width=True)
