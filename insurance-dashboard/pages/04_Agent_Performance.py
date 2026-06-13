"""Agent Performance — leaderboard, premiums vs claims, portfolio mix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.sidebar_note import show as _sidebar_note
from data.load_data import load_claims_fact, load_policies
from data.colors import NAVY, BLUE, GREEN, AMBER, RED, GRID, PRODUCT_COLORS, RISK_SCALE, AGENT_COLORS

st.set_page_config(page_title="Agent Performance", page_icon="🏅", layout="wide")
st.title("🏅 Agent Performance")
st.divider()
_sidebar_note()

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
top_agent       = agents.iloc[0] if not agents.empty else None
top_name        = top_agent["agent_name"] if top_agent is not None else "—"
top_revenue     = top_agent["premium_revenue"] if top_agent is not None else 0
avg_prem_pol    = (agents["premium_revenue"] / agents["policies"].replace(0, 1)).mean()
avg_claims_pol  = agents["claims_per_policy"].mean()
lowest_exposure = agents.loc[agents["claims_per_policy"].idxmin()] if not agents.empty else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Top Agent by Revenue",
          top_name.split()[-1] if top_name != "—" else "—",
          delta=f"${top_revenue:,.0f} annual premiums",
          delta_color="off",
          help="Agent with the highest total annual premium revenue.")
c2.metric("Total Annual Premiums",
          f"${agents['premium_revenue'].sum()/1e6:.2f}M",
          help="Sum of all annual premiums written across all agents.")
c3.metric("Avg Premium per Policy",
          f"${avg_prem_pol:,.0f}",
          help="Higher = agents are writing higher-value coverage on average.")
c4.metric("Avg Claims per Policy",
          f"{avg_claims_pol:.2f}",
          delta="across all agents",
          delta_color="off",
          help="Total claims filed ÷ total policies written. Lower = healthier book of business.")
st.divider()

# ── Auto-generated insight ────────────────────────────────────
if top_agent is not None and lowest_exposure is not None:
    low_name = lowest_exposure["agent_name"]
    low_cpp  = lowest_exposure["claims_per_policy"]
    st.info(
        f"**{top_name}** leads the portfolio with **${top_revenue:,.0f}** in annual premiums. "
        f"**{low_name}** has the lowest claims per policy at **{low_cpp:.2f}** — "
        "the healthiest claims ratio on the team."
    )
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
    st.plotly_chart(fig1, width="stretch")

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
    st.plotly_chart(fig2, width="stretch")

# ── Agent Leaderboard Table ───────────────────────────────────
st.divider()
st.subheader("📋 Agent Leaderboard")
st.caption(
    "All key metrics per agent in one view. "
    "**Avg Premium/Policy** = book quality — higher means the agent writes higher-value coverage. "
    "**Claims/Policy** = claims health — lower is better. "
    "🟢 Below 0.30 · 🟡 0.30–0.50 · 🔴 Above 0.50."
)

leaderboard = agents.copy()
leaderboard["premium_per_policy"] = (
    leaderboard["premium_revenue"] / leaderboard["policies"].replace(0, 1)
).round(0)

# Relative benchmarking — compare each agent to the team average
team_avg_cpp = leaderboard["claims_per_policy"].mean()
team_std_cpp = leaderboard["claims_per_policy"].std()
low_threshold  = team_avg_cpp - 0.5 * team_std_cpp   # below avg = green
high_threshold = team_avg_cpp + 0.5 * team_std_cpp   # above avg = red

leaderboard["zone"] = leaderboard["claims_per_policy"].apply(
    lambda r: "🟢 Low Risk" if r < low_threshold
    else ("🔴 High Risk" if r > high_threshold else "🟡 Average")
)
leaderboard = leaderboard.sort_values("premium_revenue", ascending=False)
leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))

def color_cpp(val):
    try:
        v = float(val)
        if v < low_threshold:  return f"color: {GREEN}; font-weight: bold"
        if v > high_threshold: return f"color: {RED}; font-weight: bold"
        return f"color: {AMBER}; font-weight: bold"
    except:
        return ""

st.caption(
    f"**Claims/Policy zones are relative to the team average of {team_avg_cpp:.2f}.** "
    f"Higher claims per policy = more exposure = higher risk. "
    f"🟢 Low Risk (< {low_threshold:.2f}) · "
    f"🟡 Average ({low_threshold:.2f}–{high_threshold:.2f}) · "
    f"🔴 High Risk (> {high_threshold:.2f})."
)
st.dataframe(
    leaderboard[[
        "Rank","agent_name","agent_state","policies",
        "premium_revenue","premium_per_policy",
        "total_claims","claims_per_policy","zone"
    ]].rename(columns={
        "agent_name":        "Agent",
        "agent_state":       "State",
        "policies":          "Policies",
        "premium_revenue":   "Annual Revenue",
        "premium_per_policy":"Avg Premium/Policy",
        "total_claims":      "Claims Filed",
        "claims_per_policy": "Claims/Policy",
        "zone":              "Zone",
    }).style.format({
        "Annual Revenue":     "${:,.0f}",
        "Avg Premium/Policy": "${:,.0f}",
        "Claims/Policy":      "{:.2f}",
    }).map(color_cpp, subset=["Claims/Policy"]),
    width="stretch", hide_index=True,
)
