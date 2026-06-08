"""Customer Segments — age bands, tenure cohorts, profitability matrix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact, load_policies, load_policyholders
import numpy as np
from data.colors import NAVY, BLUE, GREEN, RED, AMBER, GRID, RISK_SCALE

st.set_page_config(page_title="Customer Segments", page_icon="👥", layout="wide")
st.title("👥 Customer Segments")
st.caption("Profitability analysis by age at issuance and customer tenure")
st.divider()

df  = load_claims_fact()
pol = load_policies()
ph  = load_policyholders()

AGE_ORDER    = ["18–35 Young Adult","36–50 Middle Age","51–65 Pre-Retirement","65+ Senior"]
TENURE_ORDER = ["New (0–2 yrs)","Establishing (3–5 yrs)","Loyal (6–10 yrs)","Long-Term (11+ yrs)"]

# ── Age Band Analysis ─────────────────────────────────────────
st.subheader("Policy Count & Claim Rate by Age Band")
age_pol    = pol.groupby("age_band").size().reset_index(name="policies")
age_claims = df.groupby("age_band").size().reset_index(name="claims")
age_df = age_pol.merge(age_claims, on="age_band", how="left").fillna(0)
age_df["claim_rate"] = (age_df["claims"] / age_df["policies"] * 100).round(1)
age_df = age_df[age_df["age_band"].isin(AGE_ORDER)]
age_df["age_band"] = pd.Categorical(age_df["age_band"], categories=AGE_ORDER, ordered=True)
age_df = age_df.sort_values("age_band")

fig1 = go.Figure()
fig1.add_trace(go.Bar(name="Policies", x=age_df["age_band"], y=age_df["policies"],
                      marker_color=NAVY, yaxis="y1"))
fig1.add_trace(go.Bar(name="Claims",   x=age_df["age_band"], y=age_df["claims"],
                      marker_color=BLUE, yaxis="y1"))
fig1.add_trace(go.Scatter(name="Claim Rate %", x=age_df["age_band"], y=age_df["claim_rate"],
                           mode="lines+markers+text", text=[f"{v:.0f}%" for v in age_df["claim_rate"]],
                           textposition="top center", line=dict(color=RED, width=2.5),
                           marker=dict(size=8), yaxis="y2"))
fig1.update_layout(
    barmode="group", height=340,
    yaxis=dict(title="Count", gridcolor="#E2E8F0"),
    yaxis2=dict(title="Claim Rate %", overlaying="y", side="right", range=[0, 80], showgrid=False),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", y=1.1), xaxis=dict(showgrid=False),
)
st.plotly_chart(fig1, use_container_width=True)

# ── Tenure Cohort ─────────────────────────────────────────────
st.subheader("Premium Revenue vs Claim Exposure by Tenure")
ten_pol = (
    pol[pol["tenure_tier"].notna()]
    .groupby("tenure_tier")
    .agg(premium=("annual_premium","sum"), count=("policy_id","count"))
    .reset_index()
)
ten_claims = (
    df[df["tenure_tier"].notna()]
    .groupby("tenure_tier")["claim_amount"]
    .sum().reset_index().rename(columns={"claim_amount":"exposure"})
)
ten_df = ten_pol.merge(ten_claims, on="tenure_tier", how="left").fillna(0)
ten_df["tenure_tier"] = pd.Categorical(ten_df["tenure_tier"], categories=TENURE_ORDER, ordered=True)
ten_df = ten_df.sort_values("tenure_tier")
ten_df["ratio"] = (ten_df["premium"] / ten_df["exposure"].replace(0, float("nan"))).round(2)

fig2 = go.Figure()
fig2.add_trace(go.Bar(name="Annual Premiums", x=ten_df["tenure_tier"],
                      y=ten_df["premium"]/1000, marker_color=GREEN))
fig2.add_trace(go.Bar(name="Claim Exposure",  x=ten_df["tenure_tier"],
                      y=ten_df["exposure"]/1000, marker_color=RED, opacity=0.85))
fig2.update_layout(
    barmode="group", height=320, yaxis_title="Amount ($K)",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig2, use_container_width=True)

# ── Age × Tenure Loss Ratio Matrix ───────────────────────────
st.subheader("Which Customer Segments Are Most Profitable?")
st.info(
    "**How to read this chart:**\n\n"
    "Each cell shows the **Loss Ratio** for that customer group — "
    "the same metric explained on the Financial Analysis page.\n\n"
    "**Loss Ratio = Claims Paid ÷ Premiums Collected**\n\n"
    "- 🟢 **Green (below 0.70)** — Healthy. This group pays in more than they claim. "
    "The company keeps at least 30 cents of every premium dollar.\n"
    "- 🟡 **Amber (0.70 – 1.00)** — Watch zone. Claims are eating into premiums.\n"
    "- 🔴 **Red (above 1.00)** — Losing money on this segment. Claims exceed premiums collected.\n\n"
    "Use this to identify which age groups and tenure tiers drive profit — and which need pricing review."
)

paid_matrix = (
    df[(df["claim_status"] == "paid") &
       df["age_band"].notna() &
       df["tenure_tier"].notna()]
    .groupby(["age_band","tenure_tier"])["claim_amount"].sum()
    .reset_index().rename(columns={"claim_amount":"claims_paid"})
)
# Use total premiums collected (annual × years in force) so loss ratio is apples-to-apples
pol_seg = pol[pol["age_band"].notna() & pol["tenure_tier"].notna()].copy()
pol_seg["total_collected"] = pol_seg["annual_premium"] * pol_seg["years_in_force"].clip(lower=1)
pol_matrix = (
    pol_seg.groupby(["age_band","tenure_tier"])["total_collected"].sum()
    .reset_index().rename(columns={"total_collected":"premiums"})
)
matrix = pol_matrix.merge(paid_matrix, on=["age_band","tenure_tier"], how="left").fillna(0)
matrix["loss_ratio"] = (
    matrix["claims_paid"] / matrix["premiums"].replace(0, float("nan"))
).round(2)

pivot = matrix.pivot(index="age_band", columns="tenure_tier", values="loss_ratio")
pivot = pivot.reindex(index=[a for a in AGE_ORDER if a in pivot.index])
pivot = pivot.reindex(columns=[t for t in TENURE_ORDER if t in pivot.columns])

# Label each cell with the loss ratio AND a plain-English zone
def cell_label(val):
    if pd.isna(val):
        return "No data"
    zone = "✅ Healthy" if val < 0.70 else ("⚠️ Watch" if val < 1.0 else "🔴 High Risk")
    return f"{val:.2f}\n{zone}"

label_pivot = pivot.applymap(cell_label)

fig3 = px.imshow(
    pivot,
    text_auto=False,
    color_continuous_scale=[
        [0.0,  GREEN],   # 0.0  = very profitable — green
        [0.5,  AMBER],   # 0.70 midpoint — amber
        [1.0,  RED  ],   # 1.0+ = losing money — red
    ],
    zmin=0, zmax=1.0,
    labels=dict(color="Loss Ratio"),
    aspect="auto",
)

# Add cell annotations manually with both number and zone label
for i, age in enumerate(pivot.index):
    for j, tenure in enumerate(pivot.columns):
        val = pivot.loc[age, tenure]
        if pd.notna(val):
            zone = "✅ Healthy" if val < 0.70 else ("⚠️ Watch" if val < 1.0 else "🔴 High")
            fig3.add_annotation(
                x=j, y=i,
                text=f"<b>{val:.2f}</b><br><span style='font-size:10px'>{zone}</span>",
                showarrow=False,
                font=dict(color="white" if val > 0.45 else NAVY, size=12),
            )

fig3.update_layout(
    height=360,
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(title="How long they've been a customer →", side="bottom"),
    yaxis=dict(title="Age when they bought the policy →"),
    coloraxis_colorbar=dict(
        title="Loss Ratio",
        tickvals=[0, 0.35, 0.70, 1.0],
        ticktext=["0.00<br>Very profitable","0.35","0.70<br>Benchmark","1.00<br>Break-even"],
        len=0.8,
    ),
    margin=dict(t=20, b=60),
)
st.plotly_chart(fig3, use_container_width=True)

# Insight callout
if not matrix.empty:
    best      = matrix.loc[matrix["loss_ratio"].idxmin()]
    worst     = matrix.loc[matrix["loss_ratio"].idxmax()]
    best_keep = (1 - best["loss_ratio"]) * 100
    worst_lr  = worst["loss_ratio"]
    worst_desc = (
        "claims exceed premiums collected" if worst_lr > 1.0
        else f"only {(1 - worst_lr) * 100:.0f}¢ margin remaining per premium dollar"
    )
    col1, col2 = st.columns(2)
    col1.success(
        f"**Most profitable segment:** {best['age_band']} · {best['tenure_tier']}\n\n"
        f"Loss Ratio: **{best['loss_ratio']:.2f}** — "
        f"the company keeps **{best_keep:.0f}¢** of every premium dollar."
    )
    col2.error(
        f"**Highest risk segment:** {worst['age_band']} · {worst['tenure_tier']}\n\n"
        f"Loss Ratio: **{worst_lr:.2f}** — {worst_desc}."
    )
