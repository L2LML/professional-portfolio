"""
validate.py — Data quality validation before cloud load.

Runs a suite of checks across the transformed DataFrames and produces
a structured JSON report. The pipeline will warn on failures but
only halt on CRITICAL severity issues.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

import config

logger = logging.getLogger(__name__)


# ── Check result builder ──────────────────────────────────────

def check(name: str, passed: bool, severity: str,
          detail: str = "", failed_count: int = 0) -> Dict[str, Any]:
    status = "PASS" if passed else ("WARN" if severity == "warning" else "FAIL")
    return {
        "check":        name,
        "status":       status,
        "severity":     severity,
        "detail":       detail,
        "failed_count": failed_count,
    }


# ── Individual checks ─────────────────────────────────────────

def check_no_nulls(df: pd.DataFrame, table: str, columns: List[str]) -> List[Dict]:
    results = []
    for col in columns:
        if col not in df.columns:
            continue
        nulls = df[col].isna().sum()
        results.append(check(
            name=f"{table}.{col} — no nulls",
            passed=(nulls == 0),
            severity="critical",
            detail=f"{nulls} null values found" if nulls else "All values present",
            failed_count=int(nulls),
        ))
    return results


def check_unique(df: pd.DataFrame, table: str, column: str) -> Dict:
    dupes = df[column].duplicated().sum()
    return check(
        name=f"{table}.{column} — unique values",
        passed=(dupes == 0),
        severity="critical",
        detail=f"{dupes} duplicate values found" if dupes else "All values unique",
        failed_count=int(dupes),
    )


def check_valid_values(df: pd.DataFrame, table: str,
                       column: str, valid_set: set) -> Dict:
    if column not in df.columns:
        return check(f"{table}.{column} — valid values", True, "warning", "Column not found")
    invalid = ~df[column].isin(valid_set)
    count   = invalid.sum()
    return check(
        name=f"{table}.{column} — valid values",
        passed=(count == 0),
        severity="critical",
        detail=f"Invalid: {df.loc[invalid, column].unique().tolist()}" if count else "All values valid",
        failed_count=int(count),
    )


def check_positive(df: pd.DataFrame, table: str, column: str) -> Dict:
    if column not in df.columns:
        return check(f"{table}.{column} — positive values", True, "warning", "Column not found")
    non_positive = (df[column] <= 0).sum()
    return check(
        name=f"{table}.{column} — positive values",
        passed=(non_positive == 0),
        severity="critical",
        detail=f"{non_positive} non-positive values" if non_positive else "All values positive",
        failed_count=int(non_positive),
    )


def check_date_order(df: pd.DataFrame, table: str,
                     col_before: str, col_after: str) -> Dict:
    mask = df[col_before].notna() & df[col_after].notna()
    violations = (df.loc[mask, col_before] > df.loc[mask, col_after]).sum()
    return check(
        name=f"{table}: {col_before} ≤ {col_after}",
        passed=(violations == 0),
        severity="critical",
        detail=f"{violations} rows where {col_before} > {col_after}" if violations else "Date order valid",
        failed_count=int(violations),
    )


def check_referential_integrity(child: pd.DataFrame, child_col: str,
                                 parent: pd.DataFrame, parent_col: str,
                                 label: str) -> Dict:
    orphans = ~child[child_col].isin(parent[parent_col])
    count   = orphans.sum()
    return check(
        name=f"Referential integrity — {label}",
        passed=(count == 0),
        severity="critical",
        detail=f"{count} orphaned records found" if count else "All foreign keys resolve",
        failed_count=int(count),
    )


def check_beneficiary_percentages(beneficiaries: pd.DataFrame) -> Dict:
    """Each policy's primary beneficiaries should sum to 100%."""
    primary = beneficiaries[beneficiaries["is_primary"] == True]
    totals  = primary.groupby("policy_id")["percentage"].sum()
    bad     = totals[(totals < 99.9) | (totals > 100.1)]
    return check(
        name="Beneficiary primary allocations sum to 100%",
        passed=(len(bad) == 0),
        severity="warning",
        detail=f"Policy IDs with bad totals: {bad.index.tolist()}" if len(bad) else "All policies sum to 100%",
        failed_count=int(len(bad)),
    )


def check_age_range(df: pd.DataFrame) -> Dict:
    """Age at issue should be between 18 and 100."""
    if "age_at_issue" not in df.columns:
        return check("policies.age_at_issue — range 18–100", True, "warning", "Column not found")
    out_of_range = ((df["age_at_issue"] < 18) | (df["age_at_issue"] > 100)).sum()
    return check(
        name="policies.age_at_issue — range 18–100",
        passed=(out_of_range == 0),
        severity="warning",
        detail=f"{out_of_range} policies outside range" if out_of_range else "All ages in valid range",
        failed_count=int(out_of_range),
    )


