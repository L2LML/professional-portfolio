"""
app.py — Executive Summary.
Entry point for the Healthcare Burnout KPI Dashboard.

Companion tool to the "Closing the Adherence Gap" DMAIC case study
(../healthcare-burnout-dmaic/) — this operationalizes the case study's
Measure phase: what a real quarterly burnout survey + adherence audit
would surface for leadership.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_survey
from data.colors import (
    DRIVER_COLORS, DRIVER_ORDER, GRID, INK_SECONDARY, INK_MUTED, INK_PRIMARY,
    STATUS_GOOD, STATUS_WARNING, STATUS_CRITICAL, SERIES_NEUTRAL,
)

st.set_page_config(
    page_title="Healthcare Burnout KPI Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🩺 Healthcare Burnout & Adherence KPI Dashboard")
st.caption(
    "Companion tool to the *Closing the Adherence Gap* DMAIC case study · "
    "Quarterly survey + shift-level adherence audit"
)

st.warning(
    "**⚠️ Portfolio Demo — Synthetic Sample Data**\n\n"
    "All data shown is randomly generated for demonstration purposes only. No real staff, "
    "patients, or hospital records are represented. In a production deployment, this dashboard "
    "connects to a validated MBI/Mini-Z burnout survey and an EHR- or app-based end-of-shift "
    "adherence checklist — both proposed in the companion DMAIC case study."
)
st.divider()

survey = load_survey()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")
quarters = sorted(survey["quarter"].unique().tolist())
sel_quarters = st.sidebar.multiselect("Quarter", quarters, default=quarters)
units = sorted(survey["unit"].unique().tolist())
sel_units = st.sidebar.multiselect("Unit", units, default=units)
rotations = sorted(survey["rotation_type"].unique().tolist())
sel_rotations = st.sidebar.multiselect("Rotation Cadence", rotations, default=rotations)

filtered = survey[
    survey["quarter"].isin(sel_quarters)
    & survey["unit"].isin(sel_units)
    & survey["rotation_type"].isin(sel_rotations)
]
st.sidebar.divider()
st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(survey):,} survey responses")
st.sidebar.divider()
st.sidebar.caption(
    "📊 **Companion deck:** [`healthcare-burnout-dmaic/`](../healthcare-burnout-dmaic/) — "
    "the full DMAIC case study this dashboard operationalizes."
)

if filtered.empty:
    st.info("No responses match the current filters.")
    st.stop()

# ── Current vs prior quarter (within current filters) ─────────
qnums_present = sorted(filtered["quarter_num"].unique().tolist())
curr_qnum = qnums_present[-1]
prev_qnum = qnums_present[-2] if len(qnums_present) > 1 else curr_qnum
curr_df = filtered[filtered["quarter_num"] == curr_qnum]
prev_df = filtered[filtered["quarter_num"] == prev_qnum]


def delta(curr, prev, invert=True):
    if prev == 0 or curr_qnum == prev_qnum:
        return None, "off"
    pct = (curr - prev) / abs(prev) * 100
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.1f}% vs {quarters[prev_qnum] if prev_qnum < len(quarters) else ''}", (
        "inverse" if invert else "normal"
    )


avg_burnout = curr_df["burnout_score"].mean()
avg_burnout_prev = prev_df["burnout_score"].mean()
avg_adherence = curr_df["adherence_checklist_pct"].mean()
avg_adherence_prev = prev_df["adherence_checklist_pct"].mean()
turnover_rate = curr_df["turned_over"].mean() * 100
turnover_rate_prev = prev_df["turned_over"].mean() * 100
avg_gap = curr_df["accountability_gap_score"].mean()
avg_gap_prev = prev_df["accountability_gap_score"].mean()
avg_safety = curr_df["safety_risk_score"].mean()

b_delta, b_color = delta(avg_burnout, avg_burnout_prev, invert=True)
a_delta, a_color = delta(avg_adherence, avg_adherence_prev, invert=False)
t_delta, t_color = delta(turnover_rate, turnover_rate_prev, invert=True)
g_delta, g_color = delta(avg_gap, avg_gap_prev, invert=True)

st.subheader("Key Performance Indicators")
st.caption(
    f"Current period: **{quarters[curr_qnum]}**. Trend arrows compare against the prior "
    f"selected quarter. <span style='color:{STATUS_GOOD};font-weight:600;'>improving</span> / "
    f"<span style='color:{STATUS_CRITICAL};font-weight:600;'>worsening</span>.",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Avg Burnout Score", f"{avg_burnout:.1f} / 100", delta=b_delta, delta_color=b_color,
          help="Composite MBI/Mini-Z-style score — exhaustion, depersonalization, accomplishment. Lower is better.")
c2.metric("Adherence Rate", f"{avg_adherence:.1f}%", delta=a_delta, delta_color=a_color,
          help="Average end-of-shift checklist completion (pre-, during-, post-shift). Higher is better.")
c3.metric("Turnover Rate", f"{turnover_rate:.1f}%", delta=t_delta, delta_color=t_color,
          help="Share of staff who left in the current quarter.")
c4.metric("Accountability Gap", f"{avg_gap:.1f} / 100", delta=g_delta, delta_color=g_color,
          help="Variation in adherence within a unit — the measurable form of \"some do it right, some don't.\" Lower is better.")
c5.metric("Safety Risk Index", f"{avg_safety:.1f} / 100", delta_color="off",
          help="Perceived exposure to aggressive or unpredictable patient behavior.")

st.divider()

# ── Root-cause driver breakdown + trend ────────────────────────
left, right = st.columns([1, 1.4])

with left:
    st.subheader("The Four Unmotivating Characteristics")
    st.caption("Average driver index for the current period — the root causes from the DMAIC analysis, made measurable.")
    driver_map = {
        "Workload & Staffing": curr_df["workload_index"].mean(),
        "Accountability": curr_df["accountability_gap_score"].mean(),
        "Reward": curr_df["reward_gap_score"].mean(),
        "Safety": curr_df["safety_risk_score"].mean(),
    }
    fig_drivers = go.Figure(go.Bar(
        x=[driver_map[d] for d in DRIVER_ORDER],
        y=DRIVER_ORDER,
        orientation="h",
        marker_color=[DRIVER_COLORS[d] for d in DRIVER_ORDER],
        text=[f"{driver_map[d]:.0f}" for d in DRIVER_ORDER],
        textposition="outside",
        textfont=dict(color=INK_SECONDARY),
    ))
    fig_drivers.update_layout(
        height=300, margin=dict(t=10, b=10, l=10, r=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 100], gridcolor=GRID, title="Index (0–100, higher = worse)"),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig_drivers, width="stretch")

with right:
    st.subheader("Burnout Trend — Pilot Launch Marked")
    st.caption("Quarterly average burnout score across all selected quarters. Dashed line marks the checklist + tied-recognition pilot launch.")
    trend = filtered.groupby(["quarter_num"]).agg(
        burnout=("burnout_score", "mean")
    ).reset_index()
    trend["quarter"] = trend["quarter_num"].apply(lambda i: quarters[i])

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend["quarter"], y=trend["burnout"], mode="lines+markers",
        line=dict(color=SERIES_NEUTRAL, width=2),
        marker=dict(size=8),
        name="Avg Burnout Score",
    ))
    if "2025-Q4" in trend["quarter"].values:
        pilot_pos = trend.index[trend["quarter"] == "2025-Q4"][0]
        fig_trend.add_shape(
            type="line", xref="x", yref="paper",
            x0=pilot_pos, x1=pilot_pos, y0=0, y1=1,
            line=dict(dash="dash", color=INK_MUTED, width=1.5),
        )
        fig_trend.add_annotation(
            x=pilot_pos, y=1.05, yref="paper", text="Pilot launch",
            showarrow=False, font=dict(color=INK_MUTED, size=11),
        )
    fig_trend.update_layout(
        height=300, margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Burnout Score", range=[0, 100]),
        showlegend=False,
    )
    st.plotly_chart(fig_trend, width="stretch")

st.divider()

# ── Units to watch ──────────────────────────────────────────────
st.subheader("⚠️ Units to Watch")
st.caption("Current-period units ranked by combined burnout and adherence risk.")

unit_summary = curr_df.groupby("unit").agg(
    avg_burnout=("burnout_score", "mean"),
    avg_adherence=("adherence_checklist_pct", "mean"),
    accountability_gap=("accountability_gap_score", "mean"),
    turnover=("turned_over", "mean"),
    headcount=("staff_id", "nunique"),
).reset_index()
unit_summary["turnover"] = (unit_summary["turnover"] * 100).round(1)
unit_summary = unit_summary.sort_values("avg_burnout", ascending=False)


def status_flag(burnout):
    if burnout >= 55:
        return "Critical"
    if burnout >= 45:
        return "Watch"
    return "Stable"


# Real hex, not emoji — an emoji circle renders in the browser's fixed color,
# not this palette, so it wouldn't match STATUS_CRITICAL/WARNING/GOOD elsewhere.
STATUS_FLAG_COLORS = {"Critical": STATUS_CRITICAL, "Watch": STATUS_WARNING, "Stable": STATUS_GOOD}


def style_status_flag(val):
    return f"color: {STATUS_FLAG_COLORS.get(val, INK_PRIMARY)}; font-weight: 600"


unit_summary["Status"] = unit_summary["avg_burnout"].apply(status_flag)
st.dataframe(
    unit_summary.rename(columns={
        "unit": "Unit", "avg_burnout": "Avg Burnout", "avg_adherence": "Adherence %",
        "accountability_gap": "Accountability Gap", "turnover": "Turnover %", "headcount": "Headcount",
    }).style.format({
        "Avg Burnout": "{:.1f}", "Adherence %": "{:.1f}%",
        "Accountability Gap": "{:.1f}", "Turnover %": "{:.1f}%",
    }).map(style_status_flag, subset=["Status"]),
    width="stretch", hide_index=True,
)
