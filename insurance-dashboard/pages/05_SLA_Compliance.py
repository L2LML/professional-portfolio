"""SLA & Compliance — regulatory deadlines, breach tracking, reserve exposure."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from data.load_data import load_claims_fact
from data.colors import NAVY, SKY, GREEN, AMBER, RED, GRAY, GRID

st.set_page_config(page_title="SLA & Compliance", page_icon="⚖️", layout="wide")
st.title("⚖️ SLA & Compliance")

st.info(
    "**What is an SLA?**  A Service Level Agreement (SLA) is a regulatory and business standard "
    "that defines how quickly claims must be handled. Most U.S. states legally require insurers to:\n\n"
    "- **Acknowledge** a claim (assign an examiner) within **10 days** of filing.\n"
    "- **Make a decision** (approve or deny) within **45 days** of filing.\n\n"
    "Failing to meet these deadlines can result in **regulatory fines, lawsuits, and license risk**. "
    "This page tracks SLA compliance across all claims and identifies where the company is at risk."
)
st.divider()

df = load_claims_fact()

# ── SLA Calculations ──────────────────────────────────────────
# Acknowledge SLA: examiner assigned (proxy: not pending with no examiner after 10 days)
df["acknowledge_breached"] = (
    df["assigned_examiner"].isna() &
    (df["days_open"].fillna(0) > 10)
)

# Decision SLA: claims decided within 45 days
decided = df[df["claim_status"].isin(["paid","approved","denied"])].copy()
decided["decision_sla_met"]  = decided["days_to_decision"] <= 45
decided["decision_sla_days"] = decided["days_to_decision"]

open_claims = df[df["claim_status"].isin(["pending","under_review"])].copy()
open_claims["at_risk"]  = open_claims["days_open"].fillna(0).between(30, 44)
open_claims["breached"] = open_claims["days_open"].fillna(0) >= 45

# ── KPI Cards ─────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

total_decided      = len(decided)
sla_met            = decided["decision_sla_met"].sum()
sla_compliance_pct = sla_met / max(total_decided, 1) * 100
acknowledge_breach = df["acknowledge_breached"].sum()
at_risk_count      = open_claims["at_risk"].sum()
hard_breach_count  = open_claims["breached"].sum()

# Reserve: open exposure × historical approval rate
approval_rate   = sla_met / max(total_decided, 1)
pending_reserve = open_claims["claim_amount"].sum() * approval_rate

c1.metric("Decision SLA Compliance",
          f"{sla_compliance_pct:.1f}%",
          "Target: 100%",
          delta_color="off")
c2.metric("Claims Meeting 45-Day Rule", f"{sla_met:,} of {total_decided:,}")
c3.metric("Acknowledge Breaches (10d)", f"{acknowledge_breach:,}",
          "No examiner after 10 days", delta_color="off")
c4.metric("Open Claims At Risk (30–44d)", f"{at_risk_count:,}")
c5.metric("Pending Reserve Estimate",   f"${pending_reserve:,.0f}")

with st.expander("📖 What do these numbers mean?"):
    st.markdown("""
