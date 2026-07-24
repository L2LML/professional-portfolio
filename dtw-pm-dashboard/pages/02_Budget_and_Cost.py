"""02_Budget_and_Cost.py — Budget vs. actual by category, and contingency burn."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_projects, load_budget
from data.colors import (
    PROJECT_COLORS, PROJECT_ORDER, PROJECT_SHORT_NAMES, BASELINE, GRID,
    INK_SECONDARY, STATUS_GOOD, STATUS_WARNING, STATUS_CRITICAL,
)

st.set_page_config(page_title="Budget & Cost — DTW PM Dashboard", page_icon="💰", layout="wide")
st.title("💰 Budget & Cost Tracking")
st.caption("Budget vs. actual by cost category — sourced from each project's PM Tracking Workbook (Budget Tracker tab).")

projects = load_projects()
budget = load_budget()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        proj_row = projects[projects["project_id"] == project_id].iloc[0]
        color = PROJECT_COLORS[project_id]
        b = budget[budget["project_id"] == project_id].copy()
        b = b.sort_values("budgeted", ascending=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Approved Budget", f"${proj_row['total_budget']:,.0f}")
        c2.metric("Actual Spend to Date", f"${proj_row['current_actual_total']:,.0f}",
                   f"{proj_row['current_actual_total']/proj_row['total_budget']*100:.0f}% of budget",
                   delta_color="off")
        contingency_row = b[b["category"] == "Contingency"]
        cont_used = contingency_row["actual"].iloc[0] if not contingency_row.empty else 0
        c3.metric("Contingency Remaining", f"${proj_row['contingency'] - cont_used:,.0f}",
                   f"{cont_used/proj_row['contingency']*100:.0f}% used", delta_color="inverse")

        st.caption(f"**Budget status:** {proj_row['budget_status']}")
        st.divider()

        # ── Budgeted vs Actual by category ─────────────────────
        st.subheader("Budgeted vs. Actual by Cost Category")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=b["category"], x=b["budgeted"], name="Budgeted", orientation="h",
                              marker_color=BASELINE))
        fig.add_trace(go.Bar(y=b["category"], x=b["actual"], name="Actual to Date", orientation="h",
                              marker_color=color))
        fig.update_layout(
            barmode="group", height=90 + 34 * len(b), margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="$", gridcolor=GRID, tickprefix="$", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        st.plotly_chart(fig, width="stretch")

        # ── Variance table ──────────────────────────────────────
        st.subheader("Variance Detail")

        def style_variance(val):
            if val > 0:
                return f"color: {STATUS_CRITICAL}; font-weight: 600"
            if val < 0:
                return f"color: {STATUS_GOOD}"
            return f"color: {INK_SECONDARY}"

        def style_pct_used(val):
            if val >= 1.0:
                return f"color: {STATUS_CRITICAL}; font-weight: 600"
            if val >= 0.85:
                return f"color: {STATUS_WARNING}"
            return f"color: {INK_SECONDARY}"

        display = b.sort_values("budgeted", ascending=False).rename(columns={
            "category": "Category", "budgeted": "Budgeted", "committed": "Committed",
            "actual": "Actual to Date", "variance": "Variance", "pct_used": "% Used",
        })
        st.dataframe(
            display[["Category", "Budgeted", "Committed", "Actual to Date", "Variance", "% Used"]]
            .style.format({
                "Budgeted": "${:,.0f}", "Committed": "${:,.0f}", "Actual to Date": "${:,.0f}",
                "Variance": "${:,.0f}", "% Used": "{:.0%}",
            })
            .map(style_variance, subset=["Variance"])
            .map(style_pct_used, subset=["% Used"]),
            width="stretch", hide_index=True,
        )
