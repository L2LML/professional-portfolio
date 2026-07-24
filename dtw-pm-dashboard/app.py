"""
app.py — Portfolio Executive Summary.
Entry point for the DTW IT Center PM Dashboard.

Companion tool to the "DTW IT Center PM Toolkit"
(../dtw-it-center-pm-toolkit/) — this operationalizes the same schedule,
budget, risk, and stakeholder data captured in that toolkit's Word/Excel
documents into an interactive rollup across both example projects.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.load_data import (
    load_projects, load_budget, load_risks, load_monthly_progress,
)
from data.colors import (
    PROJECT_COLORS, PROJECT_ORDER, PROJECT_SHORT_NAMES, STATUS_COLORS,
    GRID, INK_SECONDARY, INK_MUTED, INK_PRIMARY, BASELINE, status_color,
)

st.set_page_config(
    page_title="DTW IT Center PM Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✈️ DTW IT Center — PM Portfolio Dashboard")
st.caption(
    "Companion tool to the *DTW IT Center PM Toolkit* · "
    "Construction/Infrastructure + Technology project rollup"
)

st.warning(
    "**⚠️ Portfolio Demo — Illustrative Scenario**\n\n"
    "Both projects are a self-directed, illustrative scenario prepared as candidate work for an "
    "Infrastructure/IT Project Manager role — not a record of an actual Metro Detroit Airport / "
    "Wayne County Airport Authority engagement. Every figure here traces back to the same "
    "Charter, PM Tracking Workbook, and Status/Closeout Report published in the companion "
    "[`dtw-it-center-pm-toolkit`](../dtw-it-center-pm-toolkit) folder; only the monthly time "
    "series between those documents' known checkpoints is synthesized, to give the trend charts "
    "something to show."
)
st.divider()

projects = load_projects()
budget = load_budget()
risks = load_risks()
monthly = load_monthly_progress()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")
sel_projects = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
st.sidebar.divider()
st.sidebar.caption(
    "📁 **Companion toolkit:** [`dtw-it-center-pm-toolkit/`](../dtw-it-center-pm-toolkit) — "
    "the Charter, PM Tracking Workbook, and Status/Closeout Report this dashboard visualizes."
)

if not sel_projects:
    st.info("Select at least one project in the sidebar.")
    st.stop()

proj_f = projects[projects["project_id"].isin(sel_projects)]
budget_f = budget[budget["project_id"].isin(sel_projects)]
risks_f = risks[risks["project_id"].isin(sel_projects)]
monthly_f = monthly[monthly["project_id"].isin(sel_projects)]

# ── Portfolio KPI row ───────────────────────────────────────────
total_budget = proj_f["total_budget"].sum()
total_actual = proj_f["current_actual_total"].sum()
total_contingency = proj_f["contingency"].sum()
contingency_used = budget_f[budget_f["category"] == "Contingency"]["actual"].sum()
open_risks_n = (risks_f["status"] != "Closed").sum()
weighted_pct = (proj_f["current_pct_complete"] * proj_f["total_budget"]).sum() / proj_f["total_budget"].sum()

st.subheader("Portfolio Key Performance Indicators")
st.caption(f"Rolled up across {len(sel_projects)} selected project(s), as of each project's current status-report month.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Combined Approved Budget", f"${total_budget:,.0f}",
          help="Sum of each selected project's total approved budget (GMP for construction).")
c2.metric("Combined Actual Spend", f"${total_actual:,.0f}", f"{total_actual/total_budget*100:.0f}% of budget",
          delta_color="off", help="Sum of actual-to-date spend as of each project's current status-report month.")
c3.metric("Contingency Remaining", f"${total_contingency - contingency_used:,.0f}",
          f"{contingency_used/total_contingency*100:.0f}% used", delta_color="inverse",
          help="Combined contingency reserve remaining across selected projects.")
c4.metric("Weighted Schedule % Complete", f"{weighted_pct:.0f}%",
          help="Each project's % complete, weighted by its share of combined budget.")
c5.metric("Open Risks", f"{open_risks_n}", help="Risks not yet in Closed status, across selected projects.")

st.divider()

# ── Project status cards ────────────────────────────────────────
st.subheader("Project Status")
cols = st.columns(len(proj_f))
for col, (_, row) in zip(cols, proj_f.iterrows()):
    color = PROJECT_COLORS[row["project_id"]]
    with col:
        st.markdown(
            f"<div style='border-left:6px solid {color}; padding:4px 0 4px 14px;'>"
            f"<span style='color:{color}; font-weight:700; font-size:1.05rem;'>{row['project_type']}</span><br>"
            f"<span style='color:{INK_SECONDARY};'>{row['project_name']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"Overall: <span style='color:{status_color(row['overall_status'])}; font-weight:700;'>{row['overall_status']}</span> · "
            f"Month {row['current_month']} of {row['duration_months']}",
            unsafe_allow_html=True,
        )
        st.progress(int(row["current_pct_complete"]), text=f"{row['current_pct_complete']}% schedule complete")
        st.caption(f"**Schedule:** {row['schedule_status']}")
        st.caption(f"**Budget:** {row['budget_status']}")
        st.caption(f"**Sponsor:** {row['sponsor']} · **PM:** {row['project_manager']}")

st.divider()

# ── Trend charts: small multiples, one per project, per metric ─
st.subheader("Cumulative Spend — Planned vs. Actual")
st.caption("Dashed gray = baseline plan (smooth S-curve to total budget). Solid = actual. Vertical marker = the status-report snapshot month captured in the toolkit's documents.")

spend_cols = st.columns(len(proj_f))
for col, project_id in zip(spend_cols, proj_f["project_id"]):
    g = monthly_f[monthly_f["project_id"] == project_id]
    color = PROJECT_COLORS[project_id]
    snapshot_month = int(proj_f.loc[proj_f["project_id"] == project_id, "current_month"].iloc[0])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["month"], y=g["planned_cum_spend"], mode="lines", name="Planned",
                              line=dict(color=BASELINE, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=g["month"], y=g["actual_cum_spend"], mode="lines", name="Actual",
                              line=dict(color=color, width=2.5)))
    fig.add_shape(type="line", xref="x", yref="paper", x0=snapshot_month, x1=snapshot_month, y0=0, y1=1,
                  line=dict(dash="dot", color=INK_MUTED, width=1.5))
    fig.add_annotation(x=snapshot_month, y=1.06, yref="paper", text="Status report", showarrow=False,
                        font=dict(color=INK_MUTED, size=10))
    fig.update_layout(
        title=PROJECT_SHORT_NAMES.get(project_id, project_id), height=320,
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Month", showgrid=False),
        yaxis=dict(title="Cumulative $", gridcolor=GRID, tickprefix="$", tickformat=",.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    col.plotly_chart(fig, width="stretch")

st.subheader("Schedule — Cumulative % Complete, Planned vs. Actual")
sched_cols = st.columns(len(proj_f))
for col, project_id in zip(sched_cols, proj_f["project_id"]):
    g = monthly_f[monthly_f["project_id"] == project_id]
    color = PROJECT_COLORS[project_id]
    snapshot_month = int(proj_f.loc[proj_f["project_id"] == project_id, "current_month"].iloc[0])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["month"], y=g["planned_cum_pct"], mode="lines", name="Planned",
                              line=dict(color=BASELINE, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=g["month"], y=g["actual_cum_pct"], mode="lines", name="Actual",
                              line=dict(color=color, width=2.5)))
    fig.add_shape(type="line", xref="x", yref="paper", x0=snapshot_month, x1=snapshot_month, y0=0, y1=1,
                  line=dict(dash="dot", color=INK_MUTED, width=1.5))
    fig.update_layout(
        title=PROJECT_SHORT_NAMES.get(project_id, project_id), height=300,
        margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Month", showgrid=False),
        yaxis=dict(title="% Complete", gridcolor=GRID, range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    col.plotly_chart(fig, width="stretch")

st.divider()

# ── Risks to watch ──────────────────────────────────────────────
st.subheader("⚠️ Risks to Watch")
st.caption("Open or monitored risks across selected projects, ranked by score (probability × impact).")

watch = risks_f[risks_f["status"] != "Closed"].copy()
watch["Project"] = watch["project_id"].map(PROJECT_SHORT_NAMES)
watch = watch.sort_values("score", ascending=False)


def style_score(val):
    if val >= 12:
        return f"color: {status_color('red')}; font-weight: 600"
    if val >= 6:
        return f"color: {status_color('yellow')}; font-weight: 600"
    return f"color: {status_color('green')}; font-weight: 600"


st.dataframe(
    watch.rename(columns={
        "risk_id": "ID", "description": "Description", "category": "Category",
        "score": "Score", "response": "Response Strategy", "owner": "Owner", "status": "Status",
    })[["Project", "ID", "Description", "Category", "Score", "Response Strategy", "Owner", "Status"]]
    .style.map(style_score, subset=["Score"]),
    width="stretch", hide_index=True,
)
