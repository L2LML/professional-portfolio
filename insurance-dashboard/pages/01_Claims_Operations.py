"""Claims Operations — aging, examiner workload, cause analysis."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact
from data.colors import AGING_COLORS, BLUE, SKY, NAVY, GRID, TEXT_MID, STATUS_COLORS, AMBER, RED, GREEN

st.set_page_config(page_title="Claims Operations", page_icon="📋", layout="wide")
st.title("📋 Claims Operations")
st.divider()

df    = load_claims_fact()
open_ = df[df["claim_status"].isin(["pending","under_review"])].copy()

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Open Claims",    len(open_))
c2.metric("Overdue (60+d)", (open_["aging_flag"] == "OVERDUE").sum())
c3.metric("Aging (30–60d)", (open_["aging_flag"] == "AGING").sum())
c4.metric("On Track",       (open_["aging_flag"] == "ON TRACK").sum())
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
    "Navy bars = total claims filed for each cause. "
    "🔴 Red dots = denial rate for that cause. "
    "A high denial rate on a specific cause may indicate a policy exclusion or fraud investigation pattern."
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

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=cause["cause_of_death"],
    y=cause["total"],
    name="Total Claims",
    marker_color=NAVY,
    text=cause["total"],
    textposition="outside",
    yaxis="y1",
))
fig3.add_trace(go.Scatter(
    x=cause["cause_of_death"],
    y=cause["denial_rate"],
    name="Denial Rate %",
    mode="markers+lines",
    marker=dict(color=RED, size=10, symbol="circle"),
    line=dict(color=RED, width=2, dash="dot"),
    yaxis="y2",
))
fig3.update_layout(
    height=340,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(title="Total Claims", gridcolor=GRID, side="left"),
    yaxis2=dict(title="Denial Rate %", overlaying="y", side="right",
                range=[0, 100], showgrid=False, ticksuffix="%"),
    legend=dict(orientation="h", y=1.12),
    barmode="overlay",
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
