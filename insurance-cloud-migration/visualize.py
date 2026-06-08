"""
visualize.py — Pre-migration data audit charts.

Generates 5 business-focused charts from the transformed DataFrames
and saves them as high-resolution PNGs. These serve as a visual
data quality and profile report before loading to the cloud.
"""

import logging
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

import config

logger = logging.getLogger(__name__)

# ── Style ─────────────────────────────────────────────────────
NAVY      = "#1E2761"
ACCENT    = "#0284C7"
TEAL      = "#047857"
AMBER     = "#D97706"
ROSE      = "#DC2626"
PURPLE    = "#7C3AED"
LIGHT     = "#F4F7FF"
MED_GRAY  = "#64748B"
PALETTE   = [NAVY, ACCENT, TEAL, AMBER, ROSE, PURPLE]

plt.rcParams.update({
    "figure.facecolor":  LIGHT,
    "axes.facecolor":    "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.labelcolor":   MED_GRAY,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.titlecolor":   NAVY,
    "xtick.color":       MED_GRAY,
    "ytick.color":       MED_GRAY,
    "font.family":       "DejaVu Sans",
})


def _save(fig: plt.Figure, filename: str) -> Path:
    path = config.CHARTS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=LIGHT, edgecolor="none")
    plt.close(fig)
    logger.info("  Saved: %s", path.name)
    return path


# ── Chart 1: Claims Status Pipeline ──────────────────────────
def chart_claims_status(claims: pd.DataFrame) -> Path:
    """Horizontal bar showing count and value by claim status."""
    order = ["pending", "under_review", "approved", "paid", "denied", "withdrawn"]
    colors_map = {
        "pending":      AMBER,
        "under_review": ACCENT,
        "approved":     TEAL,
        "paid":         NAVY,
        "denied":       ROSE,
        "withdrawn":    MED_GRAY,
    }

    summary = (
        claims.groupby("status")
        .agg(count=("claim_id", "count"), total_value=("claim_amount", "sum"))
        .reindex([s for s in order if s in claims["status"].values])
        .reset_index()
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Claims Status Pipeline", fontsize=15, fontweight="bold",
                 color=NAVY, y=1.02)

    bar_colors = [colors_map.get(s, MED_GRAY) for s in summary["status"]]

    # Count
    bars = ax1.barh(summary["status"], summary["count"], color=bar_colors, height=0.6)
    ax1.set_xlabel("Number of Claims")
    ax1.set_title("Claim Count by Status")
    for bar, val in zip(bars, summary["count"]):
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 str(val), va="center", fontsize=10, color=NAVY, fontweight="bold")

    # Value
    bars2 = ax2.barh(summary["status"], summary["total_value"] / 1_000_000,
                      color=bar_colors, height=0.6)
    ax2.set_xlabel("Total Claim Value ($M)")
    ax2.set_title("Total Claim Value by Status")
    for bar, val in zip(bars2, summary["total_value"]):
        ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                 f"${val/1e6:.2f}M", va="center", fontsize=10, color=NAVY, fontweight="bold")

    fig.tight_layout()
    return _save(fig, "01_claims_status_pipeline.png")


