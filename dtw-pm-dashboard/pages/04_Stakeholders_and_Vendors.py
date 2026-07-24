"""04_Stakeholders_and_Vendors.py — Power/interest grid + vendor/contractor register."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_stakeholders, load_vendors
from data.colors import (
    PROJECT_COLORS, PROJECT_ORDER, PROJECT_SHORT_NAMES, STATUS_GOOD, STATUS_WARNING,
    BASELINE, GRID, INK_SECONDARY, INK_MUTED,
)

st.set_page_config(page_title="Stakeholders & Vendors — DTW PM Dashboard", page_icon="🤝", layout="wide")
st.title("🤝 Stakeholders & Vendors")
st.caption("Power/interest grid and vendor/contractor register — sourced from each project's PM Tracking Workbook.")

stakeholders = load_stakeholders()
vendors = load_vendors()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

VENDOR_RATING_COLOR = {"Meets expectations": STATUS_GOOD, "Watch — lead-time slip": STATUS_WARNING, "Not yet rated": BASELINE}

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        color = PROJECT_COLORS[project_id]
        s = stakeholders[stakeholders["project_id"] == project_id].copy()
        v = vendors[vendors["project_id"] == project_id].copy()

        st.subheader("Stakeholder Power/Interest Grid")
        fig = go.Figure()
        fig.add_annotation(x=1.25, y=3.3, text="Keep Satisfied", showarrow=False, font=dict(color=INK_MUTED, size=11))
        fig.add_annotation(x=2.75, y=3.3, text="Manage Closely", showarrow=False, font=dict(color=INK_MUTED, size=11))
        fig.add_annotation(x=1.25, y=0.7, text="Monitor", showarrow=False, font=dict(color=INK_MUTED, size=11))
        fig.add_annotation(x=2.75, y=0.7, text="Keep Informed", showarrow=False, font=dict(color=INK_MUTED, size=11))
        fig.add_vline(x=2, line=dict(color=GRID, width=1))
        fig.add_hline(y=2, line=dict(color=GRID, width=1))
        fig.add_trace(go.Scatter(
            x=s["interest_score"], y=s["influence_score"], mode="markers+text",
            marker=dict(size=22, color=color, line=dict(width=1, color="white")),
            text=[str(i + 1) for i in range(len(s))], textfont=dict(color="white", size=10),
            textposition="middle center",
            hovertext=[f"{row.stakeholder}<br>{row.interest_note}<br>Influence: {row.influence} · Interest: {row.interest}" for row in s.itertuples()],
            hoverinfo="text", showlegend=False,
        ))
        fig.update_layout(
            height=420, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Interest", range=[0.5, 3.5], tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], gridcolor=GRID),
            yaxis=dict(title="Influence", range=[0.5, 3.5], tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], gridcolor=GRID),
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("Numbers correspond to the stakeholder list row below (hover a bubble for detail).")

        st.dataframe(
            s.reset_index(drop=True).rename(columns={
                "stakeholder": "Stakeholder", "interest_note": "Why They Care",
                "influence": "Influence", "interest": "Interest",
            })[["Stakeholder", "Why They Care", "Influence", "Interest"]],
            width="stretch",
        )

        st.divider()
        st.subheader("Vendor / Contractor Register")
        v_sorted = v.sort_values("contract_value", ascending=True)
        fig2 = go.Figure(go.Bar(
            y=v_sorted["vendor"], x=v_sorted["contract_value"], orientation="h",
            marker_color=[VENDOR_RATING_COLOR.get(r, INK_MUTED) for r in v_sorted["rating"]],
            text=[f"${x:,.0f}" for x in v_sorted["contract_value"]], textposition="outside",
            textfont=dict(color=INK_SECONDARY),
        ))
        fig2.update_layout(
            height=80 + 40 * len(v_sorted), margin=dict(t=10, b=10, l=10, r=60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Contract Value ($)", gridcolor=GRID, tickprefix="$", tickformat=",.0f"),
            showlegend=False,
        )
        st.plotly_chart(fig2, width="stretch")
        st.caption(
            f"Bar color: <span style='color:{STATUS_GOOD};'>■</span> Meets expectations · "
            f"<span style='color:{STATUS_WARNING};'>■</span> Watch · "
            f"<span style='color:{BASELINE};'>■</span> Not yet rated",
            unsafe_allow_html=True,
        )

        st.dataframe(
            v.rename(columns={
                "vendor": "Vendor / Contractor", "scope": "Scope of Work",
                "contract_value": "Contract Value", "rating": "Performance Rating",
            })[["Vendor / Contractor", "Scope of Work", "Contract Value", "Performance Rating"]]
            .style.format({"Contract Value": "${:,.0f}"}),
            width="stretch", hide_index=True,
        )
