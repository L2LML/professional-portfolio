"""
transform.py — Enrich and standardize extracted DataFrames for cloud analytics.

Adds computed fields (age bands, tenure tiers, processing metrics),
standardizes formats, fills nulls, and builds a denormalized analytical
fact table ready for a cloud data warehouse.
"""

import logging
import time
from typing import Dict

import numpy as np
import pandas as pd

import config

logger = logging.getLogger(__name__)


# ── Individual table transformations ─────────────────────────

def transform_policyholders(df: pd.DataFrame) -> pd.DataFrame:
    """Add age, tenure, and segmentation fields to policyholders."""
    df = df.copy()
    today = pd.Timestamp.today()

    df["date_of_birth"]      = pd.to_datetime(df["date_of_birth"])
    df["policyholder_since"] = pd.to_datetime(df["policyholder_since"])

    # Current age
    df["current_age"] = (
        (today - df["date_of_birth"]).dt.days / 365.25
    ).astype("Int64")

    # Years with company
    df["tenure_years"] = (
        (today - df["policyholder_since"]).dt.days / 365.25
    ).round(1)

    # Tenure tier
    df["tenure_tier"] = pd.cut(
        df["tenure_years"],
        bins=config.TENURE_BINS,
        labels=config.TENURE_LABELS,
    ).astype(str)

    # Standardize state abbreviation
    df["address_state"] = df["address_state"].str.upper().str.strip()

    # Fill missing contact info
    df["email"] = df["email"].fillna("not_provided")
    df["phone"] = df["phone"].fillna("not_provided")

    logger.info("  policyholders: added current_age, tenure_years, tenure_tier")
    return df


def transform_policies(df: pd.DataFrame) -> pd.DataFrame:
    """Add age band, policy classification, and premium rate fields."""
    df = df.copy()
    today = pd.Timestamp.today()

    df["issue_date"]      = pd.to_datetime(df["issue_date"])
    df["expiration_date"] = pd.to_datetime(df["expiration_date"])

    # Age band at issuance
    df["age_band"] = pd.cut(
        df["age_at_issue"],
        bins=config.AGE_BINS,
        labels=config.AGE_LABELS,
    ).astype(str)

    # Permanent vs. term
    df["is_permanent"] = df["expiration_date"].isna()

    # Years in force
    df["years_in_force"] = (
        (today - df["issue_date"]).dt.days / 365.25
    ).round(1)

    # Normalized premium rate per $1,000 of coverage
    df["premium_per_1k_coverage"] = (
        df["annual_premium"] / df["face_value"] * 1_000
    ).round(2)

    # Days until expiry (term policies only)
    df["days_until_expiry"] = np.where(
        df["expiration_date"].notna(),
        (df["expiration_date"] - today).dt.days,
        np.nan,
    )

    # Has riders flag
    df["has_riders"] = df["riders"].notna()

    logger.info("  policies: added age_band, is_permanent, years_in_force, "
                "premium_per_1k_coverage, days_until_expiry")
    return df