# ── Chart 2: Monthly Claims Volume Trend ─────────────────────
def chart_monthly_trend(claims: pd.DataFrame) -> Path:
    """Line chart of monthly claims filed with volume and value."""
    claims = claims.copy()
    claims["date_filed"] = pd.to_datetime(claims["date_filed"])
    claims["year_month"] = claims["date_filed"].dt.to_period("M")

    monthly = (
        claims.groupby("year_month")
        .agg(count=("claim_id", "count"), total_value=("claim_amount", "sum"))
        .tail(24)   # last 24 months
        .reset_index()
    )
    monthly["label"] = monthly["year_month"].astype(str)

    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.fill_between(monthly["label"], monthly["count"],
                     color=ACCENT, alpha=0.25)
    ax1.plot(monthly["label"], monthly["count"],
             color=ACCENT, linewidth=2.5, marker="o", markersize=5, label="Claims Filed")
    ax2.plot(monthly["label"], monthly["total_value"] / 1_000,
             color=NAVY, linewidth=2, linestyle="--", marker="s", markersize=4,
             label="Total Value ($K)")

    step = max(1, len(monthly) // 8)
    ax1.set_xticks(range(0, len(monthly), step))
    ax1.set_xticklabels(monthly["label"].iloc[::step], rotation=35, ha="right", fontsize=9)
    ax1.set_ylabel("Claims Filed", color=ACCENT)
    ax2.set_ylabel("Total Value ($K)", color=NAVY)
    ax1.set_title("Monthly Claims Volume — Last 24 Months", fontsize=13)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.8)

    fig.tight_layout()
    return _save(fig, "02_monthly_claims_trend.png")


