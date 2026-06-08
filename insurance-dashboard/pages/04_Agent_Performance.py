"""Agent Performance — leaderboard, premiums vs claims, portfolio mix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.load_data import load_claims_fact, load_policies
from data.colors import NAVY, BLUE, GREEN, AMBER, RED, GRID, PRODUCT_COLORS, RISK_SCALE, AGENT_COLORS

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
agent_claims = (
    df.groupby("agent_name")
    .agg(total_claims=("claim_id","count"),
         claim_exposure=("claim_amount","sum"),
         paid_claims=("claim_status", lambda x: (x=="paid").sum()))
    .reset_index()
)
agents = (
    agent_policies
    .merge(agent_claims, on="agent_name", how="left")
    .fillna(0)
)
# Claims per Policy: total claims filed / total policies written.
# Reflects average claim volume per policy — can exceed 1.0 when multiple
# beneficiaries file on the same policy.
# Low = fewer claims per policy (healthier book); High = more exposure.
agents["claims_per_policy"] = (
    agents["total_claims"] / agents["policies"].replace(0, float("nan"))
).round(2)
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
        marker_color=NAVY,
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
        "**Claims per Policy** = total claims filed ÷ total policies written. "
        "A value of 0.5 means 1 claim per 2 policies. Values above 1.0 mean multiple "
        "claims per policy (e.g. several beneficiaries filing on the same policy). "
        "🟢 Green = low (fewer claims per policy) · 🔴 Red = high (more claims per policy)."
    )
    max_ratio = agents["claims_per_policy"].max()
    fig2 = px.scatter(
        agents, x="policies", y="total_claims",
        size="premium_revenue", color="claims_per_policy",
        hover_name="agent_name",
        hover_data={
            "claims_per_policy": ":.2f",
            "premium_revenue":   ":$,.0f",
            "policies":          True,
            "total_claims":      True,
        },
        color_continuous_scale=RISK_SCALE,
        range_color=[0, max(max_ratio, 1.0)],
        labels={
            "policies":         "Policies Written",
            "total_claims":     "Claims Filed",
            "claims_per_policy":"Claims per Policy",
            "premium_revenue":  "Annual Premium",
        },
        size_max=40,
    )
    fig2.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0"),
        coloraxis_colorbar=dict(
            title="Claims / Policy",
            tickformat=".1f",
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Portfolio Mix — what product types each agent is selling ──
st.subheader("Agent Portfolio Mix — Policy Type Breakdown")
st.caption(
    "Permanent policies (Whole Life, Universal Life, Variable Life) generate long-term "
    "premium revenue and build cash value. A healthy agent portfolio balances term and "
    "permanent products. Agents with more permanent policies deliver higher lifetime value."
)

mix = (
    pol.groupby(["agent_name","policy_type"])
    .size()
    .reset_index(name="count")
)

fig3 = px.bar(
    mix,
    x="agent_name", y="count",
    color="policy_type",
    color_discrete_map=PRODUCT_COLORS,
    labels={"agent_name": "Agent", "count": "Policies Written", "policy_type": "Product"},
    barmode="stack",
)
fig3.update_layout(
    height=340,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, title=""),
    yaxis=dict(gridcolor="#E2E8F0", title="Policies Written"),
    legend=dict(orientation="h", y=1.12, title=""),
)
st.plotly_chart(fig3, use_container_width=True)

# ── Revenue efficiency callouts ────────────────────────────────
st.subheader("Revenue Efficiency")
st.caption("Annual premium per policy written — higher means the agent is selling higher-value coverage.")

eff = agents.copy()
eff["premium_per_policy"] = (eff["premium_revenue"] / eff["policies"]).round(0)
eff = eff.sort_values("premium_per_policy", ascending=False)

cols = st.columns(len(eff))
for col, row in zip(cols, eff.itertuples()):
    col.metric(
        label=row.agent_name.split()[-1],   # last name only to fit
        value=f"${row.premium_per_policy:,.0f}",
        delta=f"{row.policies} policies",
    )
