"""
generate_sample_data.py — Generate realistic sample Parquet files for the dashboard.

Run this once to create the data/sample directory files.

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
    "Thomas Greene", "Angela Reyes",
]
AGENT_STATES = ["MI", "MI", "OH", "MI", "IN", "MI", "MI", "OH", "MI", "IN"]

# Each agent specializes in certain products
AGENT_PRODUCT_WEIGHTS = {
    "James Thornton":   [55, 25, 10,  5,  5],   # Term Life specialist
    "Patricia Nguyen":  [15, 55, 20,  5,  5],   # Whole Life specialist
    "Robert Alvarez":   [25, 20, 45,  5,  5],   # Universal Life specialist
    "Sandra Williams":  [40, 30, 15, 10,  5],   # Balanced
    "Kevin Okafor":     [50, 20, 10,  5, 15],   # Term + Final Expense
    "Diane Kowalski":   [20, 45, 25,  5,  5],   # Whole Life leaning
    "Marcus Jefferson": [35, 30, 25,  5,  5],   # Balanced
    "Linda Patel":      [10, 15, 15, 10, 50],   # Final Expense specialist
    "Thomas Greene":    [50, 25, 15,  5,  5],   # Term Life
    "Angela Reyes":     [20, 25, 40, 10,  5],   # Universal Life leaning
}

EXAMINERS = [
    "Sarah Donovan", "Michael Torres", "James Whitfield",
    "Rachel Kim", "David Osei",
]

# Better geographic spread
STATES = (
    ["MI"] * 8 + ["OH"] * 5 + ["IN"] * 4 +
    ["IL"] * 4 + ["WI"] * 3 + ["MN"] * 2 +
    ["KY"] * 2 + ["TN"] * 2
)

FIRST_NAMES = [
    "Harold", "Dorothy", "Raymond", "Carol", "Walter", "Barbara",
    "Thomas", "Patricia", "George", "Ruth", "Dennis", "Helen",
    "Frank", "Gloria", "Arthur", "Sylvia", "Jerome", "Norma",
    "Calvin", "Mildred", "Derek", "Richard", "Nancy", "Charles",
    "Betty", "William", "Sandra", "Joseph", "Donna", "Edward",
    "Margaret", "James", "Frances", "Robert", "Alice", "John",
    "Evelyn", "Michael", "Shirley", "David", "Virginia", "Steven",
    "Martha", "Kenneth", "Rose", "Brian", "Diane", "Gary",
    "Janet", "Larry",
]
LAST_NAMES = [
    "Bennett", "Castillo", "Foster", "Hutchinson", "Simmons", "Nguyen",
    "O'Brien", "Washington", "Martinez", "Thompson", "Clarke", "Okafor",
    "Deluca", "Reed", "Yamamoto", "Hartman", "Banks", "Espinoza",
    "Price", "Grant", "Holloway", "Anderson", "Wilson", "Harris",
    "Moore", "Jackson", "Taylor", "White", "Lewis", "Robinson",
    "Walker", "Hall", "Allen", "Young", "King", "Wright",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans",
]

CAUSES = ["Cardiac arrest", "Cancer", "Natural causes", "Accidental",
          "Stroke", "COVID-19", "Heart disease", "Respiratory failure"]
CAUSE_WEIGHTS = [0.25, 0.20, 0.18, 0.12, 0.10, 0.08, 0.05, 0.02]

# Realistic decision days per cause — accidental takes longest (investigation required)
CAUSE_DECISION_DAYS = {
    "Natural causes":      (10, 30),
    "Cardiac arrest":      (12, 35),
    "Heart disease":       (12, 35),
    "Stroke":              (15, 40),
    "Respiratory failure": (15, 40),
    "Cancer":              (15, 45),
    "COVID-19":            (20, 50),
    "Accidental":          (25, 75),
}

DENIAL_REASONS = [
    "Policy lapsed at time of death",
    "Within 2-year contestability period",
    "Material misrepresentation on application",
    "Cause of death excluded under policy terms",
    "Beneficiary designation dispute",
]

RELATIONSHIPS = ["Spouse", "Child", "Parent", "Sibling", "Trust", "Estate"]

# Winter months peak for cardiac/natural causes
MONTH_WEIGHTS = [1.3, 1.2, 1.0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.9, 1.0, 1.1, 1.4]


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


def face_value_for_age(age):
    """Age-appropriate face values — younger = larger term, seniors = smaller final expense."""
    if age <= 35:
        return int(np.random.choice(
            [100000, 150000, 250000, 300000, 400000, 500000],
            p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05]
        ))
    elif age <= 50:
        return int(np.random.choice(
            [150000, 250000, 300000, 400000, 500000, 750000, 1000000],
            p=[0.15, 0.20, 0.20, 0.20, 0.15, 0.07, 0.03]
        ))
    elif age <= 65:
        return int(np.random.choice(
            [75000, 100000, 150000, 250000, 300000, 400000, 500000],
            p=[0.10, 0.15, 0.20, 0.25, 0.15, 0.10, 0.05]
        ))
    else:
        return int(np.random.choice(
            [20000, 30000, 50000, 75000, 100000, 150000],
            p=[0.25, 0.25, 0.25, 0.15, 0.07, 0.03]
        ))


# ── Policyholders ─────────────────────────────────────────────
n_ph = 80
policyholders = pd.DataFrame({
    "policyholder_id": range(1, n_ph + 1),
    "first_name":  random.choices(FIRST_NAMES, k=n_ph),
    "last_name":   random.choices(LAST_NAMES,  k=n_ph),
    "date_of_birth": [rand_date(date(1930, 1, 1), date(1990, 12, 31)) for _ in range(n_ph)],
    "address_state": random.choices(STATES, k=n_ph),
    "smoker": [random.random() < 0.15 for _ in range(n_ph)],
})
policyholders["policyholder_since"] = [
    rand_date(date(1990, 1, 1), date(2022, 12, 31)) for _ in range(n_ph)
]
today = pd.Timestamp.today()
policyholders["current_age"] = (
    (today - pd.to_datetime(policyholders["date_of_birth"])).dt.days / 365.25
).astype(int)
policyholders["tenure_years"] = (
    (today - pd.to_datetime(policyholders["policyholder_since"])).dt.days / 365.25
).round(1)
policyholders["tenure_tier"] = policyholders["tenure_years"].apply(tenure_tier)
policyholders["full_name"]   = policyholders["first_name"] + " " + policyholders["last_name"]

# ── Policies ──────────────────────────────────────────────────
n_p = 150
agent_state_map = dict(zip(AGENTS, AGENT_STATES))
policies_raw = []

for i in range(n_p):
    ph_id = random.randint(1, n_ph)
    ph    = policyholders[policyholders["policyholder_id"] == ph_id].iloc[0]
    agent = random.choice(AGENTS)

    # Agent specialization
    policy_type = random.choices(POLICY_TYPES, weights=AGENT_PRODUCT_WEIGHTS[agent])[0]

    # Final Expense only for policyholders 55+
    if policy_type == "Final Expense" and ph["current_age"] < 55:
        policy_type = "Term Life"

    issue_date   = rand_date(date(1995, 1, 1), date(2023, 6, 1))
    age_at_issue = max(18, int(
        (pd.Timestamp(issue_date) - pd.Timestamp(ph["date_of_birth"])).days / 365.25
    ))
    fv = face_value_for_age(age_at_issue)

    # Lapse probability tied to tenure — newer customers lapse more
    tenure_yrs = ph["tenure_years"]
    lapse_prob = 0.20 if tenure_yrs < 3 else (0.08 if tenure_yrs < 6 else 0.02)
    status = random.choices(
        ["active", "expired", "lapsed"],
        weights=[1 - lapse_prob, lapse_prob * 0.4, lapse_prob * 0.6]
    )[0]

    policies_raw.append({
        "policy_id":          i + 1,
        "policy_number":      f"POL-{2000 + i // 5:04d}-{i + 1:05d}",
        "policyholder_id":    ph_id,
        "policy_type":        policy_type,
        "agent_name":         agent,
        "agent_state":        agent_state_map[agent],
        "face_value":         fv,
        "annual_premium":     None,
        "issue_date":         issue_date,
        "status":             status,
        "full_name":          ph["full_name"],
        "address_state":      ph["address_state"],
        "smoker":             ph["smoker"],
        "date_of_birth":      ph["date_of_birth"],
        "current_age":        ph["current_age"],
        "tenure_years":       ph["tenure_years"],
        "tenure_tier":        ph["tenure_tier"],
        "policyholder_since": ph["policyholder_since"],
        "age_at_issue":       age_at_issue,
        "age_band":           age_band(age_at_issue),
    })

policies = pd.DataFrame(policies_raw)

# Premium: 3–7% of face value, higher for smokers
base_rate   = np.random.uniform(0.03, 0.07, n_p)
smoker_mult = np.where(policies["smoker"], 1.35, 1.0)
policies["annual_premium"] = (policies["face_value"] * base_rate * smoker_mult).round(0)
policies["years_in_force"] = (
    (today - pd.to_datetime(policies["issue_date"])).dt.days / 365.25
).round(1)
policies["premium_per_1k_coverage"] = (
    policies["annual_premium"] / policies["face_value"] * 1000
).round(2)
policies["is_permanent"] = policies["policy_type"].isin(
    ["Whole Life", "Universal Life", "Variable Life", "Final Expense"]
)

# ── Claims — one per policy, ~50% of policies have a claim ────
claim_policy_ids = random.sample(range(n_p), k=int(n_p * 0.50))
n_c = len(claim_policy_ids)

statuses = random.choices(
    ["paid", "approved", "under_review", "pending", "denied"],
    weights=[28, 12, 20, 18, 10], k=n_c
)
causes = random.choices(CAUSES, weights=CAUSE_WEIGHTS, k=n_c)


def rand_filed_date(status):
    """Growing YoY volume + seasonal winter peaks for historical claims."""
    today_d = date.today()
    if status in ("pending", "under_review"):
        days_ago = random.choices(
            [random.randint(1, 29),
             random.randint(30, 44),
             random.randint(45, 90)],
            weights=[45, 30, 25]
        )[0]
        return today_d - timedelta(days=days_ago)
    else:
        # 2022=25%, 2023=35%, 2024=40% — growing claim volume year over year
        yr    = random.choices([2022, 2023, 2024], weights=[25, 35, 40])[0]
        month = random.choices(range(1, 13), weights=MONTH_WEIGHTS)[0]
        max_day = 28 if month == 2 else (30 if month in [4, 6, 9, 11] else 31)
        day = random.randint(1, max_day)
        try:
            return date(yr, month, day)
        except ValueError:
            return date(yr, month, 28)


filed_dates = [rand_filed_date(statuses[i]) for i in range(n_c)]
death_dates = [fd - timedelta(days=random.randint(3, 45)) for fd in filed_dates]

claims_raw = []
for i in range(n_c):
    pid   = claim_policy_ids[i] + 1   # convert 0-indexed to 1-indexed policy_id
    pol   = policies[policies["policy_id"] == pid].iloc[0]
    stat  = statuses[i]
    fd    = filed_dates[i]
    cause = causes[i]

    # Mostly 100% of face value — partial payouts are rare
    pct = random.choices([100, 75, 50], weights=[85, 10, 5])[0]
    amt = round(float(pol["face_value"]) * pct / 100, 2)

    # Realistic decision time based on cause of death
    day_range     = CAUSE_DECISION_DAYS.get(cause, (15, 60))
    days_decision = random.randint(*day_range) if stat in ("paid", "approved", "denied") else None

    approved = fd + timedelta(days=days_decision) if stat in ("paid", "approved") and days_decision else None
    denied   = fd + timedelta(days=days_decision) if stat == "denied" and days_decision else None
    paid_dt  = (approved + timedelta(days=random.randint(3, 10))) if stat == "paid" and approved else None

    claims_raw.append({
        "claim_id":           i + 1,
        "claim_number":       f"CLM-{fd.year}-{i + 1:05d}",
        "claim_status":       stat,
        "date_of_death":      death_dates[i],
        "date_filed":         fd,
        "date_approved":      approved,
        "date_denied":        denied,
        "date_paid":          paid_dt,
        "cause_of_death":     cause,
        "claim_amount":       amt,
        "assigned_examiner":  random.choice(EXAMINERS) if stat != "pending" else None,
        "denial_reason":      random.choice(DENIAL_REASONS) if stat == "denied" else None,
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

# ── Computed fields ───────────────────────────────────────────
claims_fact["days_to_decision"] = np.where(
    claims_fact["date_approved"].notna(),
    (pd.to_datetime(claims_fact["date_approved"]) - pd.to_datetime(claims_fact["date_filed"])).dt.days,
    np.where(
        claims_fact["date_denied"].notna(),
        (pd.to_datetime(claims_fact["date_denied"]) - pd.to_datetime(claims_fact["date_filed"])).dt.days,
        np.nan
    )
)
open_mask = claims_fact["claim_status"].isin(["pending", "under_review"])
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
    "hire_date":   [rand_date(date(2010, 1, 1), date(2022, 12, 31)) for _ in AGENTS],
})

# ── Save all files ────────────────────────────────────────────
claims_fact.to_parquet(  OUT / "claims_fact.parquet",   index=False)
policies.to_parquet(     OUT / "policies.parquet",      index=False)
policyholders.to_parquet(OUT / "policyholders.parquet", index=False)
agent_df.to_parquet(     OUT / "agents.parquet",        index=False)

print(f"✅ Sample data generated → {OUT}")
print(f"   claims_fact:    {len(claims_fact)} rows")
print(f"   policies:       {len(policies)} rows")
print(f"   policyholders:  {len(policyholders)} rows")
print(f"   agents:         {len(agent_df)} rows")

if __name__ == "__main__":
    pass
