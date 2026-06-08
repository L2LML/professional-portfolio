"""Customer Segments — age bands, tenure cohorts, profitability matrix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact, load_policies, load_policyholders

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
                      marker_color="#1E2761", yaxis="y1"))
fig1.add_trace(go.Bar(name="Claims",   x=age_df["age_band"], y=age_df["claims"],
                      marker_color="#0284C7", yaxis="y1"))
fig1.add_trace(go.Scatter(name="Claim Rate %", x=age_df["age_band"], y=age_df["claim_rate"],
                           mode="lines+markers+text", text=[f"{v:.0f}%" for v in age_df["claim_rate"]],
                           textposition="top center", line=dict(color="#DC2626", width=2.5),
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
                      y=ten_df["premium"]/1000, marker_color="#047857"))
fig2.add_trace(go.Bar(name="Claim Exposure",  x=ten_df["tenure_tier"],
                      y=ten_df["exposure"]/1000, marker_color="#DC2626", opacity=0.85))
fig2.update_layout(
    barmode="group", height=320, yaxis_title="Amount ($K)",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig2, use_container_width=True)

# ── Age × Tenure Profitability Matrix ─────────────────────────
st.subheader("Age × Tenure Profitability Matrix")
st.caption("Premium-to-claim ratio — higher = more profitable segment")

matrix_data = (
    df[df["age_band"].notna() & df["tenure_tier"].notna()]
    .groupby(["age_band","tenure_tier"])
    .agg(claims=("claim_id","count"), exposure=("claim_amount","sum"))
    .reset_index()
)
pol_matrix = (
    pol[pol["age_band"].notna() & pol["tenure_tier"].notna()]
    .groupby(["age_band","tenure_tier"])
    .agg(premium=("annual_premium","sum"), policies=("policy_id","count"))
    .reset_index()
)
matrix = pol_matrix.merge(matrix_data, on=["age_band","tenure_tier"], how="left").fillna(0)
matrix["profit_ratio"] = (matrix["premium"] / matrix["exposure"].replace(0, float("nan"))).round(2)

pivot = matrix.pivot(index="age_band", columns="tenure_tier", values="profit_ratio")
pivot = pivot.reindex(index=[a for a in AGE_ORDER if a in pivot.index])
pivot = pivot.reindex(columns=[t for t in TENURE_ORDER if t in pivot.columns])

fig3 = px.imshow(
    pivot, text_auto=".2f",
    color_continuous_scale=["#DC2626","#FBBF24","#047857"],
    labels=dict(color="Premium/Claim Ratio"),
    aspect="auto",
)
fig3.update_layout(
    height=320, paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Tenure Tier", yaxis_title="Age Band at Issuance",
    coloraxis_colorbar=dict(title="Ratio"),
)
st.plotly_chart(fig3, use_container_width=True)
st.caption("🟢 Green = high premium-to-claim ratio (profitable)  ·  🔴 Red = high claim exposure relative to premiums")
