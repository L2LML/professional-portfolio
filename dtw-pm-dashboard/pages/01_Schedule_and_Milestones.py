"""01_Schedule_and_Milestones.py — WBS/Gantt view + milestone tracker per project."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_projects, load_schedule, load_milestones
from data.colors import (
    PROJECT_COLORS, PROJECT_ORDER, PROJECT_SHORT_NAMES, STATUS_GOOD, BASELINE,
    GRID, INK_SECONDARY, INK_MUTED,
)

st.set_page_config(page_title="Schedule & Milestones — DTW PM Dashboard", page_icon="🗓️", layout="wide")
st.title("🗓️ Schedule & Milestones")
st.caption("Work Breakdown Structure, task-level progress, and milestone tracking — sourced from each project's PM Tracking Workbook.")

projects = load_projects()
schedule = load_schedule()
milestones = load_milestones()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

STATUS_BAR_COLOR = {"Complete": STATUS_GOOD, "In Progress": None, "Not Started": BASELINE}

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        proj_row = projects[projects["project_id"] == project_id].iloc[0]
        color = PROJECT_COLORS[project_id]
        sched = schedule[schedule["project_id"] == project_id].copy()
        mstones = milestones[milestones["project_id"] == project_id].copy()

        st.markdown(
            f"**{proj_row['project_name']}** · {proj_row['duration_months']}-month schedule · "
            f"currently Month {proj_row['current_month']} ({proj_row['current_pct_complete']}% complete)"
        )

        # ── Gantt-style bar chart ─────────────────────────────
        sched = sched.iloc[::-1].reset_index(drop=True)  # first task at top
        bar_colors = [STATUS_BAR_COLOR[s] or color for s in sched["status"]]
        labels = sched["phase"] + " — " + sched["task"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels, x=(sched["end_month"] - sched["start_month"]).clip(lower=0.3),
            base=sched["start_month"], orientation="h",
            marker_color=bar_colors,
            text=[f"{p}%" for p in sched["pct_complete"]],
            textposition="outside", textfont=dict(color=INK_SECONDARY, size=11),
            hovertext=[
                f"{row.task}<br>Owner: {row.owner}<br>Month {row.start_month}–{row.end_month} · {row.pct_complete}% complete · {row.status}"
                for row in sched.itertuples()
            ],
            hoverinfo="text",
        ))
        fig.update_layout(
            height=90 + 32 * len(sched), margin=dict(t=10, b=10, l=10, r=60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Month", gridcolor=GRID, range=[0, proj_row["duration_months"] + 1]),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"Bar color: <span style='color:{STATUS_GOOD};'>■</span> Complete · "
            f"<span style='color:{color};'>■</span> In Progress · "
            f"<span style='color:{BASELINE};'>■</span> Not Started",
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Milestones ─────────────────────────────────────────
        st.subheader("Milestones")
        m_color = {"Complete": STATUS_GOOD, "In Progress": color, "Not Started": INK_MUTED}

        def style_status(val):
            return f"color: {m_color.get(val, INK_MUTED)}; font-weight: 600"

        st.dataframe(
            mstones.rename(columns={"milestone": "Milestone", "month": "Target Month", "status": "Status"})
            [["Milestone", "Target Month", "Status"]]
            .style.map(style_status, subset=["Status"]),
            width="stretch", hide_index=True,
        )
