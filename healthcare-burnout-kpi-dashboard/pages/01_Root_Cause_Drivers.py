"""pages/01_Root_Cause_Drivers.py — The four unmotivating characteristics, by unit and role."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_survey
from data.colors import DRIVER_COLORS, DRIVER_ORDER, GRID, INK_SECONDARY, SERIES_NEUTRAL

st.set_page_config(page_title="Root-Cause Drivers", page_icon="🧭", layout="wide")
st.title("🧭 Root-Cause Drivers")
st.caption("Workload, Accountability, Reward, and Safety — the four fishbone branches from the DMAIC analysis, measured.")

survey = load_survey()

quarters = sorted(survey["quarter"].unique().tolist())
sel_quarter = st.selectbox("Quarter", quarters, index=len(quarters) - 1)
df = survey[survey["quarter"] == sel_quarter]

st.divider()

# ── Driver breakdown by unit (grouped bar, legend, fixed color order) ──
st.subheader("Driver Index by Unit")
st.caption("Each bar group is one unit; each color is a fixed driver — the same color always means the same thing.")

unit_driver = df.groupby("unit").agg(
    **{
        "Workload & Staffing": ("workload_index", "mean"),
        "Accountability": ("accountability_gap_score", "mean"),
        "Reward": ("reward_gap_score", "mean"),
        "Safety": ("safety_risk_score", "mean"),
    }
).reset_index()

fig = go.Figure()
for driver in DRIVER_ORDER:
    fig.add_trace(go.Bar(
        x=unit_driver["unit"], y=unit_driver[driver],
        name=driver, marker_color=DRIVER_COLORS[driver],
    ))
fig.update_layout(
    barmode="group", height=420, margin=dict(t=10, b=10, l=10, r=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor=GRID, title="Index (0–100, higher = worse)", range=[0, 100]),
    legend=dict(orientation="h", y=1.12),
)
st.plotly_chart(fig, width="stretch")

st.divider()

# ── Driver breakdown by role ─────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Driver Index by Role")
    st.caption("Medical students, hospital staff, and administrative roles each carry a different mix.")
    role_driver = df.groupby("role").agg(
        **{d: (c, "mean") for d, c in zip(
            DRIVER_ORDER,
            ["workload_index", "accountability_gap_score", "reward_gap_score", "safety_risk_score"],
        )}
    ).reset_index()
    fig_role = go.Figure()
    for driver in DRIVER_ORDER:
        fig_role.add_trace(go.Bar(
            x=role_driver["role"], y=role_driver[driver],
            name=driver, marker_color=DRIVER_COLORS[driver],
        ))
    fig_role.update_layout(
        barmode="group", height=360, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor=GRID, title="Index", range=[0, 100]),
        showlegend=False,
    )
    st.plotly_chart(fig_role, width="stretch")

with right:
    st.subheader("Accountability Gap vs. Burnout")
    st.caption("Each point is one unit — the wider the adherence variance within a team, the higher its burnout score tends to run.")
    SHORT_UNIT = {
        "Emergency Department": "Emergency Dept.",
        "Pediatric ICU": "Pediatric ICU",
        "Medical-Surgical": "Med-Surg",
        "Oncology": "Oncology",
        "Inpatient Rehab": "Inpatient Rehab",
    }
    scatter_df = df.groupby("unit").agg(
        accountability_gap=("accountability_gap_score", "mean"),
        burnout=("burnout_score", "mean"),
        headcount=("staff_id", "nunique"),
    ).reset_index()
    scatter_df["label"] = scatter_df["unit"].map(SHORT_UNIT)
    fig_scatter = go.Figure(go.Scatter(
        x=scatter_df["accountability_gap"], y=scatter_df["burnout"],
        mode="markers+text", text=scatter_df["label"], textposition="top center",
        marker=dict(size=scatter_df["headcount"] / 2, color=SERIES_NEUTRAL,
                    line=dict(width=1, color="white")),
        textfont=dict(size=10, color=INK_SECONDARY),
    ))
    y_max = float(scatter_df["burnout"].max())
    y_min = float(scatter_df["burnout"].min())
    y_pad = max((y_max - y_min) * 0.35, 5)
    x_max = float(scatter_df["accountability_gap"].max())
    x_min = float(scatter_df["accountability_gap"].min())
    x_pad = max((x_max - x_min) * 0.3, 8)
    fig_scatter.update_layout(
        height=360, margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=GRID, title="Accountability Gap (adherence variance)",
                   range=[x_min - x_pad, x_max + x_pad]),
        yaxis=dict(gridcolor=GRID, title="Avg Burnout Score", range=[y_min - y_pad, y_max + y_pad]),
        showlegend=False,
    )
    st.plotly_chart(fig_scatter, width="stretch")

with st.expander("📖 What do these drivers mean?"):
    st.markdown("""
| Driver | Plain-English Definition |
|---|---|
| **Workload & Staffing** | Understaffing and rigid rotation models forcing constant task-switching. |
| **Accountability** | Measured as the *variance* in adherence-checklist completion within a unit — the objective form of "some people do it right, some don't." |
| **Reward** | Low-cost motivators (food, massages, extra breaks) aren't consistently in place, and initiatives that do happen are often last-minute rather than planned. Staff-organized traditions like potlucks work well on their own. |
| **Safety** | Perceived and reported exposure to aggressive or unpredictable patient behavior. |

All four are scored 0–100, where **higher always means worse** — so they can be compared directly against each other.
""")
