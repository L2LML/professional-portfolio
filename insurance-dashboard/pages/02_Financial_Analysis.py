"""Financial Analysis — payouts, revenue vs exposure, running totals."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
        marker_color=[PRODUCT_COLORS.get(t, NAVY) for t in by_type["policy_type"]],
        text=[f"${v/1000:,.0f}K" for v in by_type["claim_amount"]],
        textposition="outside",
    ))
    fig1.update_layout(height=300, xaxis_title="Total Paid ($K)",
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig1, use_container_width=True)

# ── Net Margin by Product ─────────────────────────────────────
with right:
    st.subheader("Net Margin by Product")
    st.caption(
        "**Net Margin** = Annual Premiums Collected minus Claims Paid. "
        "🟢 Green = the product generates more in premiums than it pays in claims. "
        "🔴 Red = claims are exceeding premiums collected — the product is losing money."
    )
    rev = pol.groupby("policy_type")["annual_premium"].sum().reset_index()
    exp = df[df["claim_status"]=="paid"].groupby("policy_type")["claim_amount"].sum().reset_index()
    combined = rev.merge(exp, on="policy_type", how="outer").fillna(0)
    combined.columns = ["Policy Type","Premiums","Claims Paid"]
    combined["Net Margin"] = combined["Premiums"] - combined["Claims Paid"]
    combined = combined.sort_values("Net Margin", ascending=True)
    combined["color"] = combined["Net Margin"].apply(
        lambda v: GREEN if v >= 0 else RED
    )

    fig2 = go.Figure(go.Bar(
        x=combined["Net Margin"] / 1000,
        y=combined["Policy Type"],
        orientation="h",
        marker_color=combined["color"].tolist(),
        text=[f"${v/1000:+,.0f}K" for v in combined["Net Margin"]],
        textposition="outside",
    ))
    fig2.add_vline(x=0, line_color="black", line_width=1)
    fig2.update_layout(
        height=300,
        xaxis_title="Net Margin ($K)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
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

# ── Loss Ratio by Product ─────────────────────────────────────
st.divider()
st.subheader("📊 Loss Ratio by Product Line")
st.info(
    "**Loss Ratio** = Total Claims Paid ÷ Total Premiums Collected for that product. \n\n"
    "- **Below 0.70** 🟢 — Healthy. The company keeps 30+ cents of every premium dollar after paying claims.\n"
    "- **0.70 – 0.85** 🟡 — Watch zone. Still profitable but claims are eating into margins.\n"
    "- **Above 0.85** 🔴 — High risk. Little margin left for operating costs. Above 1.0 means paying out more than collecting.\n\n"
    "Industry benchmark for life insurance: **0.55 – 0.75**"
)

paid_by_type = (
    df[df["claim_status"] == "paid"]
    .groupby("policy_type")["claim_amount"].sum()
    .reset_index().rename(columns={"claim_amount":"paid"})
)
prem_by_type = (
    pol.groupby("policy_type")["annual_premium"].sum()
    .reset_index().rename(columns={"annual_premium":"premiums"})
)
lr_df = prem_by_type.merge(paid_by_type, on="policy_type", how="left").fillna(0)
lr_df["loss_ratio"] = (lr_df["paid"] / lr_df["premiums"].replace(0, float("nan"))).round(3)
lr_df = lr_df.dropna(subset=["loss_ratio"]).sort_values("loss_ratio", ascending=True)

# Color each bar by its loss ratio zone
lr_df["color"] = lr_df["loss_ratio"].apply(
    lambda r: GREEN if r < 0.70 else (AMBER if r < 0.85 else RED)
)
lr_df["zone"] = lr_df["loss_ratio"].apply(
    lambda r: "Healthy (< 0.70)" if r < 0.70 else ("Watch (0.70–0.85)" if r < 0.85 else "High Risk (> 0.85)")
)

fig_lr = go.Figure()
for _, row in lr_df.iterrows():
    fig_lr.add_trace(go.Bar(
        x=[row["loss_ratio"]],
        y=[row["policy_type"]],
        orientation="h",
        marker_color=row["color"],
        name=row["zone"],
        text=[f"{row['loss_ratio']:.2f}"],
        textposition="outside",
        showlegend=False,
    ))

# Industry benchmark line at 0.70
fig_lr.add_vline(
    x=0.70, line_dash="dash", line_color=AMBER, line_width=2,
    annotation_text="Benchmark 0.70", annotation_position="top right",
    annotation_font_color=AMBER,
)
# Break-even line at 1.0
fig_lr.add_vline(
    x=1.0, line_dash="dot", line_color=RED, line_width=2,
    annotation_text="Break-even 1.0", annotation_position="top right",
    annotation_font_color=RED,
)
fig_lr.update_layout(
    height=320, xaxis_title="Loss Ratio",
    xaxis=dict(range=[0, max(lr_df["loss_ratio"].max() * 1.3, 1.1)], showgrid=False),
    yaxis=dict(showgrid=False),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=20, l=10, r=80),
)
st.plotly_chart(fig_lr, use_container_width=True)

# Summary callout
overall_lr = df[df["claim_status"]=="paid"]["claim_amount"].sum() / max(pol["annual_premium"].sum(), 1)
zone_label = "🟢 Healthy" if overall_lr < 0.70 else ("🟡 Watch Zone" if overall_lr < 0.85 else "🔴 High Risk")
st.metric("Overall Portfolio Loss Ratio", f"{overall_lr:.2f}", zone_label, delta_color="off")
