"""
extract.py — Extract all source tables from PostgreSQL into pandas DataFrames.

Connects to the life_insurance_claims database, pulls every table in SOURCE_TABLES,
saves raw Parquet snapshots, and returns a dict of DataFrames for the pipeline.
"""

import logging
import time
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine, text

import config

logger = logging.getLogger(__name__)


def get_engine():
    """Create and return a SQLAlchemy engine for the source database."""
    try:
        engine = create_engine(config.DB_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established: %s/%s",
                    config.DB_CONFIG["host"], config.DB_CONFIG["database"])
        return engine
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        raise


def extract_table(engine, table_name: str) -> pd.DataFrame:
    """Extract a single table into a DataFrame."""
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        logger.info("  %-25s  %5d rows  %d columns", table_name, len(df), len(df.columns))
        return df
    except Exception as e:
        logger.error("Failed to extract table '%s': %s", table_name, e)
        raise


def extract_custom_query(engine, name: str, query: str) -> pd.DataFrame:
    """Extract a named result set from a custom SQL query."""
    try:
        df = pd.read_sql(query, engine)
        logger.info("  %-25s  %5d rows (custom query)", name, len(df))
        return df
    except Exception as e:
        logger.error("Failed to extract query '%s': %s", name, e)
        raise


def save_raw_snapshot(frames: Dict[str, pd.DataFrame]) -> None:
    """Save raw DataFrames as Parquet snapshots before any transformation."""
    for name, df in frames.items():
        path = config.PARQUET_RAW / f"{name}.parquet"
        df.to_parquet(path, index=False, engine="pyarrow")
    logger.info("Raw snapshots saved → %s", config.PARQUET_RAW)


def run() -> Dict[str, pd.DataFrame]:
    """
    Main extract step.
    Returns a dict of {table_name: DataFrame} for all source tables
    plus a pre-built analytical query.
    """
    logger.info("=" * 60)
    logger.info("EXTRACT — pulling %d tables from PostgreSQL", len(config.SOURCE_TABLES))
    logger.info("=" * 60)

    start = time.time()
    engine = get_engine()
    frames: Dict[str, pd.DataFrame] = {}

    # ── Standard table extracts ───────────────────────────────
    for table in config.SOURCE_TABLES:
        frames[table] = extract_table(engine, table)

    # ── Pre-built analytical query (flattened claims fact) ────
    CLAIMS_FACT_QUERY = """
        SELECT
            c.claim_id,
            c.claim_number,
            c.status                                AS claim_status,
            c.date_of_death,
            c.date_filed,
            c.date_approved,
            c.date_denied,
            c.date_paid,
            c.cause_of_death,
            c.claim_amount,
            c.assigned_examiner,
            c.denial_reason,
            p.policy_number,
            p.face_value,
            p.annual_premium,
            p.age_at_issue,
            p.issue_date,
            p.expiration_date,
            p.status                                AS policy_status,
            p.riders,
            pt.type_name                            AS policy_type,
            pt.has_cash_value,
            ph.first_name || ' ' || ph.last_name    AS policyholder_name,
            ph.date_of_birth,
            ph.address_state,
            ph.smoker,
            ph.policyholder_since,
            b.first_name || ' ' || b.last_name      AS beneficiary_name,
            b.relationship,
            b.percentage                            AS beneficiary_pct,
            b.is_primary                            AS is_primary_beneficiary,
            a.first_name || ' ' || a.last_name      AS agent_name,
            a.state                                 AS agent_state
        FROM claims c
        JOIN policies      p  ON c.policy_id        = p.policy_id
        JOIN policy_types  pt ON p.policy_type_id   = pt.policy_type_id
        JOIN policyholders ph ON p.policyholder_id  = ph.policyholder_id
        LEFT JOIN beneficiaries b ON c.beneficiary_id = b.beneficiary_id
        LEFT JOIN agents        a ON p.agent_id       = a.agent_id
        ORDER BY c.date_filed DESC
    """
    frames["claims_fact"] = extract_custom_query(engine, "claims_fact", CLAIMS_FACT_QUERY)

    elapsed = round(time.time() - start, 2)
    total_rows = sum(len(df) for df in frames.values())
    logger.info("Extract complete — %d tables, %d total rows in %.2fs",
                len(frames), total_rows, elapsed)

    save_raw_snapshot(frames)
    return frames


if __name__ == "__main__":
    run()
