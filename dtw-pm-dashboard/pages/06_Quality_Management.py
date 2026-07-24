"""06_Quality_Management.py — Quality Control checklist status per project."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_quality
from data.colors import (
    PROJECT_COLORS, PROJECT_ORDER, PROJECT_SHORT_NAMES, STATUS_GOOD, BASELINE, INK_MUTED,
)

st.set_page_config(page_title="Quality Management — DTW PM Dashboard", page_icon="✅", layout="wide")
st.title("✅ Quality Management")
st.caption("Quality Control checklist — inspection/acceptance-test checkpoints and status, sourced from each project's PM Tracking Workbook (Quality_Checklist tab).")

quality = load_quality()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

STATUS_COLOR = {"Pass": STATUS_GOOD, "In Progress": None, "Not Started": BASELINE}

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        color = PROJECT_COLORS[project_id]
        q = quality[quality["project_id"] == project_id].copy()

        counts = q["status"].value_counts()
        total = len(q)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Checkpoints Tracked", total)
        c2.metric("Passed", int(counts.get("Pass", 0)), f"{counts.get('Pass', 0)/total*100:.0f}%", delta_color="off")
        c3.metric("In Progress", int(counts.get("In Progress", 0)))
        c4.metric("Not Started", int(counts.get("Not Started", 0)))

        st.divider()
        st.subheader("Checkpoint Status")
        q_display = q.iloc[::-1]
        bar_colors = [STATUS_COLOR[s] or color for s in q_display["status"]]
        fig = go.Figure(go.Bar(
            y=q_display["checkpoint"], x=[1] * len(q_display), orientation="h",
            marker_color=bar_colors,
            text=q_display["status"], textposition="inside", insidetextanchor="start",
            textfont=dict(color="white", size=11),
            hovertext=[f"{row.checkpoint}<br>{row.category} · Target: {row.target}<br>Owner: {row.owner}" for row in q_display.itertuples()],
            hoverinfo="text",
        ))
        fig.update_layout(
            height=70 + 42 * len(q_display), margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, range=[0, 1]),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"Bar color: <span style='color:{STATUS_GOOD};'>■</span> Pass · "
            f"<span style='color:{color};'>■</span> In Progress · "
            f"<span style='color:{BASELINE};'>■</span> Not Started",
            unsafe_allow_html=True,
        )

        st.subheader("Quality Control Checklist Detail")
        STATUS_TEXT_COLOR = {"Pass": STATUS_GOOD, "In Progress": color, "Not Started": INK_MUTED}

        def style_status(val):
            return f"color: {STATUS_TEXT_COLOR.get(val, INK_MUTED)}; font-weight: 600"

        st.dataframe(
            q.rename(columns={
                "checkpoint": "Checkpoint", "category": "Category", "acceptance_criteria": "Acceptance Criteria",
                "method": "Inspection / Test Method", "status": "Status", "target": "Target", "owner": "Owner",
            })[["Checkpoint", "Category", "Acceptance Criteria", "Inspection / Test Method", "Status", "Target", "Owner"]]
            .style.map(style_status, subset=["Status"]),
            width="stretch", hide_index=True,
        )
