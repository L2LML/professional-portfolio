"""Claims Operations — aging, examiner workload, cause analysis."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact

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

# ── Aging distribution ────────────────────────────────────────
with left:
    st.subheader("Open Claims Aging")
    if not open_.empty:
        aging_counts = open_["aging_flag"].value_counts().reset_index()
        aging_counts.columns = ["Flag", "Count"]
        COLOR = {"OVERDUE": "#DC2626", "AGING": "#D97706", "ON TRACK": "#047857"}
        fig = px.bar(aging_counts, x="Flag", y="Count",
                     color="Flag", color_discrete_map=COLOR,
                     text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=300,
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"))
        st.plotly_chart(fig, use_container_width=True)

# ── Examiner workload ─────────────────────────────────────────
with right:
    st.subheader("Examiner Workload")
    workload = (
        open_[open_["assigned_examiner"].notna()]
        .groupby("assigned_examiner")
        .agg(count=("claim_id","count"), avg_days=("days_open","mean"))
        .reset_index()
        .sort_values("count", ascending=True)
    )
    if not workload.empty:
        fig2 = go.Figure(go.Bar(
            x=workload["count"], y=workload["assigned_examiner"],
            orientation="h", marker_color="#0284C7",
            text=[f"{c} claims · {d:.0f} avg days" for c, d in
                  zip(workload["count"], workload["avg_days"])],
            textposition="outside",
        ))
        fig2.update_layout(height=300,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)

# ── Cause of death distribution ───────────────────────────────
st.subheader("Claims by Cause of Death")
cause = (
    df.groupby("cause_of_death")
    .agg(total=("claim_id","count"), denied=("claim_status", lambda x: (x=="denied").sum()),
         avg_amount=("claim_amount","mean"))
    .reset_index()
    .sort_values("total", ascending=False)
)
cause["denial_rate"] = (cause["denied"] / cause["total"] * 100).round(1)

fig3 = px.bar(cause, x="cause_of_death", y="total",
              color="denial_rate",
              color_continuous_scale=["#047857","#D97706","#DC2626"],
              labels={"cause_of_death":"Cause","total":"Claims","denial_rate":"Denial %"},
              text="total")
fig3.update_traces(textposition="outside")
fig3.update_layout(height=320, coloraxis_colorbar=dict(title="Denial %"),
                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                   xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#E2E8F0"))
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
