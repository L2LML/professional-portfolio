"""
generate_sample_data.py — Generate realistic sample Parquet files for the dashboard.

Run this once to create the data/ directory files.
Based on the life-insurance-claims-db schema and seed data.

Usage:
    python data/generate_sample_data.py
"""

import random
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUT = Path(__file__).parent / "sample"
OUT.mkdir(exist_ok=True)

# ── Reference data ────────────────────────────────────────────
POLICY_TYPES = ["Term Life", "Whole Life", "Universal Life", "Variable Life", "Final Expense"]
AGENTS = [
    "James Thornton", "Patricia Nguyen", "Robert Alvarez", "Sandra Williams",
    "Kevin Okafor", "Diane Kowalski", "Marcus Jefferson", "Linda Patel",
]
AGENT_STATES = ["MI", "MI", "OH", "MI", "IN", "MI", "MI", "OH"]
EXAMINERS = ["Sarah Donovan", "Michael Torres", "James Whitfield"]
STATES = ["MI"] * 10 + ["OH"] * 5 + ["IN"] * 5 + ["IL"] * 3 + ["WI"] * 2
FIRST_NAMES = ["Harold", "Dorothy", "Raymond", "Carol", "Walter", "Barbara",
               "Thomas", "Patricia", "George", "Ruth", "Dennis", "Helen",
               "Frank", "Gloria", "Arthur", "Sylvia", "Jerome", "Norma",
               "Calvin", "Mildred", "Derek", "Richard", "Nancy", "Charles",
               "Betty", "William", "Sandra", "Joseph", "Donna"]
LAST_NAMES = ["Bennett", "Castillo", "Foster", "Hutchinson", "Simmons", "Nguyen",
              "O'Brien", "Washington", "Martinez", "Thompson", "Clarke", "Okafor",
              "Deluca", "Reed", "Yamamoto", "Hartman", "Banks", "Espinoza",
              "Price", "Grant", "Holloway", "Anderson", "Wilson", "Harris",
              "Moore", "Jackson", "Taylor", "White", "Lewis"]
CAUSES = ["Cardiac arrest", "Cancer", "Natural causes", "Accidental",
          "Stroke", "COVID-19", "Heart disease", "Respiratory failure"]
CAUSE_WEIGHTS = [0.25, 0.20, 0.18, 0.12, 0.10, 0.08, 0.05, 0.02]
RELATIONSHIPS = ["Spouse", "Child", "Parent", "Sibling", "Trust", "Estate"]

def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def age_band(age):
    if age <= 35: return "18–35 Young Adult"
    if age <= 50: return "36–50 Middle Age"
    if age <= 65: return "51–65 Pre-Retirement"
    return "65+ Senior"

def tenure_tier(years):
    if years < 3:  return "New (0–2 yrs)"
    if years < 6:  return "Establishing (3–5 yrs)"
    if years < 11: return "Loyal (6–10 yrs)"
    return "Long-Term (11+ yrs)"

# ── Policyholders ─────────────────────────────────────────────
n_ph = 29
policyholders = pd.DataFrame({
    "policyholder_id": range(1, n_ph + 1),
    "first_name":  random.sample(FIRST_NAMES, n_ph),
    "last_name":   random.sample(LAST_NAMES,  n_ph),
    "date_of_birth": [rand_date(date(1930, 1, 1), date(1990, 12, 31)) for _ in range(n_ph)],
    "address_state": random.choices(STATES, k=n_ph),
    "smoker": [random.random() < 0.15 for _ in range(n_ph)],
})
policyholders["policyholder_since"] = [
    rand_date(date(1995, 1, 1), date(2020, 12, 31)) for _ in range(n_ph)
]
today = pd.Timestamp.today()
policyholders["current_age"] = (
    (today - pd.to_datetime(policyholders["date_of_birth"])).dt.days / 365.25
).astype(int)
policyholders["tenure_years"] = (
    (today - pd.to_datetime(policyholders["policyholder_since"])).dt.days / 365.25
).round(1)
policyholders["tenure_tier"] = policyholders["tenure_years"].apply(tenure_tier)
policyholders["full_name"] = policyholders["first_name"] + " " + policyholders["last_name"]

