# Insurance Claims BI Dashboard

An interactive business intelligence dashboard built with Streamlit and Plotly, visualizing life insurance claims operations data. The third tier in the insurance data portfolio — SQL → ETL Pipeline → Dashboard.

---

## Live Dashboard

> **Run locally in 60 seconds — no database required.**
> Pre-generated sample data is included in the repo.

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Dashboard Pages

### 🏦 Executive Summary (`app.py`)
- KPI cards: total claims, total paid out, denial rate, avg decision time, open claims
- Claims by status — donut chart
- Monthly claims volume — trend line
- Open high-value claims table (>$250K) with aging flags

### 📋 Claims Operations
- Open claims by aging status (On Track / Aging / Overdue)
- Examiner workload — claims count + average days open per examiner
- Claims distribution by cause of death with denial rate overlay
- Full open claims detail table

### 💰 Financial Analysis
- Total payouts by policy type
- Annual premium revenue vs. claim exposure by product line
- Cumulative payout running total over time
- Denial rate analysis and reason breakdown

### 👥 Customer Segments
- Policy count and claim rate by age band at issuance (18–35 / 36–50 / 51–65 / 65+)
- Premium revenue vs. claim exposure by customer tenure tier
- **Age × Tenure Profitability Matrix** — heatmap showing premium-to-claim ratio by segment

### 🏅 Agent Performance
- Premium revenue leaderboard (horizontal bar)
- Policies written vs. claims filed scatter plot (bubble size = premium revenue)
- Full agent leaderboard table with conditional formatting

---

## Architecture

```
life-insurance-claims-db/     ← PostgreSQL schema + SQL queries
        ↓
insurance-cloud-migration/    ← Python ETL — Extract, Transform, Validate, Load
        ↓
insurance-dashboard/          ← THIS PROJECT — Streamlit + Plotly BI layer
    data/sample/*.parquet     ← Pre-generated sample data (works standalone)
```

---

## Files

| File | Purpose |
|------|---------|
| `app.py` | Executive Summary — main entry point |
| `pages/01_Claims_Operations.py` | Claims aging, examiner workload, cause analysis |
| `pages/02_Financial_Analysis.py` | Payouts, revenue vs. exposure, running totals |
| `pages/03_Customer_Segments.py` | Age band, tenure cohort, profitability matrix heatmap |
| `pages/04_Agent_Performance.py` | Agent leaderboard and scatter analysis |
| `data/load_data.py` | Cached data loader — reads Parquet files |
| `data/generate_sample_data.py` | Re-generate sample data if needed |
| `data/sample/*.parquet` | Pre-built sample data (130 claims, 35 policies) |
| `.streamlit/config.toml` | Dashboard theme — navy/blue professional palette |

---

## Technologies

| Library | Purpose |
|---------|---------|
| `streamlit` | Dashboard framework — pages, sidebar, metrics, layout |
| `plotly` | Interactive charts — bar, line, scatter, pie, heatmap |
| `pandas` | Data loading, filtering, aggregation |
| `pyarrow` | Parquet file reading |

---

## Skills Demonstrated

| Skill | Detail |
|-------|--------|
| **Streamlit** | Multi-page app, sidebar filters, metrics, `st.cache_data` |
| **Plotly** | Bar, line, scatter, donut, heatmap — all interactive |
| **Data Visualization** | Business-focused chart design for insurance operations |
| **Dashboard Design** | KPI cards, filter-driven views, conditional formatting |
| **pandas** | GroupBy, merge, pivot, aggregation |
| **Data Storytelling** | Each page tells a clear operational or financial story |

---

*Lisa Lewandowski · [GitHub: L2LML](https://github.com/L2LML)*
