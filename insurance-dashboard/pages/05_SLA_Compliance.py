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
    st.subheader("What Kind of Claims Are Open?")
    st.caption(
        "Open claims broken down by **policy type** — so you can see whether overdue claims "
        "are concentrated in Term Life, Whole Life, or other products. "
        "Colors match the product legend used throughout the dashboard."
    )
    if not open_claims.empty:
        from data.colors import PRODUCT_COLORS
        # Classify each open claim by urgency
        open_claims["sla_bucket"] = open_claims["days_open"].apply(
            lambda d: "🔴 Breached (45+ days)" if d >= 45
            else ("🟡 At Risk (30–44 days)" if d >= 30
            else "🟢 On Track (< 30 days)")
        )
        BUCKET_ORDER = ["🟢 On Track (< 30 days)","🟡 At Risk (30–44 days)","🔴 Breached (45+ days)"]
        by_type = (
            open_claims.groupby(["sla_bucket","policy_type"])
            .size().reset_index(name="count")
        )
        import pandas as pd_inner
        by_type["sla_bucket"] = pd_inner.Categorical(
            by_type["sla_bucket"], categories=BUCKET_ORDER, ordered=True
        )
        by_type = by_type.sort_values("sla_bucket")

        fig1 = px.bar(
            by_type, x="sla_bucket", y="count",
            color="policy_type",
            color_discrete_map=PRODUCT_COLORS,
            barmode="stack",
            labels={"sla_bucket":"SLA Status","count":"Open Claims","policy_type":"Product"},
            text="count",
        )
        fig1.update_traces(textposition="inside", textfont_color="white")
        fig1.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor=GRID),
            legend=dict(orientation="h", y=1.15, title=""),
        )
        st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("Decision Time Distribution")
    st.caption(
        "How many days did it take to approve or deny decided claims? "
        "🟢 Green bars = within the 45-day SLA. "
        "🟡 Amber = approaching the limit (31–45 days). "
        "🔴 Red = SLA breached. The more red, the higher the regulatory risk."
    )
    if not decided.empty:
        import numpy as np
        bins   = [0, 10, 20, 30, 45, 60, 90, 999]
        labels = ["0–10d","11–20d","21–30d","31–45d","46–60d","61–90d","90+d"]
        colors = [GREEN,   GREEN,   GREEN,   AMBER,   RED,     RED,     RED  ]
        decided["bin"] = pd.cut(
            decided["days_to_decision"], bins=bins, labels=labels, right=True
        )
        bin_counts = decided["bin"].value_counts().reindex(labels, fill_value=0).reset_index()
        bin_counts.columns = ["Bin","Count"]

        fig2 = go.Figure(go.Bar(
            x=bin_counts["Bin"],
            y=bin_counts["Count"],
            marker_color=colors,
            text=bin_counts["Count"],
            textposition="outside",
        ))
        fig2.add_vline(
            x=3.5,              # between "31–45d" and "46–60d" buckets
            line_dash="dash", line_color=RED, line_width=2,
            annotation_text="45-day SLA limit",
            annotation_font_color=RED,
            annotation_position="top right",
        )
        fig2.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="Days to Decision"),
            yaxis=dict(gridcolor=GRID, title="# Claims"),
            showlegend=False,
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