# ── Policies ──────────────────────────────────────────────────
n_p = 35
policies = pd.DataFrame({
    "policy_id":       range(1, n_p + 1),
    "policy_number":   [f"POL-{2000+i//3:04d}-{i:05d}" for i in range(1, n_p + 1)],
    "policyholder_id": random.choices(range(1, n_ph + 1), k=n_p),
    "policy_type":     random.choices(POLICY_TYPES, weights=[35, 30, 20, 10, 5], k=n_p),
    "agent_name":      random.choices(AGENTS, k=n_p),
    "agent_state":     None,
    "face_value":      np.random.choice(
                           [20000, 75000, 100000, 150000, 250000, 300000, 400000, 500000, 750000, 1000000],
                           p=[0.05, 0.08, 0.12, 0.12, 0.18, 0.12, 0.12, 0.12, 0.05, 0.04],
                           size=n_p),
    "annual_premium":  None,
    "issue_date":      [rand_date(date(1998, 1, 1), date(2023, 1, 1)) for _ in range(n_p)],
    "status":          random.choices(["active", "active", "active", "active", "expired", "lapsed"],
                                       weights=[70, 70, 70, 70, 10, 10], k=n_p),
})
# Agent state lookup
agent_state_map = dict(zip(AGENTS, AGENT_STATES))
policies["agent_state"] = policies["agent_name"].map(agent_state_map)

# Compute age at issue
policies = policies.merge(
    policyholders[["policyholder_id", "date_of_birth", "full_name", "address_state",
                   "smoker", "policyholder_since", "tenure_years", "tenure_tier", "current_age"]],
    on="policyholder_id", how="left"
)
policies["age_at_issue"] = (
    (pd.to_datetime(policies["issue_date"]) - pd.to_datetime(policies["date_of_birth"])).dt.days / 365.25
).astype(int)
policies["age_band"] = policies["age_at_issue"].apply(age_band)

# Premium: roughly 0.5-1.5% of face value per year, higher for older/smoker
base_rate = np.random.uniform(0.005, 0.015, n_p)
smoker_mult = np.where(policies["smoker"], 1.3, 1.0)
policies["annual_premium"] = (policies["face_value"] * base_rate * smoker_mult).round(0)
policies["years_in_force"] = (
    (today - pd.to_datetime(policies["issue_date"])).dt.days / 365.25
).round(1)
policies["premium_per_1k_coverage"] = (
    policies["annual_premium"] / policies["face_value"] * 1000
).round(2)
policies["is_permanent"] = policies["policy_type"].isin(["Whole Life", "Universal Life", "Variable Life", "Final Expense"])

# ── Claims ────────────────────────────────────────────────────
n_c = 130
claim_policies = random.choices(range(1, n_p + 1), k=n_c)

statuses = random.choices(
    ["paid", "paid", "paid", "approved", "under_review", "pending", "denied"],
    weights=[30, 30, 20, 15, 15, 10, 10], k=n_c
)

filed_dates = [rand_date(date(2018, 1, 1), date(2024, 11, 1)) for _ in range(n_c)]
death_dates = [fd - timedelta(days=random.randint(3, 45)) for fd in filed_dates]
causes = random.choices(CAUSES, weights=CAUSE_WEIGHTS, k=n_c)

