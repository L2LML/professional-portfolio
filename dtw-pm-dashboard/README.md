# ✈️ DTW IT Center — PM Portfolio Dashboard

An interactive, multi-page Streamlit dashboard that operationalizes the [DTW IT Center PM Toolkit](../dtw-it-center-pm-toolkit/) — turning its Charter, PM Tracking Workbook, and Status/Closeout Report documents into a rollup you can click through instead of opening Word/Excel files one at a time.

> ⚠️ **Demo dashboard — illustrative scenario.** Both projects are self-directed, candidate work for an Infrastructure/IT Project Manager role, not a record of an actual Metro Detroit Airport / Wayne County Airport Authority engagement. Every figure traces back to the toolkit's published documents; only the monthly time series between those documents' known checkpoints (current status-report month, final closeout) is synthesized, so the trend charts have something to show.

---

## 📥 Run It Locally (60 seconds, no setup)

Pre-built sample data is included in the repo.

```bash
git clone https://github.com/L2LML/professional-portfolio.git
cd professional-portfolio/dtw-pm-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open your browser to **http://localhost:8501**

To regenerate the dataset from scratch: `python data/generate_sample_data.py`

---

## 📋 Dashboard Pages

### ✈️ Portfolio Executive Summary (`app.py`)
Combined KPIs across both projects (approved budget, actual spend, contingency remaining, weighted schedule % complete, open risks), a status card per project with RAG badges, small-multiple cumulative-spend and cumulative-schedule trend charts (planned vs. actual, with the status-report snapshot month marked), and a cross-project "Risks to Watch" table.

### 🗓️ Schedule & Milestones
A Gantt-style view of each project's Work Breakdown Structure — task bars colored by status (Complete / In Progress / Not Started), plus the milestone tracker table.

### 💰 Budget & Cost Tracking
Budgeted-vs-actual by cost category (grouped bar), plus a variance table with committed/actual/variance/% used, per project.

### ⚠️ Risk & Issue Management
A probability × impact risk heatmap (bubble size = score, color = status), the full risk register, and the issue/change log.

### 🤝 Stakeholders & Vendors
A power/interest grid (Keep Satisfied / Manage Closely / Monitor / Keep Informed) for each project's stakeholder register, and a vendor/contractor register with contract value by performance rating.

### 📚 Lessons Learned & Closeout
Final summary vs. baseline (schedule, budget, scope), plus each project's Closeout Report lessons learned — What Went Well, What Could Improve, Recommendations, and Outstanding Items / Transition.

---

## 🧮 How the Data Is Built

`data/generate_sample_data.py` writes every static table — schedule tasks, budget categories, risks, issues, vendors, stakeholders — by copying the exact figures from the two projects' PM Tracking Workbooks in [`../dtw-it-center-pm-toolkit/`](../dtw-it-center-pm-toolkit/), so the dashboard tells the same story as the published documents rather than a separately-invented one.

The only synthesized data is the monthly time series: each toolkit document only captures two fixed points in time (the status-report month and the final closeout), so a monthly history is interpolated between those anchors with a smoothstep ease + small seeded noise, purely to give the burn-down and schedule-curve charts a trend to show. A vertical marker on each trend chart shows exactly which month the toolkit's status report was drawn from.

---

## 🎨 Design System

Colors reuse the exact navy/steel/light-blue hex values from the toolkit's Word and Excel documents, so the dashboard reads as the same designed body of work rather than a different visual language. The two project-identity colors and the shared status (good/warning/critical) triad were chosen and validated with the data-viz skill's CVD-safety/contrast checker rather than picked by eye — see `data/colors.py` for the exact validation commands and results.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `streamlit` | Multi-page dashboard framework |
| `plotly` | Interactive charts |
| `pandas` / `numpy` | Sample data generation, aggregation |
| `pyarrow` | Parquet read/write |

---

## Skills Demonstrated

Dashboard design · data visualization · PM data modeling (schedule/budget/risk/stakeholder/vendor) · KPI rollup design · Python (pandas, Streamlit, Plotly).

---

*Lisa Lewandowski · [GitHub: L2LML](https://github.com/L2LML) · Companion to the [DTW IT Center PM Toolkit](../dtw-it-center-pm-toolkit/)*