def transform_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Add processing metrics, time dimensions, and risk flags to claims."""
    df = df.copy()
    today = pd.Timestamp.today()

    date_cols = ["date_of_death", "date_filed", "date_approved", "date_denied", "date_paid"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Days from death to filing (filing lag)
    df["days_death_to_filing"] = (df["date_filed"] - df["date_of_death"]).dt.days

    # Days to decision (approve or deny)
    df["days_to_decision"] = np.where(
        df["date_approved"].notna(),
        (df["date_approved"] - df["date_filed"]).dt.days,
        np.where(
            df["date_denied"].notna(),
            (df["date_denied"] - df["date_filed"]).dt.days,
            np.nan,
        ),
    )

    # Days open (in-progress claims only)
    open_mask = df["status"].isin(["pending", "under_review"])
    df["days_open"] = np.where(
        open_mask,
        (today - df["date_filed"]).dt.days,
        np.nan,
    )

    # Aging flag for open claims
    df["aging_flag"] = np.where(
        df["days_open"] > 60, "OVERDUE",
        np.where(df["days_open"] > 30, "AGING",
        np.where(open_mask, "ON TRACK", None))
    )

    # Time dimensions for analytics
    df["claim_year"]    = df["date_filed"].dt.year
    df["claim_month"]   = df["date_filed"].dt.month
    df["claim_quarter"] = df["date_filed"].dt.quarter

    # Risk and classification flags
    df["is_high_value"]    = df["claim_amount"] > config.HIGH_VALUE_THRESHOLD
    df["is_denied"]        = df["status"] == "denied"
    df["is_paid"]          = df["status"] == "paid"

    # Processing speed category
    effective_days = df["days_to_decision"].fillna(df["days_open"].fillna(999))
    df["processing_category"] = pd.cut(
        effective_days,
        bins=[-1, 14, 30, 60, float("inf")],
        labels=["Fast (≤14 days)", "Normal (15–30)", "Slow (31–60)", "Overdue (60+)"],
    ).astype(str)

    logger.info("  claims: added days_to_decision, days_open, aging_flag, "
                "claim_year/month/quarter, is_high_value, processing_category")
    return df


def transform_claims_fact(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich the pre-built analytical fact table with computed fields."""
    df = df.copy()
    today = pd.Timestamp.today()

    date_cols = ["date_of_death", "date_filed", "date_approved", "date_denied",
                 "date_paid", "date_of_birth", "issue_date", "policyholder_since"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Age band
    df["age_band"] = pd.cut(
        df["age_at_issue"],
        bins=config.AGE_BINS,
        labels=config.AGE_LABELS,
    ).astype(str)

    # Tenure
    df["tenure_years"] = (
        (today - df["policyholder_since"]).dt.days / 365.25
    ).round(1)
    df["tenure_tier"] = pd.cut(
        df["tenure_years"],
        bins=config.TENURE_BINS,
        labels=config.TENURE_LABELS,
    ).astype(str)

    # Processing time
    df["days_to_decision"] = np.where(
        df["date_approved"].notna(),
        (df["date_approved"] - df["date_filed"]).dt.days,
        np.where(
            df["date_denied"].notna(),
            (df["date_denied"] - df["date_filed"]).dt.days,
            np.nan,
        ),
    )

    # Time dimensions
    df["claim_year"]    = df["date_filed"].dt.year
    df["claim_month"]   = df["date_filed"].dt.month
    df["claim_quarter"] = df["date_filed"].dt.quarter

    df["is_high_value"] = df["claim_amount"] > config.HIGH_VALUE_THRESHOLD

    logger.info("  claims_fact: enriched with age_band, tenure_tier, "
                "time dimensions, processing metrics")
    return df


# ── Main transform entry point ────────────────────────────────

def run(frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Apply all transformations. Returns enriched DataFrames.
    """
    logger.info("=" * 60)
    logger.info("TRANSFORM — enriching %d DataFrames", len(frames))
    logger.info("=" * 60)

    start = time.time()
    transformed: Dict[str, pd.DataFrame] = {}

    transform_map = {
        "policyholders": transform_policyholders,
        "policies":      transform_policies,
        "claims":        transform_claims,
        "claims_fact":   transform_claims_fact,
    }

    for name, df in frames.items():
        if name in transform_map:
            transformed[name] = transform_map[name](df)
        else:
            transformed[name] = df.copy()

    # ── Save transformed Parquet files ────────────────────────
    for name, df in transformed.items():
        layer = "analytical" if name == "claims_fact" else "transformed"
        base  = config.PARQUET_ANALYTICAL if name == "claims_fact" else config.PARQUET_TRANSFORMED
        path  = base / f"{name}.parquet"
        df.to_parquet(path, index=False, engine="pyarrow")

    elapsed = round(time.time() - start, 2)
    logger.info("Transform complete — %d tables enriched in %.2fs", len(transformed), elapsed)

    # ── Summary of new columns added ─────────────────────────
    for name in transform_map:
        if name in frames and name in transformed:
            new_cols = set(transformed[name].columns) - set(frames[name].columns)
            if new_cols:
                logger.info("  %-20s  +%d columns: %s",
                            name, len(new_cols), ", ".join(sorted(new_cols)))

    return transformed


if __name__ == "__main__":
    from extract import run as extract_run
    data = extract_run()
    run(data)