def check_row_counts(frames: Dict[str, pd.DataFrame]) -> List[Dict]:
    """Warn if any table has zero rows."""
    results = []
    for name, df in frames.items():
        results.append(check(
            name=f"{name} — row count > 0",
            passed=(len(df) > 0),
            severity="critical",
            detail=f"{len(df)} rows",
            failed_count=0 if len(df) > 0 else 1,
        ))
    return results


# ── Main validation runner ────────────────────────────────────

def run(frames: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Run all data quality checks. Returns a structured report dict
    and saves it as JSON to output/reports/validation_report.json.
    """
    logger.info("=" * 60)
    logger.info("VALIDATE — running data quality checks")
    logger.info("=" * 60)

    start   = time.time()
    results = []

    claims        = frames.get("claims",        pd.DataFrame())
    policies      = frames.get("policies",      pd.DataFrame())
    policyholders = frames.get("policyholders", pd.DataFrame())
    beneficiaries = frames.get("beneficiaries", pd.DataFrame())

    # ── Row counts ────────────────────────────────────────────
    results += check_row_counts(frames)

    # ── Null checks ───────────────────────────────────────────
    results += check_no_nulls(claims, "claims",
                               ["claim_number","policy_id","date_of_death","date_filed","claim_amount","status"])
    results += check_no_nulls(policies, "policies",
                               ["policy_number","policyholder_id","face_value","annual_premium","issue_date","status"])
    results += check_no_nulls(policyholders, "policyholders",
                               ["first_name","last_name","date_of_birth"])

    # ── Unique keys ───────────────────────────────────────────
    results.append(check_unique(claims, "claims", "claim_number"))
    results.append(check_unique(policies, "policies", "policy_number"))

    # ── Valid enum values ─────────────────────────────────────
    results.append(check_valid_values(
        claims, "claims", "status",
        {"pending","under_review","approved","denied","paid","withdrawn"}
    ))
    results.append(check_valid_values(
        policies, "policies", "status",
        {"active","lapsed","surrendered","matured","expired"}
    ))

    # ── Positive amounts ──────────────────────────────────────
    results.append(check_positive(claims,   "claims",   "claim_amount"))
    results.append(check_positive(policies, "policies", "face_value"))
    results.append(check_positive(policies, "policies", "annual_premium"))

    # ── Date logic ────────────────────────────────────────────
    results.append(check_date_order(claims, "claims", "date_of_death", "date_filed"))

    # ── Referential integrity ─────────────────────────────────
    if not policies.empty and not policyholders.empty:
        results.append(check_referential_integrity(
            policies, "policyholder_id",
            policyholders, "policyholder_id",
            "policies → policyholders"
        ))
    if not claims.empty and not policies.empty:
        results.append(check_referential_integrity(
            claims, "policy_id",
            policies, "policy_id",
            "claims → policies"
        ))

    # ── Business rules ────────────────────────────────────────
    if not beneficiaries.empty:
        results.append(check_beneficiary_percentages(beneficiaries))
    results.append(check_age_range(policies))

    # ── Summary ───────────────────────────────────────────────
    passed   = sum(1 for r in results if r["status"] == "PASS")
    warnings = sum(1 for r in results if r["status"] == "WARN")
    failures = sum(1 for r in results if r["status"] == "FAIL")
    elapsed  = round(time.time() - start, 2)

    report = {
        "run_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_checks": len(results),
            "passed":        passed,
            "warnings":      warnings,
            "failures":      failures,
            "elapsed_sec":   elapsed,
            "overall_status": "PASS" if failures == 0 else "FAIL",
        },
        "checks": results,
    }

    # ── Save report ───────────────────────────────────────────
    report_path = config.REPORTS_DIR / "validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # ── Log summary ───────────────────────────────────────────
    logger.info("Validation complete — %d checks in %.2fs", len(results), elapsed)
    logger.info("  PASS: %d  |  WARN: %d  |  FAIL: %d", passed, warnings, failures)

    for r in results:
        if r["status"] != "PASS":
            log_fn = logger.warning if r["status"] == "WARN" else logger.error
            log_fn("  [%s] %s — %s", r["status"], r["check"], r["detail"])

    if failures > 0:
        logger.error("Pipeline has %d critical failures — review before loading to cloud", failures)
    else:
        logger.info("All critical checks passed — safe to proceed with load")

    logger.info("Report saved → %s", report_path)
    return report


if __name__ == "__main__":
    from extract import run as extract_run
    from transform import run as transform_run
    data = extract_run()
    data = transform_run(data)
    run(data)