# ── Chart 3: Payout by Policy Type ───────────────────────────
def chart_payout_by_policy_type(claims_fact: pd.DataFrame) -> Path:
    """Grouped bar showing claim count and total payout by policy type."""
    if "policy_type" not in claims_fact.columns:
        logger.warning("claims_fact missing 'policy_type' — skipping chart 3")
        return None

    paid = claims_fact[claims_fact["claim_status"] == "paid"]
    summary = (
        paid.groupby("policy_type")
        .agg(count=("claim_id", "count"), total_payout=("claim_amount", "sum"))
        .sort_values("total_payout", ascending=True)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.barh(summary["policy_type"], summary["total_payout"] / 1_000,
                   color=PALETTE[:len(summary)], height=0.55)
    ax.set_xlabel("Total Paid Out ($K)")
    ax.set_title("Total Paid Claims by Policy Type")

    for bar, row in zip(bars, summary.itertuples()):
        ax.text(bar.get_width() + 5,
                bar.get_y() + bar.get_height() / 2,
                f"${row.total_payout/1e3:,.0f}K  ({row.count} claims)",
                va="center", fontsize=10, color=NAVY)

    fig.tight_layout()
    return _save(fig, "03_payout_by_policy_type.png")


# ── Chart 4: Customer Age Band Analysis ──────────────────────
def chart_age_band_analysis(policies: pd.DataFrame, claims: pd.DataFrame) -> Path:
    """Grouped bar — policy count vs. claim rate by age band at issuance."""
    if "age_band" not in policies.columns:
        logger.warning("policies missing 'age_band' — skipping chart 4")
        return None

    policy_counts = (
        policies[policies["age_band"].notna()]
        .groupby("age_band")
        .size()
        .rename("policy_count")
    )
    claim_counts = (
        policies[policies["age_band"].notna()]
        .merge(claims[["policy_id"]], on="policy_id", how="left")
        .groupby("age_band")["policy_id"]
        .count()
        .rename("claim_count")
    )
    df = pd.concat([policy_counts, claim_counts], axis=1).fillna(0)
    df["claim_rate"] = (df["claim_count"] / df["policy_count"] * 100).round(1)
    df = df.reset_index()

    x     = np.arange(len(df))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    ax1.bar(x - width / 2, df["policy_count"], width, color=NAVY, label="Policies Written", alpha=0.85)
    ax1.bar(x + width / 2, df["claim_count"],  width, color=ACCENT, label="Claims Filed",   alpha=0.85)
    ax2.plot(x, df["claim_rate"], color=ROSE, linewidth=2.5, marker="D",
             markersize=8, label="Claim Rate %", zorder=5)

    ax1.set_xticks(x)
    ax1.set_xticklabels(df["age_band"], fontsize=10)
    ax1.set_ylabel("Count")
    ax2.set_ylabel("Claim Rate (%)", color=ROSE)
    ax1.set_title("Policy Count & Claim Rate by Age Band at Issuance")

    for xi, rate in zip(x, df["claim_rate"]):
        ax2.annotate(f"{rate:.0f}%", (xi, rate),
                     textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=9, color=ROSE, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.8)

    fig.tight_layout()
    return _save(fig, "04_age_band_analysis.png")


# ── Chart 5: Tenure Cohort Claim Rates ───────────────────────
def chart_tenure_cohort(policyholders: pd.DataFrame,
                         policies: pd.DataFrame,
                         claims: pd.DataFrame) -> Path:
    """Horizontal grouped bar — premium revenue vs. claim exposure by tenure."""
    if "tenure_tier" not in policyholders.columns:
        logger.warning("policyholders missing 'tenure_tier' — skipping chart 5")
        return None

    merged = (
        policies
        .merge(policyholders[["policyholder_id", "tenure_tier"]], on="policyholder_id", how="left")
        .merge(claims[["policy_id", "claim_amount"]].groupby("policy_id")["claim_amount"]
               .sum().reset_index().rename(columns={"claim_amount": "total_claims"}),
               on="policy_id", how="left")
    )
    merged["total_claims"] = merged["total_claims"].fillna(0)

    order = config.TENURE_LABELS
    summary = (
        merged[merged["tenure_tier"].notna()]
        .groupby("tenure_tier")
        .agg(
            premium_revenue=("annual_premium",  "sum"),
            claim_exposure=("total_claims",     "sum"),
            customer_count=("policyholder_id",  "nunique"),
        )
        .reindex([t for t in order if t in merged["tenure_tier"].values])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    x     = np.arange(len(summary))
    width = 0.38

    b1 = ax.bar(x - width / 2, summary["premium_revenue"] / 1_000,
                width, color=TEAL,  label="Annual Premium Revenue ($K)", alpha=0.88)
    b2 = ax.bar(x + width / 2, summary["claim_exposure"]  / 1_000,
                width, color=ROSE,  label="Total Claims Exposure ($K)",  alpha=0.88)

    ax.set_xticks(x)
    ax.set_xticklabels(summary["tenure_tier"], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}K"))
    ax.set_title("Premium Revenue vs. Claims Exposure by Customer Tenure")
    ax.legend(framealpha=0.8)

    # Customer count labels above bars
    for xi, row in zip(x, summary.itertuples()):
        ax.text(xi, max(row.premium_revenue, row.claim_exposure) / 1_000 + 5,
                f"{row.customer_count} customers",
                ha="center", fontsize=9, color=MED_GRAY)

    fig.tight_layout()
    return _save(fig, "05_tenure_cohort_analysis.png")


# ── Main ──────────────────────────────────────────────────────

def run(frames: Dict[str, pd.DataFrame]) -> Dict[str, Path]:
    """Generate all 5 pre-migration audit charts. Returns paths."""
    logger.info("=" * 60)
    logger.info("VISUALIZE — generating pre-migration audit charts")
    logger.info("=" * 60)

    paths = {}
    claims        = frames.get("claims",        pd.DataFrame())
    claims_fact   = frames.get("claims_fact",   pd.DataFrame())
    policies      = frames.get("policies",      pd.DataFrame())
    policyholders = frames.get("policyholders", pd.DataFrame())

    chart_fns = [
        ("claims_status",    lambda: chart_claims_status(claims)),
        ("monthly_trend",    lambda: chart_monthly_trend(claims)),
        ("payout_by_type",   lambda: chart_payout_by_policy_type(claims_fact)),
        ("age_band",         lambda: chart_age_band_analysis(policies, claims)),
        ("tenure_cohort",    lambda: chart_tenure_cohort(policyholders, policies, claims)),
    ]

    for name, fn in chart_fns:
        try:
            path = fn()
            if path:
                paths[name] = path
        except Exception as e:
            logger.error("Chart '%s' failed: %s", name, e)

    logger.info("Visualizations complete — %d charts saved → %s",
                len(paths), config.CHARTS_DIR)
    return paths


if __name__ == "__main__":
    from extract   import run as extract_run
    from transform import run as transform_run
    data = extract_run()
    data = transform_run(data)
    run(data)
