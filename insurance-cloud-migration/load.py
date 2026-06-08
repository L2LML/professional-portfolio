"""
load.py — Load transformed data to the cloud data lake (AWS S3 as Parquet).

Uploads all Parquet files from the transformed and analytical layers to S3,
organized by table name and run timestamp for versioned, partitioned storage.
Patterns for BigQuery and Snowflake are included as comments.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import config

logger = logging.getLogger(__name__)

RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")


# ── Local save (always runs) ──────────────────────────────────

def save_parquet_local(df: pd.DataFrame, name: str, layer: str) -> Path:
    """Save a DataFrame as Parquet to the local output directory."""
    base = config.PARQUET_ANALYTICAL if layer == "analytical" else config.PARQUET_TRANSFORMED
    path = base / f"{name}.parquet"
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path, compression="snappy")
    size_kb = path.stat().st_size // 1024
    logger.info("  %-30s  %5d rows  %4d KB  → %s", name, len(df), size_kb, path.name)
    return path


# ── AWS S3 upload ─────────────────────────────────────────────

def upload_to_s3(local_path: Path, s3_key: str) -> bool:
    """
    Upload a single file to AWS S3.
    Returns True on success, False if credentials are not configured.
    """
    if not config.AWS_CONFIG.get("access_key") or not config.AWS_CONFIG.get("secret_key"):
        logger.warning("AWS credentials not set — skipping S3 upload for %s", local_path.name)
        return False

    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        s3 = boto3.client(
            "s3",
            region_name=config.AWS_CONFIG["region"],
            aws_access_key_id=config.AWS_CONFIG["access_key"],
            aws_secret_access_key=config.AWS_CONFIG["secret_key"],
        )

        bucket = config.AWS_CONFIG["bucket"]
        s3.upload_file(
            str(local_path),
            bucket,
            s3_key,
            ExtraArgs={"ContentType": "application/octet-stream"},
        )
        logger.info("  Uploaded → s3://%s/%s", bucket, s3_key)
        return True

    except ImportError:
        logger.warning("boto3 not installed — skipping S3 upload")
        return False
    except (NoCredentialsError, ClientError) as e:
        logger.error("S3 upload failed for %s: %s", local_path.name, e)
        return False


def build_s3_key(table_name: str, layer: str) -> str:
    """
    Build a partitioned S3 key for versioned, date-partitioned storage.

    Example output:
        migrations/v1/transformed/run_20240601_143022/policyholders.parquet
    """
    prefix = config.AWS_CONFIG["prefix"].rstrip("/")
    return f"{prefix}/{layer}/run_{RUN_TS}/{table_name}.parquet"


# ── Cloud load patterns (reference implementations) ──────────

def load_to_bigquery_pattern(df: pd.DataFrame, table_name: str) -> None:
    """
    Reference pattern: Load DataFrame to Google BigQuery.
    Requires: pip install google-cloud-bigquery pandas-gbq

    from google.cloud import bigquery
    import pandas_gbq

    project_id  = os.getenv("GCP_PROJECT_ID")
    dataset     = os.getenv("BQ_DATASET", "insurance_claims")
    destination = f"{project_id}.{dataset}.{table_name}"

    pandas_gbq.to_gbq(
        df,
        destination_table=destination,
        project_id=project_id,
        if_exists="replace",         # or "append"
        progress_bar=False,
    )
    """
    pass


def load_to_snowflake_pattern(df: pd.DataFrame, table_name: str) -> None:
    """
    Reference pattern: Load DataFrame to Snowflake.
    Requires: pip install snowflake-connector-python snowflake-sqlalchemy

    from snowflake.connector.pandas_tools import write_pandas
    import snowflake.connector

    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "INSURANCE_DW"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "CLAIMS"),
    )
    success, nchunks, nrows, output = write_pandas(
        conn, df, table_name.upper(), auto_create_table=True
    )
    """
    pass


# ── Main load entry point ─────────────────────────────────────

def run(frames: Dict[str, pd.DataFrame],
        validation_report: Dict = None) -> Dict[str, List]:
    """
    Save all DataFrames as Parquet locally and upload to S3.
    Returns a summary of all files saved and uploaded.
    """
    logger.info("=" * 60)
    logger.info("LOAD — saving %d tables as Parquet + uploading to S3", len(frames))
    logger.info("=" * 60)

    # Halt on critical validation failures
    if validation_report:
        failures = validation_report.get("summary", {}).get("failures", 0)
        if failures > 0:
            logger.error(
                "Load ABORTED — %d critical validation failures. Fix data issues first.",
                failures
            )
            raise RuntimeError(f"Validation failed with {failures} critical errors.")

    start       = time.time()
    saved_local = []
    uploaded_s3 = []

    analytical_tables = {"claims_fact"}

    for name, df in frames.items():
        layer = "analytical" if name in analytical_tables else "transformed"
        try:
            # ── Local save ────────────────────────────────────
            path = save_parquet_local(df, name, layer)
            saved_local.append(str(path))

            # ── S3 upload ─────────────────────────────────────
            s3_key = build_s3_key(name, layer)
            success = upload_to_s3(path, s3_key)
            if success:
                uploaded_s3.append(s3_key)

        except Exception as e:
            logger.error("Failed to load table '%s': %s", name, e)

    elapsed = round(time.time() - start, 2)
    logger.info("Load complete in %.2fs", elapsed)
    logger.info("  Local files saved : %d", len(saved_local))
    logger.info("  S3 uploads        : %d", len(uploaded_s3))

    if uploaded_s3:
        logger.info("  S3 bucket         : s3://%s/%s",
                    config.AWS_CONFIG["bucket"], config.AWS_CONFIG["prefix"])
    else:
        logger.info("  S3 skipped (no credentials) — all data saved locally")

    return {"local": saved_local, "s3": uploaded_s3}


if __name__ == "__main__":
    from extract   import run as extract_run
    from transform import run as transform_run
    from validate  import run as validate_run

    data   = extract_run()
    data   = transform_run(data)
    report = validate_run(data)
    run(data, report)
