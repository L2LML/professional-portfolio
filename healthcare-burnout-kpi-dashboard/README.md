# 🩺 Healthcare Burnout & Adherence KPI Dashboard

An interactive, multi-page Streamlit dashboard that operationalizes the **Measure** phase of the [Healthcare Burnout DMAIC Case Study](../healthcare-burnout-dmaic/) — turning "what would we survey and track" into an actual working tool.

> ⚠️ **Demo dashboard — all data is synthetically generated.** No real staff, patients, or hospital records are shown. In production this connects to a validated MBI/Mini-Z burnout survey and an EHR- or app-based end-of-shift adherence checklist.

---

## 📥 Run It Locally (60 seconds, no setup)

Pre-built sample data is included in the repo.

```bash
git clone https://github.com/L2LML/professional-portfolio.git
cd professional-portfolio/healthcare-burnout-kpi-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open your browser to **http://localhost:8501**

To regenerate the synthetic dataset from scratch: `python data/generate_sample_data.py`

---

## 📋 Dashboard Pages

### 🩺 Executive Summary (`app.py`)
5 KPI cards (burnout score, adherence rate, turnover, accountability gap, safety risk), the four root-cause drivers as a bar chart, a burnout trend line with the pilot launch marked, and a "Units to Watch" risk table.

### 🧭 Root-Cause Drivers
The four "unmotivating characteristics" from the DMAIC fishbone — Workload & Staffing, Accountability, Reward, Safety — broken out by unit and by role, plus a scatter of accountability gap (adherence variance within a team) against burnout score.

### 🔄 Adherence & Rotation Cadence
Adherence rate, late-arrival/early-departure rates, a **Chronic Pattern** view, and a pre-/during-/post-shift completion breakdown, each cut by rotation cadence (Daily / Weekly / Half-Day).

The Chronic Pattern view is the sharpest finding in the dashboard: a subset of staff arrive **~20 minutes late** and leave **~35 minutes early** on the *same weekday, every week* — a fixed personal pattern, not random tardiness — while still being paid for the full shift. The page reports the average minutes late/early for these occurrences, which weekday it concentrates on, and how many staff exhibit it (headcount is reported separately from the minutes figures — they measure different things). It also names the cost that doesn't show up in a paycheck: compliant coworkers absorb the coverage gap and the emotional, physical, and communicative strain of it recurring.

### 📋 Initiative Tracker
Every Improve-phase initiative from the case study, its cost tier and rollout status, and an early pilot-impact comparison (four quarters pre-launch vs. two quarters post-launch) for the checklist + tied-recognition pilot.

---

## 🧮 How the Synthetic Data Is Built

`data/generate_sample_data.py` simulates six quarters (2024-Q4 → 2026-Q1) for ~150 staff across 5 units, 4 roles, and 3 rotation cadences:

- Each staff member has a persistent, bimodal **reliability trait** — most are highly consistent, a real minority coast — which drives their shift-level checklist completion (`adherence_log`, ~12k rows) and, in turn, the survey-level `adherence_checklist_pct`.
- **Accountability Gap** is computed as the *variance* in adherence within a unit-quarter, not a self-report — the objective, measurable form of "some people do it right, some don't."
- A minority of staff are flagged as **chronic-pattern** offenders: a fixed weekday on which they consistently arrive ~20 minutes late and leave ~35 minutes early (both drawn from a normal distribution around those targets). The flag is only set on shifts where that actual deviation occurred — a shift suppressed by the pilot's effect isn't miscounted as chronic just because it fell on the staff member's usual day.
- Burnout score is a weighted composite of the four root-cause drivers plus noise.
- A **pilot effect** is baked in starting 2025-Q4 (checklist + tied recognition launch): burnout, workload, accountability gap, and reward gap improve modestly; adherence rises — giving the dashboard an honest before/after story rather than a flat baseline.
- Turnover is probabilistic based on intent-to-leave, with departed staff backfilled by new hires each quarter to hold headcount steady.

---

## 🎨 Design System

Colors were chosen and validated with a CVD-safety/contrast checker rather than picked by eye — root-cause drivers, rotation cadence, and initiative status each use a fixed, non-overlapping categorical palette so the same color always carries the same meaning across every page.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `streamlit` | Multi-page dashboard framework |
| `plotly` | Interactive charts |
| `pandas` / `numpy` | Synthetic data generation, aggregation |
| `pyarrow` | Parquet read/write |

---

## Skills Demonstrated

Dashboard design · data visualization · synthetic data modeling · KPI definition · DMAIC Measure-phase operationalization · Python (pandas, Streamlit, Plotly).

---

*Lisa Lewandowski · [GitHub: L2LML](https://github.com/L2LML) · Companion to the [Healthcare Burnout DMAIC Case Study](../healthcare-burnout-dmaic/)*
