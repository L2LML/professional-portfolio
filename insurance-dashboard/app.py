"""
app.py — Executive Summary dashboard page.
Entry point for the Insurance Claims BI Dashboard.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from data.load_data import load_claims_fact, load_policies
from data.colors import (
    STATUS_COLORS, NAVY, SKY, GREEN, AMBER, RED, GRAY, GRID
)

st.set_page_config(
    page_title="Insurance Claims Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Insurance Claims Dashboard")
st.caption("Life Insurance Operations · Built with PostgreSQL → Python ETL → Streamlit")
st.divider()

df  = load_claims_fact()
pol = load_policies()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")
years     = sorted(df["claim_year"].dropna().unique().tolist())
sel_years = st.sidebar.multiselect("Year Filed", years, default=years)
pol_types = sorted(df["policy_type"].dropna().unique().tolist())
sel_types = st.sidebar.multiselect("Policy Type", pol_types, default=pol_types)
states    = sorted(df["address_state"].dropna().unique().tolist())
sel_states= st.sidebar.multiselect("State", states, default=states)

filtered = df[
    df["claim_year"].isin(sel_years) &
    df["policy_type"].isin(sel_types) &
    df["address_state"].isin(sel_states)
]
st.sidebar.divider()
st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(df):,} claims")

# ── Computed metrics ──────────────────────────────────────────
total_claims    = len(filtered)
total_paid      = filtered[filtered["claim_status"] == "paid"]["claim_amount"].sum()
# Loss ratio = claims paid ÷ total premiums COLLECTED over the policy lifetime
# (annual premium × years in force per policy) — apples-to-apples comparison
total_premiums  = (pol["annual_premium"] * pol["years_in_force"].clip(lower=1)).sum()
loss_ratio      = total_paid / total_premiums if total_premiums > 0 else 0
avg_processing  = filtered["days_to_decision"].dropna().mean()

# Pending reserve = open claim exposure × historical approval rate
decided         = filtered[filtered["claim_status"].isin(["paid","approved","denied"])]
approval_rate   = (
    len(decided[decided["claim_status"].isin(["paid","approved"])]) /
    max(len(decided), 1)
)
open_exposure   = filtered[
    filtered["claim_status"].isin(["pending","under_review"])
]["claim_amount"].sum()
pending_reserve = open_exposure * approval_rate

# SLA: decisions made within 45 days
decided_claims      = filtered[filtered["days_to_decision"].notna()]
sla_compliant_pct   = (
    (decided_claims["days_to_decision"] <= 45).sum() /
    max(len(decided_claims), 1) * 100
)

# ── KPI Cards ─────────────────────────────────────────────────
st.subheader("Key Performance Indicators")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Claims Filed",  f"{total_claims:,}")

# Loss ratio: color-code the delta message
lr_label = (
    "🟢 Healthy"   if loss_ratio < 0.70 else
    "🟡 Watch"     if loss_ratio < 0.85 else
    "🔴 High Risk"
)
c2.metric("Loss Ratio", f"{loss_ratio:.2f}", lr_label,
          delta_color="off")

c3.metric("Total Paid Out",        f"${total_paid/1_000_000:.2f}M")
c4.metric("Avg Decision Time",     f"{avg_processing:.0f} days" if pd.notna(avg_processing) else "—")
c5.metric("Pending Reserve Est.",  f"${pending_reserve:,.0f}")

# ── Metric explanations ───────────────────────────────────────
with st.expander("📖 What do these numbers mean?"):
    st.markdown("""
| Metric | Plain-English Definition |
|--------|--------------------------|
| **Total Claims Filed** | How many death benefit claims have been submitted by beneficiaries across all policies. |
| **Loss Ratio** | Claims paid out ÷ premiums collected. **0.70 means the company pays 70¢ for every $1 earned in premiums.** Below 0.70 = healthy. Above 1.0 = paying out more than taking in — unsustainable. Industry benchmark: 0.55–0.75. |
| **Total Paid Out** | The actual dollar amount disbursed to beneficiaries for approved and paid claims. |
| **Avg Decision Time** | On average, how many days from when a claim is filed to when it is approved or denied. Faster = better customer experience and lower regulatory risk. |
| **Pending Reserve Estimate** | The estimated dollar liability sitting in open/in-review claims. Calculated as: open claim exposure × historical approval rate. Finance teams use this to ensure the company holds enough cash on hand. |
""")

st.divider()

# ── Charts row ────────────────────────────────────────────────
left, right = st.columns([1, 2])

# Claims by status — donut
with left:
    st.subheader("Claims by Status")
    st.caption("Each segment is a stage in the claims lifecycle — from filing through payment or denial.")
    status_counts = filtered["claim_status"].value_counts().reset_index()
    status_counts.columns = ["Status","Count"]
    fig_donut = px.pie(
        status_counts, values="Count", names="Status",
        hole=0.55, color="Status",
        color_discrete_map=STATUS_COLORS,
    )
    fig_donut.update_traces(textposition="outside", textinfo="percent+label")
    fig_donut.update_layout(
        showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
        height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Monthly trend — current year vs prior year
with right:
    st.subheader("Monthly Claims Volume — Year Over Year")
    st.caption(
        "Compares claim volume this year vs the same months last year. "
        "Rising bars with a gap above the prior-year line signals growing claim activity."
    )

    monthly = (
        filtered.groupby(["claim_year","claim_month"])
        .agg(count=("claim_id","count"))
        .reset_index()
    )
    current_year = int(filtered["claim_year"].max()) if len(filtered) > 0 else 2024
    prior_year   = current_year - 1

    curr = monthly[monthly["claim_year"] == current_year].set_index("claim_month")["count"]
    prev = monthly[monthly["claim_year"] == prior_year].set_index("claim_month")["count"]
    months = list(range(1, 13))
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig_yoy = go.Figure()
    # Prior year: gray bars in background (reference)
    fig_yoy.add_trace(go.Bar(
        x=month_labels,
        y=[prev.get(m, 0) for m in months],
        name=str(prior_year),
        marker_color=GRAY,
        opacity=0.5,
    ))
    # Current year: navy bars in foreground (what we're watching)
    fig_yoy.add_trace(go.Bar(
        x=month_labels,
        y=[curr.get(m, 0) for m in months],
        name=str(current_year),
        marker_color=NAVY,
    ))
    fig_yoy.update_layout(
        barmode="overlay",
        height=320, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Claims Filed"),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

# ── Open high-value claims ────────────────────────────────────
st.subheader("⚠️ Open High-Value Claims  (> $250,000)")
st.caption(
    "Claims over $250,000 that are still pending or under review. "
    "These represent the largest financial exposure on the company's books and warrant senior examiner attention."
)
high_open = filtered[
    filtered["claim_status"].isin(["pending","under_review"]) &
    (filtered["claim_amount"] > 250_000)
][["claim_number","claim_status","policyholder_name","policy_type",
   "cause_of_death","claim_amount","date_filed","days_open",
   "aging_flag","assigned_examiner"]].sort_values("claim_amount", ascending=False)

if high_open.empty:
    st.success("No open high-value claims matching current filters.")
else:
    st.dataframe(
        high_open.rename(columns={
            "claim_number":"Claim #","claim_status":"Status",
            "policyholder_name":"Policyholder","policy_type":"Product",
            "cause_of_death":"Cause","claim_amount":"Amount",
            "date_filed":"Filed","days_open":"Days Open",
            "aging_flag":"Aging","assigned_examiner":"Examiner"
        }).style.format({"Amount":"${:,.0f}","Days Open":"{:.0f}"}),
        use_container_width=True, hide_index=True,
    )
