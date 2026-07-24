"""pages/02_Adherence_and_Rotation.py — Adherence and the rotation-cadence tradeoff."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_survey, load_adherence_log
from data.colors import (
    ROTATION_COLORS, ROTATION_ORDER, GRID, INK_SECONDARY,
    SHIFT_ARRIVED_LATE, SHIFT_LEFT_EARLY, SEQUENTIAL_TEAL,
)

st.set_page_config(page_title="Adherence & Rotation", page_icon="🔄", layout="wide")
st.title("🔄 Adherence & Rotation Cadence")
st.caption("Daily, weekly, and half-day rotation each impose a different cost — this is where that shows up in the numbers.")

survey = load_survey()
log = load_adherence_log()

quarters = sorted(survey["quarter"].unique().tolist())
sel_quarter = st.selectbox("Quarter", quarters, index=len(quarters) - 1)
s_df = survey[survey["quarter"] == sel_quarter]
l_df = log[log["quarter"] == sel_quarter]

st.divider()

c1, c2, c3 = st.columns(3)
for col, rot in zip([c1, c2, c3], ROTATION_ORDER):
    sub = s_df[s_df["rotation_type"] == rot]
    col.metric(
        f"{rot} — Adherence", f"{sub['adherence_checklist_pct'].mean():.1f}%",
        help=f"Average end-of-shift checklist completion for {rot.lower()} rotation staff.",
    )

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Adherence Rate by Rotation Cadence")
    st.caption("Average checklist completion — pre-, during-, and post-shift combined.")
    rot_adherence = s_df.groupby("rotation_type")["adherence_checklist_pct"].mean().reindex(ROTATION_ORDER)
    fig1 = go.Figure(go.Bar(
        x=rot_adherence.index, y=rot_adherence.values,
        marker_color=[ROTATION_COLORS[r] for r in rot_adherence.index],
        text=[f"{v:.1f}%" for v in rot_adherence.values], textposition="outside",
        textfont=dict(color=INK_SECONDARY),
    ))
    fig1.update_layout(
        height=340, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="Adherence %", range=[0, 100]),
        showlegend=False,
    )
    st.plotly_chart(fig1, width="stretch")

with right:
    st.subheader("Late Arrivals & Early Departures")
    st.caption("Share of shifts with a late arrival or an early/unannounced departure, by rotation cadence.")
    rot_flags = l_df.groupby("rotation_type").agg(
        late=("arrived_late", "mean"), early=("left_early", "mean"),
    ).reindex(ROTATION_ORDER) * 100
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=rot_flags.index, y=rot_flags["late"], name="Arrived Late",
                           marker_color=SHIFT_ARRIVED_LATE))
    fig2.add_trace(go.Bar(x=rot_flags.index, y=rot_flags["early"], name="Left Early",
                           marker_color=SHIFT_LEFT_EARLY))
    fig2.update_layout(
        barmode="group", height=340, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="% of Shifts"),
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig2, width="stretch")

st.divider()

st.subheader("The Chronic Pattern")
st.caption(
    "The pattern itself: arriving **~20 minutes late** and leaving **~35 minutes early** — "
    "the same day, the same shift, week after week — while still being paid for the full "
    "shift. It's a fixed personal pattern, not random tardiness."
)
st.caption(
    "The cost isn't just the unworked time. Compliant coworkers absorb the coverage gap and "
    "carry the emotional, physical, and communicative strain of it recurring — performing "
    "'unbothered' at work while it keeps happening."
)

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
chronic_log = l_df[l_df["chronic_pattern"]]
n_chronic_staff = chronic_log["staff_id"].nunique()
n_total_staff = l_df["staff_id"].nunique()
pct_chronic = (n_chronic_staff / n_total_staff * 100) if n_total_staff else 0

c1, c2, c3 = st.columns(3)
c1.metric(
    "Avg Minutes Late — Chronic Hits",
    f"{chronic_log['minutes_late'].mean():.0f} min" if not chronic_log.empty else "—",
    help="Average arrival delay on a chronic-pattern staff member's designated weekday.",
)
c2.metric(
    "Avg Minutes Early — Chronic Hits",
    f"{chronic_log['minutes_early'].mean():.0f} min" if not chronic_log.empty else "—",
    help="Average early departure on a chronic-pattern staff member's designated weekday.",
)
c3.metric(
    "Staff Exhibiting the Pattern", f"{n_chronic_staff}",
    help=f"Headcount, not minutes — {pct_chronic:.0f}% of {n_total_staff} staff this quarter repeat the same late/early combo on the same weekday every time.",
)

cleft, cright = st.columns(2)
with cleft:
    st.caption("Chronic-pattern hits by weekday — which day it concentrates on.")
    wd_counts = chronic_log.groupby("weekday").size().reindex(WEEKDAY_ORDER).fillna(0)
    fig_wd = go.Figure(go.Bar(
        x=wd_counts.index, y=wd_counts.values, marker_color=SHIFT_LEFT_EARLY,
        text=[int(v) for v in wd_counts.values], textposition="outside",
        textfont=dict(color=INK_SECONDARY),
    ))
    fig_wd.update_layout(
        height=300, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="Chronic-Pattern Shifts"),
        showlegend=False,
    )
    st.plotly_chart(fig_wd, width="stretch")

with cright:
    st.caption("Minutes late/early: chronic-pattern shifts vs. every other shift.")
    by_chronic = l_df.groupby("chronic_pattern")[["minutes_late", "minutes_early"]].mean()
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        x=["Late", "Early"],
        y=[by_chronic.loc[False, "minutes_late"], by_chronic.loc[False, "minutes_early"]],
        name="Typical Shift", marker_color=SEQUENTIAL_TEAL[2],
    ))
    if True in by_chronic.index:
        fig_cmp.add_trace(go.Bar(
            x=["Late", "Early"],
            y=[by_chronic.loc[True, "minutes_late"], by_chronic.loc[True, "minutes_early"]],
            name="Chronic-Pattern Shift", marker_color=SHIFT_LEFT_EARLY,
        ))
    fig_cmp.update_layout(
        barmode="group", height=300, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="Minutes"),
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig_cmp, width="stretch")

st.divider()

st.subheader("Shift-Phase Breakdown")
st.caption("Pre-shift prep, during-shift execution, and post-shift closing (including documentation) don't get the same level of adherence.")
phase = l_df.groupby("rotation_type")[["pre_shift_pct", "during_shift_pct", "post_shift_pct"]].mean().reindex(ROTATION_ORDER)
fig3 = go.Figure()
for phase_col, phase_label in [("pre_shift_pct", "Pre-Shift"), ("during_shift_pct", "During-Shift"), ("post_shift_pct", "Post-Shift")]:
    fig3.add_trace(go.Bar(x=phase.index, y=phase[phase_col], name=phase_label))
fig3.update_traces(marker_line_width=0)
fig3.data[0].marker.color = SEQUENTIAL_TEAL[1]
fig3.data[1].marker.color = SEQUENTIAL_TEAL[3]
fig3.data[2].marker.color = SEQUENTIAL_TEAL[4]
fig3.update_layout(
    barmode="group", height=340, margin=dict(t=10, b=10, l=10, r=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor=GRID, title="Completion %", range=[0, 100]),
    legend=dict(orientation="h", y=1.15),
)
st.caption("Post-shift is consistently the weakest phase — the same pattern as skipped end-of-shift sanitizing and documentation described in the case study.")
st.plotly_chart(fig3, width="stretch")

with st.expander("📖 Every metric cut by rotation cadence — why it matters"):
    st.markdown("""
| Rotation | Relearning Burden | Worker Fatigue | Continuity Impact |
|---|---|---|---|
| **Daily** | Highest — constant re-establishing of trust & routine | Lowest per-shift accumulation | Most disruptive for the person receiving care |
| **Weekly** | Moderate | Compounds across the full week before reset | Moderate — predictable but long exposure |
| **Half-Day** | Low per handoff | Best — mid-shift recovery point | Highest handoff frequency — hardest on routine-dependent individuals |

There is no single schedule that optimizes all three — see the companion DMAIC case study's Measure phase.
""")
