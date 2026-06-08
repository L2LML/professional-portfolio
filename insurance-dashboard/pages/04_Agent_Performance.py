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
top_agent    = agents.iloc[0]["agent_name"] if not agents.empty else "—"
avg_prem_pol = (agents["premium_revenue"] / agents["policies"].replace(0,1)).mean()
high_exposure = (agents["claims_per_policy"] >= 1.0).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Agents", len(agents),
          help="Number of active licensed agents in the portfolio.")
c2.metric("Total Annual Premiums", f"${agents['premium_revenue'].sum()/1e6:.2f}M",
          help="Sum of all annual premiums written across all agents.")
c3.metric("Avg Premium per Policy", f"${avg_prem_pol:,.0f}",
          help="Higher = agents are writing higher-value coverage on average.")
c4.metric("Agents with High Exposure", f"{high_exposure} of {len(agents)}",
          delta="≥ 1 claim per policy written",
          delta_color="off" if high_exposure == 0 else "inverse",
          help="Agents where total claims filed equals or exceeds policies written.")
st.divider()

left, right = st.columns(2)

# ── Agent leaderboard — premium revenue ──────────────────────
with left:
    st.subheader("Premium Revenue by Agent — by Product Type")
    st.caption(
        "Stacked bars show each agent's total premium revenue broken down by **policy type**. "
        "Colors match the product legend used throughout the dashboard."
    )
    agent_product = (
        pol.groupby(["agent_name","policy_type"])["annual_premium"]
        .sum().reset_index()
    )
    # Sort agents by total revenue descending
    order = agents.sort_values("premium_revenue", ascending=True)["agent_name"].tolist()
    fig1 = px.bar(
        agent_product,
        x="annual_premium", y="agent_name",
        color="policy_type",
        color_discrete_map=PRODUCT_COLORS,
        orientation="h",
        barmode="stack",
        category_orders={"agent_name": order},
        labels={"annual_premium":"Annual Premium ($)","agent_name":"Agent","policy_type":"Product"},
        text="annual_premium",
    )
    fig1.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="inside",
        textfont_color="white",
    )
    fig1.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="Annual Premium ($)"),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="h", y=1.15, title=""),
    )
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
    # Color each agent dot by their dominant claim policy type
    dominant = (
        df.groupby(["agent_name","policy_type"])
        .size().reset_index(name="cnt")
    )
    dominant = dominant.loc[dominant.groupby("agent_name")["cnt"].idxmax()][["agent_name","policy_type"]]
    dominant = dominant.rename(columns={"policy_type":"dominant_type"})
    agents_plot = agents.merge(dominant, on="agent_name", how="left")
    agents_plot["dominant_type"] = agents_plot["dominant_type"].fillna("Unknown")

    fig2 = go.Figure()
    for ptype, color in PRODUCT_COLORS.items():
        subset = agents_plot[agents_plot["dominant_type"] == ptype]
        if subset.empty:
            continue
        fig2.add_trace(go.Scatter(
            x=subset["policies"],
            y=subset["total_claims"],
            mode="markers+text",
            name=ptype,
            marker=dict(
                size=(subset["premium_revenue"] / agents_plot["premium_revenue"].max() * 40 + 12).tolist(),
                color=color,
                opacity=0.9,
                line=dict(color="white", width=1.5),
            ),
            text=subset["agent_name"].str.split().str[-1],
            textposition="top center",
            customdata=subset[["claims_per_policy","premium_revenue","dominant_type"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Policies Written: %{x}<br>"
                "Claims Filed: %{y}<br>"
                "Dominant Claim Type: %{customdata[2]}<br>"
                "Claims per Policy: %{customdata[0]:.2f}<br>"
                "Annual Premium: $%{customdata[1]:,.0f}<extra></extra>"
            ),
        ))

    fig2.update_layout(
        height=360,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=GRID, title="Policies Written"),
        yaxis=dict(gridcolor=GRID, title="Claims Filed"),
        legend=dict(orientation="h", y=1.15, title="Dominant Claim Type:"),
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
