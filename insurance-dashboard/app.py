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

st.title("🏦 Lisa's Insurance Claims Dashboard")
st.caption("Life Insurance Operations · Built with PostgreSQL → Python ETL → Streamlit")

st.warning(
    "**⚠️ Portfolio Demo — Synthetic Sample Data**\n\n"
    "All data shown in this dashboard is randomly generated for demonstration purposes only. "
    "No real policyholders, claims, or financial figures are represented. "
    "In a production environment, this dashboard connects directly to the "
    "**Life Insurance Claims PostgreSQL database** via the **Python ETL pipeline** — "
    "both of which are included in this portfolio. "
    "See the full project at [github.com/L2LML/professional-portfolio]"
    "(https://github.com/L2LML/professional-portfolio)."
)
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

# ── Computed metrics — current period ────────────────────────
total_claims   = len(filtered)
total_paid     = filtered[filtered["claim_status"] == "paid"]["claim_amount"].sum()
total_premiums = (pol["annual_premium"] * pol["years_in_force"].clip(lower=1)).sum()
loss_ratio     = total_paid / total_premiums if total_premiums > 0 else 0
avg_processing = filtered["days_to_decision"].dropna().mean()

decided      = filtered[filtered["claim_status"].isin(["paid","approved","denied"])]
approval_rate = (
    len(decided[decided["claim_status"].isin(["paid","approved"])]) /
    max(len(decided), 1)
)
open_exposure   = filtered[
    filtered["claim_status"].isin(["pending","under_review"])
]["claim_amount"].sum()
pending_reserve = open_exposure * approval_rate

decided_claims    = filtered[filtered["days_to_decision"].notna()]
sla_compliant_pct = (
    (decided_claims["days_to_decision"] <= 45).sum() /
    max(len(decided_claims), 1) * 100
)

# ── Year-over-year trend calculations ────────────────────────
# Find the two most recent years with PAID or DECIDED claims (excludes open claims)
decided = filtered[filtered["claim_status"].isin(["paid","approved","denied"])]
years_with_data = sorted(decided["claim_year"].dropna().unique().tolist(), reverse=True)
curr_yr = int(years_with_data[0]) if len(years_with_data) > 0 else 2024
prev_yr = int(years_with_data[1]) if len(years_with_data) > 1 else curr_yr - 1

curr_df = filtered[filtered["claim_year"] == curr_yr]
prev_df = filtered[filtered["claim_year"] == prev_yr]

def safe_delta(curr_val, prev_val, fmt=".0f", invert=False):
    """Return (delta_str, delta_color) for st.metric."""
    if prev_val == 0:
        return None, "off"
    delta = curr_val - prev_val
    pct   = delta / abs(prev_val) * 100
    sign  = "+" if pct > 0 else ""
    label = f"{sign}{pct:.1f}% vs {prev_yr}"
    # For inverse metrics: rising = bad = red, falling = good = green
    color = "inverse" if invert else "normal"
    return label, color

# Claims filed trend (more claims = more exposure = inverse color)
curr_claims_n = len(curr_df)
prev_claims_n = len(prev_df)
claims_delta, claims_color = safe_delta(curr_claims_n, max(prev_claims_n,1), invert=True)

# Paid out trend (more paid = worse = inverse)
curr_paid_n = curr_df[curr_df["claim_status"]=="paid"]["claim_amount"].sum()
prev_paid_n = prev_df[prev_df["claim_status"]=="paid"]["claim_amount"].sum()
paid_delta, paid_color = safe_delta(curr_paid_n, max(prev_paid_n,1), invert=True)

# Loss ratio trend (higher = worse = inverse)
prev_paid_all = filtered[
    (filtered["claim_year"] == prev_yr) &
    (filtered["claim_status"] == "paid")
]["claim_amount"].sum()
prev_lr = prev_paid_all / (total_premiums * 0.5) if total_premiums > 0 else 0
lr_delta_val = loss_ratio - prev_lr
lr_delta_str = f"{'↑' if lr_delta_val > 0 else '↓'} {abs(lr_delta_val):.2f} vs {prev_yr}"
lr_delta_color = "inverse"   # higher loss ratio = red arrow

# Avg decision time trend (faster = better = inverse)
curr_avg = curr_df["days_to_decision"].dropna().mean()
prev_avg = prev_df["days_to_decision"].dropna().mean()
avg_delta, avg_color = safe_delta(
    curr_avg if pd.notna(curr_avg) else 0,
    max(prev_avg if pd.notna(prev_avg) else 1, 1),
    invert=True
)

# Loss ratio zone label
lr_label = (
    "🟢 Healthy"  if loss_ratio < 0.70 else
    "🟡 Watch"    if loss_ratio < 0.85 else
    "🔴 High Risk"
)

# ── KPI Cards with trend arrows ───────────────────────────────
st.subheader("Key Performance Indicators")
st.caption(f"Trend arrows compare **{curr_yr}** vs **{prev_yr}**. "
           "🟢 Green = improving. 🔴 Red = worsening.")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Claims Filed", f"{total_claims:,}",
    delta=claims_delta, delta_color=claims_color,
    help="Total claims across all years. Arrow = current year vs prior year."
)
c2.metric(
    "Portfolio Loss Ratio", f"{loss_ratio:.2f}",
    delta=lr_delta_str, delta_color=lr_delta_color,
    help="Claims paid ÷ total premiums collected. Below 0.70 = healthy."
)
c3.metric(
    "Total Paid Out", f"${total_paid/1_000_000:.2f}M",
    delta=paid_delta, delta_color=paid_color,
    help="Dollar amount disbursed to beneficiaries."
)
c4.metric(
    "Avg Decision Time",
    f"{avg_processing:.0f} days" if pd.notna(avg_processing) else "—",
    delta=avg_delta, delta_color=avg_color,
    help="Average days from claim filing to approval or denial. Lower is better."
)
c5.metric(
    "Pending Reserve Est.", f"${pending_reserve:,.0f}",
    delta=f"{lr_label}  ·  SLA {sla_compliant_pct:.0f}%",
    delta_color="off",
    help="Estimated liability on open claims × historical approval rate."
)

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
    st.plotly_chart(fig_donut, width="stretch")

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
    # Use the same curr_yr/prev_yr calculated above for KPI cards
    curr = monthly[monthly["claim_year"] == curr_yr].set_index("claim_month")["count"]
    prev = monthly[monthly["claim_year"] == prev_yr].set_index("claim_month")["count"]
    months = list(range(1, 13))
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig_yoy = go.Figure()
    # Prior year: gray bars in background (reference)
    fig_yoy.add_trace(go.Bar(
        x=month_labels,
        y=[prev.get(m, 0) for m in months],
        name=str(prev_yr),
        marker_color=GRAY,
        opacity=0.5,
    ))
    # Current year: navy bars in foreground (what we're watching)
    fig_yoy.add_trace(go.Bar(
        x=month_labels,
        y=[curr.get(m, 0) for m in months],
        name=str(curr_yr),
        marker_color=NAVY,
    ))
    fig_yoy.update_layout(
        barmode="group",
        height=320, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Claims Filed"),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_yoy, width="stretch")

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
        width="stretch", hide_index=True,
    )
