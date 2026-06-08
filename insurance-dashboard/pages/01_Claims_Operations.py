"""Claims Operations — aging, examiner workload, cause analysis."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.sidebar_note import show as _sidebar_note
from data.load_data import load_claims_fact
from data.colors import AGING_COLORS, BLUE, SKY, NAVY, GRID, TEXT_MID, STATUS_COLORS, AMBER, RED, GREEN

st.set_page_config(page_title="Claims Operations", page_icon="📋", layout="wide")
st.title("📋 Claims Operations")
st.divider()
_sidebar_note()

df    = load_claims_fact()
open_ = df[df["claim_status"].isin(["pending","under_review"])].copy()

# ── KPIs with context ────────────────────────────────────────
total_open    = len(open_)
n_overdue     = (open_["aging_flag"] == "OVERDUE").sum()
n_aging       = (open_["aging_flag"] == "AGING").sum()
n_on_track    = (open_["aging_flag"] == "ON TRACK").sum()
pct_overdue   = n_overdue / max(total_open, 1) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Open Claims",    total_open,
          help="All claims not yet decided — pending + under review.")
c2.metric("Overdue (45+d)", n_overdue,
          delta=f"{pct_overdue:.0f}% of open claims",
          delta_color="off" if n_overdue == 0 else "inverse",
          help="Past the 45-day regulatory deadline. Immediate action required.")
c3.metric("At Risk (30–44d)", n_aging,
          help="Approaching the 45-day deadline. Assign or escalate now.")
c4.metric("On Track (<30d)", n_on_track,
          delta="✅ Within SLA" if n_on_track > 0 else "—",
          delta_color="off",
          help="Claims filed recently — still within regulatory timeframe.")
st.divider()

left, right = st.columns(2)

# ── Aging by Policy Type ──────────────────────────────────────
with left:
    st.subheader("Open Claims Aging by Policy Type")
    st.caption(
        "Each bar is an aging category. "
        "Colors show what **type of policy** the open claims are for — "
        "so you can see if overdue claims are concentrated in a specific product."
    )
    if not open_.empty:
        from data.colors import PRODUCT_COLORS
        aging_type = (
            open_.groupby(["aging_flag","policy_type"])
            .size().reset_index(name="count")
        )
        # Enforce aging order
        aging_order = ["ON TRACK","AGING","OVERDUE"]
        aging_type["aging_flag"] = pd.Categorical(
            aging_type["aging_flag"], categories=aging_order, ordered=True
        )
        aging_type = aging_type.sort_values("aging_flag")

        fig = px.bar(
            aging_type,
            x="aging_flag", y="count",
            color="policy_type",
            color_discrete_map=PRODUCT_COLORS,
            barmode="stack",
            labels={"aging_flag":"Aging Status","count":"Open Claims","policy_type":"Policy Type"},
            text="count",
        )
        fig.update_traces(textposition="inside", textfont_color="white")
        fig.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor=GRID),
            legend=dict(orientation="h", y=1.15, title=""),
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Examiner workload ─────────────────────────────────────────
with right:
    st.subheader("Examiner Workload by Policy Type")
    st.caption(
        "Shows each examiner's open claims broken down by the **type of policy** being claimed. "
        "Colors match the policy type legend used throughout the dashboard — "
        "so navy = Whole Life, sky = Universal Life, gray = Term Life, etc."
    )
    assigned = open_[open_["assigned_examiner"].notna()]
    if not assigned.empty:
        workload = (
            assigned.groupby(["assigned_examiner","policy_type"])
            .size().reset_index(name="count")
        )
        from data.colors import PRODUCT_COLORS
        fig2 = px.bar(
            workload,
            x="count", y="assigned_examiner",
            color="policy_type",
            color_discrete_map=PRODUCT_COLORS,
            orientation="h",
            barmode="stack",
            labels={"count":"Open Claims","assigned_examiner":"Examiner",
                    "policy_type":"Policy Type"},
            text="count",
        )
        fig2.update_traces(textposition="inside", textfont_color="white")
        fig2.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="Open Claims"),
            yaxis=dict(showgrid=False),
            legend=dict(orientation="h", y=1.15, title=""),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Cause of death distribution ───────────────────────────────
st.subheader("Claims by Cause of Death")
st.caption(
    "Each bar is colored by its **denial rate** — "
    "🟢 Green = low denial (most claims approved) · "
    "🟡 Amber = moderate denial · "
    "🔴 Red = high denial rate (common exclusion or investigation trigger). "
    "Bar height = total claims. Label shows count and denial %."
)
cause = (
    df.groupby("cause_of_death")
    .agg(total=("claim_id","count"),
         denied=("claim_status", lambda x: (x=="denied").sum()),
         avg_amount=("claim_amount","mean"))
    .reset_index()
    .sort_values("total", ascending=False)
)
cause["denial_rate"] = (cause["denied"] / cause["total"] * 100).round(1)
cause["bar_color"] = cause["denial_rate"].apply(
    lambda r: GREEN if r < 10 else (AMBER if r < 25 else RED)
)
cause["label"] = cause.apply(
    lambda r: f"{r['total']} claims<br>{r['denial_rate']:.0f}% denied", axis=1
)

fig3 = go.Figure(go.Bar(
    x=cause["cause_of_death"],
    y=cause["total"],
    marker_color=cause["bar_color"].tolist(),
    text=cause["label"],
    textposition="outside",
))
fig3.update_layout(
    height=360,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, title=""),
    yaxis=dict(gridcolor=GRID, title="Total Claims Filed"),
    showlegend=False,
    uniformtext_minsize=8,
    uniformtext_mode="hide",
)
st.plotly_chart(fig3, use_container_width=True)

# ── Open claims detail table ──────────────────────────────────
st.subheader("Open Claims Detail")
show = open_[["claim_number","claim_status","policyholder_name","policy_type",
              "cause_of_death","claim_amount","date_filed","days_open",
              "aging_flag","assigned_examiner"]].sort_values("days_open", ascending=False)
st.dataframe(
    show.rename(columns={
        "claim_number":"Claim #","claim_status":"Status",
        "policyholder_name":"Policyholder","policy_type":"Product",
        "cause_of_death":"Cause","claim_amount":"Amount",
        "date_filed":"Filed","days_open":"Days Open",
        "aging_flag":"Aging","assigned_examiner":"Examiner"
    }).style.format({"Amount":"${:,.0f}","Days Open":"{:.0f}"}),
    use_container_width=True, hide_index=True,
)

# ── Examiner Consistency ──────────────────────────────────────
st.divider()
st.subheader("🔍 Examiner Decision Consistency")
st.info(
    "**Why this matters:** If one examiner approves 90% of claims while another approves only 40%, "
    "that inconsistency is a compliance and fairness risk. Regulators and auditors look for this. "
    "Examiners should be making similar decisions on similar claims.\n\n"
    "The chart below shows each examiner's **approval rate** vs their **average decision time**. "
    "The ideal examiner is in the **bottom-right** — fast decisions, consistent approval rate near the team average."
)

decided = df[df["claim_status"].isin(["paid","approved","denied"])].copy()
if not decided.empty:
    exam_stats = (
        decided.groupby("assigned_examiner")
        .agg(
            total=("claim_id","count"),
            approved=("claim_status", lambda x: x.isin(["paid","approved"]).sum()),
            avg_days=("days_to_decision","mean"),
        )
        .reset_index()
    )
    exam_stats["approval_rate"] = (exam_stats["approved"] / exam_stats["total"] * 100).round(1)
    avg_approval = exam_stats["approval_rate"].mean()
    avg_days     = exam_stats["avg_days"].mean()

    fig_ex = go.Figure()
    for _, row in exam_stats.iterrows():
        fig_ex.add_trace(go.Scatter(
            x=[row["avg_days"]],
            y=[row["approval_rate"]],
            mode="markers+text",
            marker=dict(
                size=row["total"] * 4 + 12,
                color=NAVY,
                line=dict(color=SKY, width=2),
            ),
            text=[row["assigned_examiner"].split()[-1]],
            textposition="top center",
            name=row["assigned_examiner"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['assigned_examiner']}</b><br>"
                f"Approval Rate: {row['approval_rate']:.1f}%<br>"
                f"Avg Days: {row['avg_days']:.0f}<br>"
                f"Total Decided: {row['total']}"
            ),
        ))

    # Team average lines
    fig_ex.add_hline(y=avg_approval, line_dash="dash", line_color=AMBER, line_width=1.5,
                     annotation_text=f"Team avg approval {avg_approval:.0f}%",
                     annotation_font_color=AMBER)
    fig_ex.add_vline(x=avg_days, line_dash="dash", line_color=SKY, line_width=1.5,
                     annotation_text=f"Team avg {avg_days:.0f} days",
                     annotation_font_color=SKY)

    fig_ex.update_layout(
        height=340,
        xaxis=dict(title="Average Days to Decision", gridcolor=GRID),
        yaxis=dict(title="Approval Rate (%)", gridcolor=GRID, range=[0, 105]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_ex, use_container_width=True)
    st.caption(
        "Bubble size = number of claims decided. "
        "Dashed lines show team averages. "
        "Examiners far from the average approval rate line warrant review."
    )