claims_raw = []
for i in range(n_c):
    pid  = claim_policies[i]
    pol  = policies[policies["policy_id"] == pid].iloc[0]
    pct  = random.choice([100, 70, 60, 50, 40, 30])
    amt  = round(float(pol["face_value"]) * pct / 100, 2)
    stat = statuses[i]
    fd   = filed_dates[i]

    days_decision = random.randint(15, 75) if stat in ("paid","approved","denied") else None
    approved = fd + timedelta(days=days_decision) if stat in ("paid","approved") and days_decision else None
    denied   = fd + timedelta(days=days_decision) if stat == "denied" and days_decision else None
    paid_dt  = (approved + timedelta(days=random.randint(3,10))) if stat == "paid" and approved else None

    claims_raw.append({
        "claim_id":           i + 1,
        "claim_number":       f"CLM-{fd.year}-{i+1:05d}",
        "claim_status":       stat,
        "date_of_death":      death_dates[i],
        "date_filed":         fd,
        "date_approved":      approved,
        "date_denied":        denied,
        "date_paid":          paid_dt,
        "cause_of_death":     causes[i],
        "claim_amount":       amt,
        "assigned_examiner":  random.choice(EXAMINERS) if stat != "pending" else None,
        "denial_reason":      ("Policy lapsed at time of death" if i % 2 == 0
                               else "Within 2-year contestability period") if stat == "denied" else None,
        "policy_id":          pid,
        "policy_number":      pol["policy_number"],
        "face_value":         pol["face_value"],
        "annual_premium":     pol["annual_premium"],
        "age_at_issue":       pol["age_at_issue"],
        "age_band":           pol["age_band"],
        "issue_date":         pol["issue_date"],
        "policy_status":      pol["status"],
        "policy_type":        pol["policy_type"],
        "is_permanent":       pol["is_permanent"],
        "policyholder_id":    pol["policyholder_id"],
        "policyholder_name":  pol["full_name"],
        "date_of_birth":      pol["date_of_birth"],
        "address_state":      pol["address_state"],
        "smoker":             pol["smoker"],
        "policyholder_since": pol["policyholder_since"],
        "tenure_years":       pol["tenure_years"],
        "tenure_tier":        pol["tenure_tier"],
        "beneficiary_name":   f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "relationship":       random.choice(RELATIONSHIPS),
        "beneficiary_pct":    pct,
        "agent_name":         pol["agent_name"],
        "agent_state":        pol["agent_state"],
    })

claims_fact = pd.DataFrame(claims_raw)

# Computed fields
claims_fact["days_to_decision"] = np.where(
    claims_fact["date_approved"].notna(),
    (pd.to_datetime(claims_fact["date_approved"]) - pd.to_datetime(claims_fact["date_filed"])).dt.days,
    np.where(
        claims_fact["date_denied"].notna(),
        (pd.to_datetime(claims_fact["date_denied"]) - pd.to_datetime(claims_fact["date_filed"])).dt.days,
        np.nan
    )
)
open_mask = claims_fact["claim_status"].isin(["pending","under_review"])
claims_fact["days_open"] = np.where(
    open_mask,
    (today - pd.to_datetime(claims_fact["date_filed"])).dt.days,
    np.nan
)
claims_fact["aging_flag"] = np.where(
    claims_fact["days_open"] > 60, "OVERDUE",
    np.where(claims_fact["days_open"] > 30, "AGING",
    np.where(open_mask, "ON TRACK", None))
)
claims_fact["claim_year"]    = pd.to_datetime(claims_fact["date_filed"]).dt.year
claims_fact["claim_month"]   = pd.to_datetime(claims_fact["date_filed"]).dt.month
claims_fact["claim_quarter"] = pd.to_datetime(claims_fact["date_filed"]).dt.quarter
claims_fact["is_high_value"] = claims_fact["claim_amount"] > 250_000

# ── Agent summary ─────────────────────────────────────────────
agent_df = pd.DataFrame({
    "agent_name":  AGENTS,
    "agent_state": AGENT_STATES,
    "hire_date":   [rand_date(date(2015, 1, 1), date(2022, 12, 31)) for _ in AGENTS],
})

# ── Save all files ────────────────────────────────────────────
claims_fact.to_parquet(OUT / "claims_fact.parquet",   index=False)
policies.to_parquet(   OUT / "policies.parquet",      index=False)
policyholders.to_parquet(OUT / "policyholders.parquet", index=False)
agent_df.to_parquet(   OUT / "agents.parquet",        index=False)

print(f"✅ Sample data generated → {OUT}")
print(f"   claims_fact:    {len(claims_fact)} rows")
print(f"   policies:       {len(policies)} rows")
print(f"   policyholders:  {len(policyholders)} rows")
print(f"   agents:         {len(agent_df)} rows")

if __name__ == "__main__":
    pass
