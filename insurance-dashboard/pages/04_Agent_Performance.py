"""Agent Performance — leaderboard, premiums vs claims, portfolio mix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact, load_policies

st.set_page_config(page_title="Agent Performance", page_icon="🏅", layout="wide")
st.title("🏅 Agent Performance")
st.divider()

df  = load_claims_fact()
pol = load_policies()

# ── Agent summary ─────────────────────────────────────────────
agent_policies = (
    pol.groupby(["agent_name","agent_state"])
    .agg(policies=("policy_id","count"),
         premium_revenue=("annual_premium","sum"),
         total_coverage=("face_value","sum"))
    .reset_index()
)
# Claim rate = % of policies that have had AT LEAST ONE claim filed
# (unique policies with claims / total policies written by agent)
policies_with_claims = (
    df[["agent_name","policy_number"]]
    .drop_duplicates()
    .groupby("agent_name")
    .size()
    .reset_index(name="policies_with_claims")
)
agent_claims = (
    df.groupby("agent_name")
    .agg(total_claims=("claim_id","count"),
         claim_exposure=("claim_amount","sum"),
         paid_claims=("claim_status", lambda x: (x=="paid").sum()))
    .reset_index()
)
agents = (
    agent_policies
    .merge(agent_claims,        on="agent_name", how="left")
    .merge(policies_with_claims, on="agent_name", how="left")
    .fillna(0)
)
# Claim rate: % of policies that generated at least one claim (0–100%)
agents["claim_rate_pct"] = (
    agents["policies_with_claims"] / agents["policies"] * 100
).round(1).clip(0, 100)
agents["premium_to_claim"] = (
    agents["premium_revenue"] / agents["claim_exposure"].replace(0, float("nan"))
).round(2)
agents = agents.sort_values("premium_revenue", ascending=False)

# ── KPIs ──────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Total Agents",    len(agents))
c2.metric("Total Premiums",  f"${agents['premium_revenue'].sum()/1e6:.2f}M")
c3.metric("Total Coverage",  f"${agents['total_coverage'].sum()/1e6:.1f}M")
st.divider()

left, right = st.columns(2)

# ── Agent leaderboard — premium revenue ──────────────────────
with left:
    st.subheader("Premium Revenue by Agent")
    fig1 = go.Figure(go.Bar(
        x=agents["premium_revenue"] / 1000,
        y=agents["agent_name"],
        orientation="h",
        marker_color="#1E2761",
        text=[f"${v/1000:,.0f}K" for v in agents["premium_revenue"]],
        textposition="outside",
    ))
    fig1.update_layout(height=320,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(showgrid=False, title="Annual Premium ($K)"),
                       yaxis=dict(showgrid=False))
    st.plotly_chart(fig1, use_container_width=True)

# ── Policies written vs claims filed scatter ──────────────────
with right:
    st.subheader("Policies Written vs Claims Filed")
    st.caption(
        "**Claim Rate** = % of an agent's policies that have had at least one claim filed. "
        "🟢 Green = low claim rate (fewer policies triggered claims) · "
        "🔴 Red = high claim rate (more policies resulted in claims)."
    )
    fig2 = px.scatter(
        agents, x="policies", y="total_claims",
        size="premium_revenue", color="claim_rate_pct",
        hover_name="agent_name",
        hover_data={"claim_rate_pct": ":.1f",
                    "premium_revenue": ":$,.0f",
                    "policies": True},
        color_continuous_scale=[
            [0.0,  "#047857"],   # 0%  — green (good)
            [0.5,  "#FACC15"],   # 50% — yellow (watch)
            [1.0,  "#DC2626"],   # 100% — red (high risk)
        ],
        range_color=[0, 100],
        labels={
            "policies":      "Policies Written",
            "total_claims":  "Claims Filed",
            "claim_rate_pct":"Claim Rate %",
            "premium_revenue":"Annual Premium",
        },
        size_max=40,
    )
    fig2.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0"),
        coloraxis_colorbar=dict(
            title="Claim Rate %",
            ticksuffix="%",
            tickvals=[0, 25, 50, 75, 100],
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Full agent leaderboard table ──────────────────────────────
st.subheader("Agent Leaderboard")
display = agents[[
    "agent_name","agent_state","policies","premium_revenue",
    "total_coverage","total_claims","claim_rate_pct","premium_to_claim"
]].rename(columns={
    "agent_name":"Agent","agent_state":"State",
    "policies":"Policies","premium_revenue":"Annual Premium",
    "total_coverage":"Total Coverage","total_claims":"Claims",
    "claim_rate_pct":"Claim Rate %","premium_to_claim":"Premium/Claim"
})
st.dataframe(
    display.style.format({
        "Annual Premium":"${:,.0f}",
        "Total Coverage":"${:,.0f}",
        "Claim Rate %":"{:.1f}%",
        "Premium/Claim":"{:.2f}",
    }),
    use_container_width=True, hide_index=True,
)
