"""
config.py — Centralized configuration for the insurance cloud migration pipeline.
Loads all settings from environment variables (.env file in development).
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Source Database ───────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     os.getenv("PG_PORT",     "5432"),
    "database": os.getenv("PG_DATABASE", "life_insurance_claims"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", ""),
}

DB_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ── AWS / S3 ─────────────────────────────────────────────────
AWS_CONFIG = {
    "region":     os.getenv("AWS_REGION", "us-east-1"),
    "bucket":     os.getenv("AWS_BUCKET", "insurance-claims-datalake"),
    "prefix":     os.getenv("AWS_PREFIX", "migrations/v1/"),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}

# ── Output Paths ─────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
OUTPUT_DIR      = BASE_DIR / "output"
PARQUET_RAW     = OUTPUT_DIR / "parquet" / "raw"
PARQUET_TRANSFORMED = OUTPUT_DIR / "parquet" / "transformed"
PARQUET_ANALYTICAL  = OUTPUT_DIR / "parquet" / "analytical"
CHARTS_DIR      = OUTPUT_DIR / "charts"
REPORTS_DIR     = OUTPUT_DIR / "reports"

for path in [PARQUET_RAW, PARQUET_TRANSFORMED, PARQUET_ANALYTICAL, CHARTS_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# ── Tables to Extract ─────────────────────────────────────────
SOURCE_TABLES = [
    "policy_types",
    "agents",
    "policyholders",
    "policies",
    "beneficiaries",
    "claims",
    "claim_documents",
    "claim_payments",
    "claims_audit",
]

# ── Age Band Bins ─────────────────────────────────────────────
AGE_BINS   = [17, 35, 50, 65, 120]
AGE_LABELS = ["18–35 Young Adult", "36–50 Middle Age", "51–65 Pre-Retirement", "65+ Senior"]

# ── Tenure Bins (years) ───────────────────────────────────────
TENURE_BINS   = [-1, 2, 5, 10, 100]
TENURE_LABELS = ["New (0–2 yrs)", "Establishing (3–5 yrs)", "Loyal (6–10 yrs)", "Long-Term (11+ yrs)"]

# ── High-Value Claim Threshold ────────────────────────────────
HIGH_VALUE_THRESHOLD = 250_000

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
