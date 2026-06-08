"""
pipeline.py — End-to-end orchestrator for the insurance cloud migration.

Runs Extract → Transform → Validate → Visualize → Load in sequence.
Logs timing for each stage, writes a final run summary to JSON,
and exits with a non-zero code if any critical step fails.

Usage:
    python pipeline.py               # full run
    python pipeline.py --skip-load   # run without uploading to S3
    python pipeline.py --skip-viz    # run without generating charts
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime

import config   # sets up logging

import extract
import transform
import validate
import visualize
import load

logger = logging.getLogger("pipeline")


def parse_args():
    parser = argparse.ArgumentParser(description="Insurance Claims Cloud Migration Pipeline")
    parser.add_argument("--skip-load", action="store_true",
                        help="Skip the S3 upload step (still saves locally)")
    parser.add_argument("--skip-viz",  action="store_true",
                        help="Skip chart generation")
    return parser.parse_args()


def run_stage(name: str, fn, *args, **kwargs):
    """Run a named pipeline stage with timing and error handling."""
    logger.info("")
    start = time.time()
    try:
        result  = fn(*args, **kwargs)
        elapsed = round(time.time() - start, 2)
        logger.info("✓ %s completed in %.2fs", name, elapsed)
        return result, elapsed, None
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error("✗ %s FAILED in %.2fs: %s", name, elapsed, e)
        return None, elapsed, str(e)


def main():
    args  = parse_args()
    start = time.time()

    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║   INSURANCE CLAIMS — CLOUD MIGRATION PIPELINE           ║")
    logger.info("║   PostgreSQL → Transform → Validate → S3 Data Lake      ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("Run started: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Environment: %s", config.DB_CONFIG.get("database", "unknown"))

    summary = {
        "run_timestamp": datetime.now().isoformat(),
        "stages":        {},
        "status":        "unknown",
    }

    # ── Stage 1: Extract ──────────────────────────────────────
    frames, t, err = run_stage("EXTRACT", extract.run)
    summary["stages"]["extract"] = {"elapsed_sec": t, "error": err}
    if err:
        summary["status"] = "FAILED"
        _save_summary(summary)
        sys.exit(1)

    # ── Stage 2: Transform ────────────────────────────────────
    frames, t, err = run_stage("TRANSFORM", transform.run, frames)
    summary["stages"]["transform"] = {"elapsed_sec": t, "error": err}
    if err:
        summary["status"] = "FAILED"
        _save_summary(summary)
        sys.exit(1)

    # ── Stage 3: Validate ─────────────────────────────────────
    report, t, err = run_stage("VALIDATE", validate.run, frames)
    summary["stages"]["validate"] = {
        "elapsed_sec":  t,
        "error":        err,
        "checks_passed":  report["summary"]["passed"]   if report else 0,
        "checks_failed":  report["summary"]["failures"] if report else 0,
        "checks_warned":  report["summary"]["warnings"] if report else 0,
    }
    if err or (report and report["summary"]["failures"] > 0):
        logger.error("Critical validation failures detected — pipeline halted.")
        summary["status"] = "FAILED"
        _save_summary(summary)
        sys.exit(1)

    # ── Stage 4: Visualize ────────────────────────────────────
    if not args.skip_viz:
        chart_paths, t, err = run_stage("VISUALIZE", visualize.run, frames)
        summary["stages"]["visualize"] = {
            "elapsed_sec": t,
            "charts_saved": len(chart_paths) if chart_paths else 0,
            "error": err,
        }
    else:
        logger.info("VISUALIZE skipped (--skip-viz)")
        summary["stages"]["visualize"] = {"skipped": True}

    # ── Stage 5: Load ─────────────────────────────────────────
    if not args.skip_load:
        load_result, t, err = run_stage("LOAD", load.run, frames, report)
        summary["stages"]["load"] = {
            "elapsed_sec":   t,
            "local_files":   len(load_result["local"]) if load_result else 0,
            "s3_uploads":    len(load_result["s3"])    if load_result else 0,
            "error":         err,
        }
    else:
        logger.info("LOAD skipped (--skip-load)")
        summary["stages"]["load"] = {"skipped": True}

    # ── Final summary ─────────────────────────────────────────
    total_elapsed = round(time.time() - start, 2)
    summary["total_elapsed_sec"] = total_elapsed
    summary["status"] = "SUCCESS"

    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║   PIPELINE COMPLETE — SUCCESS                            ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("Total elapsed : %.2f seconds", total_elapsed)
    logger.info("Output dir    : %s", config.OUTPUT_DIR)
    logger.info("Parquet files : %s", config.PARQUET_TRANSFORMED)
    logger.info("Charts        : %s", config.CHARTS_DIR)
    logger.info("Reports       : %s", config.REPORTS_DIR)

    _save_summary(summary)


def _save_summary(summary: dict) -> None:
    path = config.REPORTS_DIR / "pipeline_run.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info("Run summary   : %s", path)


if __name__ == "__main__":
    main()
