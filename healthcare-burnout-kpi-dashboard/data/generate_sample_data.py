"""
generate_sample_data.py — Synthetic survey + adherence + initiative data.

Simulates what a real deployment would collect: a quarterly MBI/Mini-Z-style
burnout survey, shift-level standard-work adherence logs, and an initiative
tracker mirroring the DMAIC case study's Improve/Control phases. No real
staff, patients, or hospital data is represented.

Run: python data/generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)

OUT = Path(__file__).parent / "sample"
OUT.mkdir(parents=True, exist_ok=True)

QUARTERS = ["2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"]
PILOT_LAUNCH_QNUM = 4  # checklist + tied recognition pilot goes live in 2025-Q4

UNITS = [
    "Emergency Department",
    "Pediatric ICU",
    "Medical-Surgical",
    "Oncology",
    "Inpatient Rehab",
]
# Baseline safety exposure differs by unit (aggressive/agitated patient contact)
UNIT_SAFETY_BASE = {
    "Emergency Department": 62,
    "Pediatric ICU": 58,
    "Medical-Surgical": 40,
    "Oncology": 30,
    "Inpatient Rehab": 45,
}
UNIT_STAFFING_PRESSURE = {  # baseline workload index
    "Emergency Department": 68,
    "Pediatric ICU": 60,
    "Medical-Surgical": 55,
    "Oncology": 48,
    "Inpatient Rehab": 50,
}

ROLES = ["Nurse", "Allied Health", "Medical Student", "Administrative"]
ROLE_WEIGHTS = [0.50, 0.20, 0.15, 0.15]

ROTATIONS = ["Daily", "Weekly", "Half-Day"]
ROTATION_WEIGHTS = [0.35, 0.40, 0.25]

N_INITIAL_STAFF = 150


def draw_reliability():
    """Bimodal: most staff are consistent, a real minority coast."""
    if rng.random() < 0.68:
        return float(np.clip(rng.beta(6, 2), 0.05, 0.99))
    return float(np.clip(rng.beta(2, 4.5), 0.05, 0.99))


def new_staff_batch(n, start_qnum, next_id):
    ids = [f"S{next_id + i:04d}" for i in range(n)]
    units = rng.choice(UNITS, size=n)
    roles = rng.choice(ROLES, size=n, p=ROLE_WEIGHTS)
    rotations = rng.choice(ROTATIONS, size=n, p=ROTATION_WEIGHTS)
    reliability = np.array([draw_reliability() for _ in range(n)])
    # A chronic offender repeats the same late-arrival/early-departure combo
    # on the same weekday, week after week — a fixed personal trait, not
    # random noise. Far more likely among the least-reliable staff.
    is_chronic = np.array([rng.random() < (0.32 if r < 0.55 else 0.03) for r in reliability])
    chronic_weekday = rng.integers(0, 5, size=n)  # Mon–Fri
    return pd.DataFrame({
        "staff_id": ids, "unit": units, "role": roles,
        "rotation_type": rotations, "reliability_trait": reliability,
        "is_chronic_offender": is_chronic, "chronic_weekday": chronic_weekday,
        "hire_qnum": start_qnum, "tenure_years": 0.0,
    })


roster = new_staff_batch(N_INITIAL_STAFF, 0, 1)
next_id = N_INITIAL_STAFF + 1

survey_rows = []
log_rows = []
log_id = 1

for qnum, quarter in enumerate(QUARTERS):
    pilot_active = qnum >= PILOT_LAUNCH_QNUM

    roster["tenure_years"] = (qnum - roster["hire_qnum"]) * 0.25 + rng.normal(
        0, 0.05, len(roster)
    ).clip(min=0)

    # ---- shift-level adherence log (drives the survey-level rollup) ----
    unit_quarter_adherence = {}
    WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for _, s in roster.iterrows():
        n_shifts = int(rng.integers(10, 18))
        base = s["reliability_trait"] * 100
        is_chronic = bool(s["is_chronic_offender"])
        chronic_wd = int(s["chronic_weekday"])
        for _ in range(n_shifts):
            weekday = int(rng.integers(0, 5))
            noise = rng.normal(0, 6)
            pre = np.clip(base + (6 if pilot_active else 0) + noise, 5, 100)
            during = np.clip(base + 4 + (6 if pilot_active else 0) + rng.normal(0, 5), 5, 100)
            post = np.clip(base - 6 + (8 if pilot_active else 0) + rng.normal(0, 8), 5, 100)

            # Chronic pattern: the same weekday, week after week — dampened
            # (not eliminated) once the pilot's checklist + recognition is live.
            # chronic_pattern must reflect whether the ~20/35-minute deviation
            # actually happened this shift, not just whether it's the staff
            # member's usual day — otherwise a pilot-suppressed occurrence
            # (small minutes) still gets flagged chronic, diluting the average.
            is_chronic_day = is_chronic and weekday == chronic_wd
            is_chronic_hit = is_chronic_day and not (pilot_active and rng.random() < 0.45)
            if is_chronic_hit:
                minutes_late = float(np.clip(rng.normal(20, 3), 10, 30))
                minutes_early = float(np.clip(rng.normal(35, 4), 20, 50))
            else:
                late_chance = 0.12 + (1 - s["reliability_trait"]) * 0.15 - (0.03 if pilot_active else 0)
                early_chance = 0.10 + (1 - s["reliability_trait"]) * 0.15 - (0.03 if pilot_active else 0)
                minutes_late = float(np.clip(rng.normal(8, 5), 0, 20)) if rng.random() < late_chance else 0.0
                minutes_early = float(np.clip(rng.normal(10, 6), 0, 25)) if rng.random() < early_chance else 0.0

            log_rows.append({
                "log_id": log_id, "staff_id": s["staff_id"], "unit": s["unit"],
                "role": s["role"], "rotation_type": s["rotation_type"],
                "quarter": quarter, "quarter_num": qnum,
                "weekday": WEEKDAY_NAMES[weekday],
                "pre_shift_pct": round(pre, 1), "during_shift_pct": round(during, 1),
                "post_shift_pct": round(post, 1),
                "minutes_late": round(minutes_late, 1), "minutes_early": round(minutes_early, 1),
                "arrived_late": bool(minutes_late > 0), "left_early": bool(minutes_early > 0),
                "chronic_pattern": bool(is_chronic_hit),
            })
            log_id += 1

    log_df_q = pd.DataFrame([r for r in log_rows if r["quarter_num"] == qnum])
    log_df_q["adherence_pct"] = log_df_q[["pre_shift_pct", "during_shift_pct", "post_shift_pct"]].mean(axis=1)
    staff_adherence = log_df_q.groupby("staff_id")["adherence_pct"].mean()
    unit_gap = (
        log_df_q.groupby(["unit"])["adherence_pct"].std().fillna(0) * 2.1
    ).clip(0, 100)

    # ---- quarterly survey ----
    for _, s in roster.iterrows():
        sid = s["staff_id"]
        unit, role, rot = s["unit"], s["role"], s["rotation_type"]
        adherence = float(staff_adherence.get(sid, 60))

        workload = np.clip(
            UNIT_STAFFING_PRESSURE[unit] + rng.normal(0, 8)
            + (6 if rot == "Daily" else (-4 if rot == "Half-Day" else 0))
            - (5 if pilot_active else 0), 5, 100,
        )
        accountability_gap = np.clip(
            unit_gap.get(unit, 30) + rng.normal(0, 6)
            + (8 if rot == "Daily" else 0)
            - (6 if pilot_active else 0), 0, 100,
        )
        reward_gap = np.clip(
            55 + rng.normal(0, 12) - qnum * 1.5 - (10 if pilot_active else 0), 0, 100,
        )
        safety_risk = np.clip(
            UNIT_SAFETY_BASE[unit] + rng.normal(0, 10), 0, 100,
        )

        burnout = np.clip(
            0.32 * workload + 0.26 * accountability_gap
            + 0.20 * reward_gap + 0.22 * safety_risk
            + rng.normal(0, 5) - (100 - s["reliability_trait"] * 100) * 0.05,
            0, 100,
        )
        exhaustion = np.clip(burnout + rng.normal(0, 6), 0, 100)
        depersonalization = np.clip(burnout * 0.85 + rng.normal(0, 8), 0, 100)
        accomplishment = np.clip(100 - burnout * 0.6 + rng.normal(0, 10), 0, 100)
        intent_to_leave = np.clip(burnout * 0.7 + rng.normal(0, 10), 0, 100)

        turnover_prob = np.clip((intent_to_leave - 20) / 220, 0.01, 0.18)
        turned_over = rng.random() < turnover_prob and s["tenure_years"] > 0.2

        survey_rows.append({
            "staff_id": sid, "unit": unit, "role": role, "rotation_type": rot,
            "quarter": quarter, "quarter_num": qnum,
            "tenure_years": round(float(s["tenure_years"]), 2),
            "burnout_score": round(float(burnout), 1),
            "exhaustion_score": round(float(exhaustion), 1),
            "depersonalization_score": round(float(depersonalization), 1),
            "accomplishment_score": round(float(accomplishment), 1),
            "workload_index": round(float(workload), 1),
            "accountability_gap_score": round(float(accountability_gap), 1),
            "reward_gap_score": round(float(reward_gap), 1),
            "safety_risk_score": round(float(safety_risk), 1),
            "adherence_checklist_pct": round(adherence, 1),
            "intent_to_leave_score": round(float(intent_to_leave), 1),
            "turned_over": bool(turned_over),
            "pilot_active": bool(pilot_active),
        })

        if turned_over:
            roster.loc[roster["staff_id"] == sid, "tenure_years"] = -999  # mark for removal

    # remove departed staff, backfill with new hires to hold headcount roughly steady
    departed = roster["tenure_years"] == -999
    n_departed = int(departed.sum())
    roster = roster[~departed].reset_index(drop=True)
    if n_departed > 0 and qnum < len(QUARTERS) - 1:
        fresh = new_staff_batch(n_departed, qnum + 1, next_id)
        next_id += n_departed
        roster = pd.concat([roster, fresh], ignore_index=True)

survey_df = pd.DataFrame(survey_rows)
log_df = pd.DataFrame(log_rows)

# ---- initiative tracker (mirrors the DMAIC deck's Improve/Control phases) ----
initiatives = pd.DataFrame([
    {"initiative": "End-of-Shift Checklist + Tied Recognition", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Piloting", "launch_quarter": "2025-Q4",
     "expected_impact": "Fast reduction in adherence-gap resentment", "feasibility": "High"},
    {"initiative": "Manager Rounding & Spot Checks", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Rolled Out", "launch_quarter": "2024-Q4",
     "expected_impact": "Standards visible without feeling punitive", "feasibility": "High"},
    {"initiative": "Peer Accountability Huddles", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Rolled Out", "launch_quarter": "2025-Q1",
     "expected_impact": "Social visibility sustains standards", "feasibility": "High"},
    {"initiative": "Transparent Task-Rotation Assignments", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Rolled Out", "launch_quarter": "2025-Q1",
     "expected_impact": "Removes ambiguity in who covers what", "feasibility": "High"},
    {"initiative": "Protect Peer-Led Potluck Cadence", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Rolled Out", "launch_quarter": "2024-Q4",
     "expected_impact": "Staff-organized morale win — formalize the cadence, don't let leadership take it over", "feasibility": "High"},
    {"initiative": "Introduce & Pre-Plan Low-Cost Motivators", "phase": "Low-Cost",
     "cost_tier": "Low", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Food, massages, extra breaks — genuinely motivating and easy to trial when planned ahead instead of sprung last-minute", "feasibility": "High"},
    {"initiative": "De-escalation & Safety Training", "phase": "Higher-Cost",
     "cost_tier": "Medium", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Reduces injury risk from aggressive, non-verbal behavior", "feasibility": "Medium"},
    {"initiative": "Expanded EAP & Mental Health Benefits", "phase": "Higher-Cost",
     "cost_tier": "Medium", "status": "Piloting", "launch_quarter": "2025-Q3",
     "expected_impact": "Confidential support, no productivity clawback", "feasibility": "Medium"},
    {"initiative": "Tiered Advancement / Care Ladder", "phase": "Higher-Cost",
     "cost_tier": "Medium", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Durable, long-run retention lever", "feasibility": "Medium"},
    {"initiative": "4-Day Work Week + Dedicated 5th-Day Coverage", "phase": "Higher-Cost",
     "cost_tier": "High", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Cuts peak fatigue, preserves continuity", "feasibility": "Medium"},
    {"initiative": "Staffing Ratio Increase", "phase": "Higher-Cost",
     "cost_tier": "High", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Largest reduction in workload exhaustion", "feasibility": "Low"},
    {"initiative": "Documentation & AAC-Device Support Tools", "phase": "Higher-Cost",
     "cost_tier": "Medium", "status": "Not Started", "launch_quarter": None,
     "expected_impact": "Reduces after-hours charting burden", "feasibility": "Medium"},
])

survey_df.to_parquet(OUT / "survey_responses.parquet", index=False)
log_df.to_parquet(OUT / "adherence_log.parquet", index=False)
initiatives.to_parquet(OUT / "initiatives.parquet", index=False)

print(f"survey_responses: {len(survey_df):,} rows")
print(f"adherence_log:     {len(log_df):,} rows")
print(f"initiatives:        {len(initiatives):,} rows")
