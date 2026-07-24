"""03_Risk_and_Issues.py — Risk heatmap + risk register + issue/change log."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_risks, load_issues
from data.colors import (
    PROJECT_ORDER, PROJECT_SHORT_NAMES, STATUS_GOOD, STATUS_WARNING, STATUS_CRITICAL,
    GRID, INK_SECONDARY, INK_MUTED,
)

st.set_page_config(page_title="Risk & Issues — DTW PM Dashboard", page_icon="⚠️", layout="wide")
st.title("⚠️ Risk & Issue Management")
st.caption("Risk register (probability × impact) and issue/change log — sourced from each project's PM Tracking Workbook.")

risks = load_risks()
issues = load_issues()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

RISK_STATUS_COLOR = {"Open": STATUS_CRITICAL, "Monitoring": STATUS_WARNING, "Closed": STATUS_GOOD}

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        r = risks[risks["project_id"] == project_id].copy()
        i = issues[issues["project_id"] == project_id].copy()

        st.subheader("Risk Heatmap")
        st.caption("Bubble size = score (probability × impact). Color = status.")
        fig = go.Figure()
        for status, grp in r.groupby("status"):
            fig.add_trace(go.Scatter(
                x=grp["probability"], y=grp["impact"], mode="markers+text",
                marker=dict(size=grp["score"] * 4.5, color=RISK_STATUS_COLOR.get(status, INK_MUTED),
                            line=dict(width=1, color="white")),
                text=grp["risk_id"], textposition="middle center",
                textfont=dict(color="white", size=10),
                name=status,
                hovertext=[f"{row.risk_id}: {row.description}<br>Score {row.score} · {row.owner}" for row in grp.itertuples()],
                hoverinfo="text",
            ))
        fig.update_layout(
            height=420, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Probability (1–5)", range=[0.5, 5.5], dtick=1, gridcolor=GRID),
            yaxis=dict(title="Impact (1–5)", range=[0.5, 5.5], dtick=1, gridcolor=GRID),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("Risk Register")

        def style_risk_status(val):
            return f"color: {RISK_STATUS_COLOR.get(val, INK_MUTED)}; font-weight: 600"

        st.dataframe(
            r.sort_values("score", ascending=False).rename(columns={
                "risk_id": "ID", "description": "Description", "category": "Category",
                "probability": "Prob.", "impact": "Impact", "score": "Score",
                "response": "Response Strategy", "owner": "Owner", "status": "Status",
            })[["ID", "Description", "Category", "Prob.", "Impact", "Score", "Response Strategy", "Owner", "Status"]]
            .style.map(style_risk_status, subset=["Status"]),
            width="stretch", hide_index=True,
        )

        st.divider()
        st.subheader("Issue & Change Log")
        ISSUE_STATUS_COLOR = {
            "Open": STATUS_CRITICAL, "Under Review": STATUS_WARNING,
            "Resolved": STATUS_GOOD, "Approved": STATUS_GOOD,
        }

        def style_issue_status(val):
            return f"color: {ISSUE_STATUS_COLOR.get(val, INK_MUTED)}; font-weight: 600"

        st.dataframe(
            i.rename(columns={
                "item_id": "ID", "type": "Type", "description": "Description",
                "month_raised": "Month Raised", "owner": "Owner", "priority": "Priority", "status": "Status",
            })[["ID", "Type", "Description", "Month Raised", "Owner", "Priority", "Status"]]
            .style.map(style_issue_status, subset=["Status"]),
            width="stretch", hide_index=True,
        )
