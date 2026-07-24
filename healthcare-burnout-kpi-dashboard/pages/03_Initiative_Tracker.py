"""pages/03_Initiative_Tracker.py — Improve/Control phase tracker, tied to the DMAIC deck."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_survey, load_initiatives
from data.colors import (
    INITIATIVE_STATUS_COLORS, GRID, DRIVER_COLORS, INK_PRIMARY, INK_SECONDARY,
    STATUS_GOOD, STATUS_CRITICAL,
)

st.set_page_config(page_title="Initiative Tracker", page_icon="📋", layout="wide")
st.title("📋 Initiative Tracker")
st.caption("The Improve-phase initiatives from the DMAIC case study, with rollout status and early pilot impact.")

survey = load_survey()
initiatives = load_initiatives()

st.divider()


def status_tile(label, value, hex_color):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px;">
          <span style="width:12px;height:12px;border-radius:50%;background:{hex_color};
                       display:inline-block;flex-shrink:0;"></span>
          <span style="font-size:14px;color:{INK_SECONDARY};">{label}</span>
        </div>
        <div style="font-size:2.25rem;font-weight:600;color:{INK_PRIMARY};line-height:1.2;">{value}</div>
        """,
        unsafe_allow_html=True,
    )


# Same hex values as the chart below — a plain emoji circle (🟢🟡🔴) renders in
# the browser's fixed color, not this palette, which is exactly why it looked
# mismatched next to the "By Cost Tier" chart.
status_counts = initiatives["status"].value_counts()
c1, c2, c3 = st.columns(3)
with c1:
    status_tile("Rolled Out", int(status_counts.get("Rolled Out", 0)), INITIATIVE_STATUS_COLORS["Rolled Out"])
with c2:
    status_tile("Piloting", int(status_counts.get("Piloting", 0)), INITIATIVE_STATUS_COLORS["Piloting"])
with c3:
    status_tile("Not Started", int(status_counts.get("Not Started", 0)), INITIATIVE_STATUS_COLORS["Not Started"])

st.divider()

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Initiative Status")
    st.caption("Every initiative proposed in the case study's Improve phase, current rollout state.")
    display = initiatives.rename(columns={
        "initiative": "Initiative", "phase": "Phase", "cost_tier": "Cost Tier",
        "status": "Status", "expected_impact": "Expected Impact", "feasibility": "Feasibility",
    })[["Initiative", "Phase", "Cost Tier", "Status", "Feasibility", "Expected Impact"]]

    def style_status(val):
        color = INITIATIVE_STATUS_COLORS.get(val, "#000000")
        return f"color: {color}; font-weight: 600"

    st.dataframe(
        display.style.map(style_status, subset=["Status"]),
        width="stretch", hide_index=True, height=380,
    )

with right:
    st.subheader("By Cost Tier")
    st.caption("Most initiatives currently active are low-cost — the higher-cost, more durable levers are still pending.")
    tier_status = initiatives.groupby(["cost_tier", "status"]).size().reset_index(name="count")
    fig = go.Figure()
    for status, color in INITIATIVE_STATUS_COLORS.items():
        sub = tier_status[tier_status["status"] == status]
        fig.add_trace(go.Bar(
            x=sub["cost_tier"], y=sub["count"], name=status, marker_color=color,
        ))
    fig.update_layout(
        barmode="stack", height=380, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, categoryorder="array", categoryarray=["Low", "Medium", "High"]),
        yaxis=dict(gridcolor=GRID, title="Initiatives", dtick=1),
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig, width="stretch")

st.divider()

# ── Pilot impact: before vs after ────────────────────────────────
st.subheader("Pilot Impact: Checklist + Tied Recognition")
st.caption("2025-Q4 launch. Comparing the four quarters before the pilot to the two quarters since.")

survey_sorted = survey.copy()
pre = survey_sorted[~survey_sorted["pilot_active"]]
post = survey_sorted[survey_sorted["pilot_active"]]

metrics = {
    "Avg Burnout Score": ("burnout_score", True),
    "Adherence Rate (%)": ("adherence_checklist_pct", False),
    "Accountability Gap": ("accountability_gap_score", True),
    "Turnover Rate (%)": ("turned_over", True),
}

cols = st.columns(4)
for col, (label, (metric_col, inverse)) in zip(cols, metrics.items()):
    pre_val = pre[metric_col].mean() * (100 if metric_col == "turned_over" else 1)
    post_val = post[metric_col].mean() * (100 if metric_col == "turned_over" else 1)
    pct_change = (post_val - pre_val) / pre_val * 100 if pre_val else 0
    good = (pct_change < 0) if inverse else (pct_change > 0)
    # Real hex, not an emoji arrow — same reason as the status tiles above.
    delta_color = STATUS_GOOD if good else STATUS_CRITICAL
    with col:
        st.markdown(
            f"""
            <div style="font-size:14px;color:{INK_SECONDARY};margin-bottom:2px;">{label}</div>
            <div style="font-size:2.0rem;font-weight:600;color:{INK_PRIMARY};line-height:1.2;">{post_val:.1f}</div>
            <div style="font-size:13px;color:{delta_color};font-weight:600;">{pct_change:+.1f}% vs. pre-pilot</div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "Early pilot signal only — not a controlled trial. The case study's Control phase proposes "
    "comparing against a held-out unit before scaling."
)