| Metric | Definition |
|--------|-----------|
| **Decision SLA Compliance** | The percentage of *decided* claims (approved or denied) where the decision was made within 45 days of the claim being filed. 100% is the regulatory goal. |
| **Acknowledge Breach** | Claims that went more than 10 days after filing without an examiner assigned. This is the first regulatory trigger — states require acknowledgment within 10 days. |
| **Open Claims At Risk** | Currently open claims that have been waiting 30–44 days. These are approaching the 45-day deadline and need immediate attention to avoid a breach. |
| **Pending Reserve Estimate** | The estimated dollar amount the company will need to pay out on currently open claims, based on the historical approval rate. Finance teams use this to ensure adequate cash reserves. Formula: Open Claim Exposure × Historical Approval Rate. |
""")

st.divider()

# ── SLA Status of Open Claims ─────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Open Claims SLA Status")
    st.caption(
        "Every open claim is classified by its urgency. "
        "**Breached** claims must be escalated immediately — every day past 45 increases regulatory risk."
    )
    if not open_claims.empty:
        open_claims["sla_status"] = open_claims.apply(
            lambda r: "🔴 Breached (45+ days)"  if r["breached"]
            else ("🟡 At Risk (30–44 days)"      if r["at_risk"]
            else "🟢 On Track (< 30 days)"),
            axis=1
        )
        sla_dist = open_claims["sla_status"].value_counts().reset_index()
        sla_dist.columns = ["Status","Count"]
        color_map = {
            "🔴 Breached (45+ days)":  RED,
            "🟡 At Risk (30–44 days)": AMBER,
            "🟢 On Track (< 30 days)": GREEN,
        }
        fig1 = px.bar(sla_dist, x="Status", y="Count",
                      color="Status", color_discrete_map=color_map,
                      text="Count")
        fig1.update_traces(textposition="outside")
        fig1.update_layout(
            showlegend=False, height=300,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID),
        )
        st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("Decision Time Distribution")
    st.caption(
        "How many days did it take to approve or deny decided claims? "
        "The vertical line marks the 45-day regulatory deadline. "
        "Bars to the right of it represent SLA breaches."
    )
    if not decided.empty:
        fig2 = px.histogram(
            decided, x="days_to_decision",
            nbins=20,
            color_discrete_sequence=[SKY],
            labels={"days_to_decision": "Days to Decision", "count": "Claims"},
        )
        fig2.add_vline(
            x=45, line_dash="dash", line_color=RED, line_width=2,
            annotation_text="45-day SLA limit",
            annotation_font_color=RED,
        )
        fig2.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="# Claims"),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Breached/At-Risk Claims Table ─────────────────────────────
st.subheader("🚨 Claims Requiring Immediate Action")
st.caption(
    "These are open claims past or approaching the 45-day regulatory deadline. "
    "Each one represents a compliance risk. They should be assigned to a senior examiner today."
)
urgent = open_claims[open_claims["days_open"].fillna(0) >= 30][[
    "claim_number","claim_status","policyholder_name","policy_type",
    "claim_amount","date_filed","days_open","assigned_examiner"
]].sort_values("days_open", ascending=False)

if urgent.empty:
    st.success("✅ No claims approaching or past the 45-day SLA deadline.")
else:
    def color_days(val):
        try:
            v = float(val)
            if v >= 45: return f"background-color: {RED}22; color: {RED}; font-weight: bold"
            if v >= 30: return f"background-color: {AMBER}22; color: {AMBER}; font-weight: bold"
        except: pass
        return ""

    st.dataframe(
        urgent.rename(columns={
            "claim_number":"Claim #","claim_status":"Status",
            "policyholder_name":"Policyholder","policy_type":"Product",
            "claim_amount":"Amount","date_filed":"Filed",
            "days_open":"Days Open","assigned_examiner":"Examiner"
        }).style.format({
            "Amount":"${:,.0f}","Days Open":"{:.0f}"
        }).applymap(color_days, subset=["Days Open"]),
        use_container_width=True, hide_index=True,
    )

# ── Reserve Detail ────────────────────────────────────────────
st.divider()
st.subheader("💰 Pending Reserve by Product")
st.caption(
    f"Based on a **{approval_rate:.0%} historical approval rate** across all decided claims. "
    "The reserve is the estimated amount the company needs to hold in cash to cover open claims if approved."
)
reserve_by_type = (
    open_claims.groupby("policy_type")["claim_amount"].sum() * approval_rate
).reset_index()
reserve_by_type.columns = ["Policy Type","Reserve Estimate"]
reserve_by_type = reserve_by_type.sort_values("Reserve Estimate", ascending=True)

fig3 = go.Figure(go.Bar(
    x=reserve_by_type["Reserve Estimate"],
    y=reserve_by_type["Policy Type"],
    orientation="h",
    marker_color=NAVY,
    text=[f"${v:,.0f}" for v in reserve_by_type["Reserve Estimate"]],
    textposition="outside",
))
fig3.update_layout(
    height=280, xaxis_title="Reserve Estimate ($)",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
)
st.plotly_chart(fig3, use_container_width=True)
