"""Customer Segments — profitability matrix and monthly premium collection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.sidebar_note import show as _sidebar_note
from data.load_data import load_claims_fact, load_policies, load_policyholders
import numpy as np
from data.colors import NAVY, BLUE, GREEN, RED, AMBER, GRID, RISK_SCALE, SKY

st.set_page_config(page_title="Customer Segments", page_icon="👥", layout="wide")
st.title("👥 Customer Segments")
st.caption("Profitability analysis by age at issuance and customer tenure")
st.divider()
_sidebar_note()

df  = load_claims_fact()
pol = load_policies()
ph  = load_policyholders()

AGE_ORDER    = ["18–35 Young Adult","36–50 Middle Age","51–65 Pre-Retirement","65+ Senior"]
TENURE_ORDER = ["New (0–2 yrs)","Establishing (3–5 yrs)","Loyal (6–10 yrs)","Long-Term (11+ yrs)"]

# Compute lifetime premiums once — used throughout this page
pol["total_collected"] = pol["annual_premium"] * pol["years_in_force"].clip(lower=1)

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

actual_max = min(pivot.max().max() * 1.1, 1.5) if not pivot.empty else 1.0
actual_max = max(actual_max, 0.90)

fig3 = px.imshow(
    pivot,
    text_auto=False,
    color_continuous_scale=[
        [0.0,                  GREEN],
        [0.70 / actual_max,    AMBER],
        [0.85 / actual_max,    RED],
        [1.0,                  "#6B0000"],
    ],
    zmin=0, zmax=actual_max,
    labels=dict(color="Loss Ratio"),
    aspect="auto",
)

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
        tickvals=[0, 0.35, 0.70, 0.85, actual_max],
        ticktext=[
            "0.00 Very Profitable",
            "0.35",
            "0.70 Benchmark",
            "0.85 Watch",
            f"{actual_max:.2f} High Risk",
        ],
        len=0.9,
    ),
    margin=dict(t=20, b=60),
)
st.plotly_chart(fig3, width="stretch")

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

# ── Monthly Premium Collection ────────────────────────────────
st.divider()
st.subheader("📅 Monthly Premium Collection")
st.caption(
    "Total annual premiums from policies whose **issue month** falls in each calendar month. "
    "Shows which months historically generate the most new premium revenue — "
    "useful for cash flow planning and understanding when sales activity peaks."
)

pol["issue_month"] = pd.to_datetime(pol["issue_date"]).dt.month
monthly_prem = (
    pol.groupby("issue_month")["annual_premium"]
    .sum().reset_index().rename(columns={"annual_premium":"total_premium"})
)
# Fill any missing months with 0
all_months = pd.DataFrame({"issue_month": range(1, 13)})
monthly_prem = all_months.merge(monthly_prem, on="issue_month", how="left").fillna(0)

month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
monthly_prem["month_name"] = monthly_prem["issue_month"].apply(lambda m: month_labels[m-1])

avg_monthly = monthly_prem["total_premium"].mean()
monthly_prem["color"] = monthly_prem["total_premium"].apply(
    lambda v: NAVY if v >= avg_monthly else SKY
)

fig_monthly = go.Figure(go.Bar(
    x=monthly_prem["month_name"],
    y=monthly_prem["total_premium"],
    marker_color=monthly_prem["color"].tolist(),
    text=[f"${v:,.0f}" for v in monthly_prem["total_premium"]],
    textposition="outside",
))
fig_monthly.add_hline(
    y=avg_monthly, line_dash="dash", line_color=AMBER, line_width=1.5,
    annotation_text=f"Monthly avg ${avg_monthly:,.0f}",
    annotation_font_color=AMBER,
)
fig_monthly.update_layout(
    height=340,
    yaxis=dict(title="Annual Premiums ($)", gridcolor=GRID, tickformat="$,.0f"),
    xaxis=dict(showgrid=False, title="Issue Month"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
)
st.plotly_chart(fig_monthly, width="stretch")
st.caption(
    f"🟦 Dark navy bars = above average month (≥ ${avg_monthly:,.0f}). "
    f"🔵 Sky blue bars = below average. "
    "Amber dashed line = monthly average."
)
