# 📊 Insurance Claims BI Dashboard

An interactive, multi-page business intelligence dashboard for life insurance claims operations. Built with Python, Streamlit, and Plotly — the third tier of a full data engineering portfolio that starts with a PostgreSQL database and a Python ETL pipeline.

> ⚠️ **Demo dashboard — all data is synthetically generated.** No real policyholders, claims, or financial figures are shown. In production this connects directly to the Life Insurance Claims PostgreSQL database via the Python ETL pipeline (both included in this portfolio).

---

## 🚀 View the Live Dashboard

**👉 [https://lisa-insurance-claims.streamlit.app](https://lisa-insurance-claims.streamlit.app)**

Opens instantly in any browser — no login, no install required.

---

## 📥 Run It Locally (60 seconds, no database needed)

Pre-built sample data is included in the repo — no setup required.

```bash
# 1. Clone the portfolio repo
git clone https://github.com/L2LML/professional-portfolio.git
cd professional-portfolio/insurance-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

Open your browser to **http://localhost:8501**

---

## 📋 Dashboard Pages

### 🏦 Executive Summary (`app.py`)
The landing page. Shows the health of the entire claims operation at a glance.

| What you see | What it tells you |
|---|---|
| **5 KPI cards with trend arrows** | Total claims, Loss Ratio, Total Paid Out, Avg Decision Time, Pending Reserve — each compared to the prior year (🟢 improving / 🔴 worsening) |
| **Claims by Status donut** | Where every claim sits in the lifecycle — pending → under review → approved → paid → denied |
| **Year-over-Year trend** | Current year claim volume (navy bars) vs prior year (gray) by month |
| **Open High-Value Claims table** | Claims over $250,000 still unresolved — the company's biggest financial exposure right now |

---

### 📋 Claims Operations
Day-to-day claims management view for operations managers.

| What you see | What it tells you |
|---|---|
| **Open Claims Aging by Policy Type** | Stacked bars showing On Track / At Risk / Overdue — colored by policy type so you see *what kind* of claims are delayed |
| **Examiner Workload by Policy Type** | Which examiners have which product types in their queue — identifies overloaded staff |
| **Claims by Cause of Death** | Bar height = total claims. Color = denial rate zone (🟢 low / 🔴 high). Which causes get denied most often? |
| **Open Claims Detail table** | Every open claim with days open, aging flag, and examiner |
| **Examiner Decision Consistency** | Scatter plot: approval rate vs. avg days. Team average lines flag examiners who are inconsistent or slow |

---

### 💰 Financial Analysis
Profitability and exposure — for finance and actuarial teams.

| What you see | What it tells you |
|---|---|
| **Total Paid Out by Product** | Which products have generated the most claims payments, in actual dollar amounts |
| **Loss Ratio by Product** | 🟢/🟡/🔴 colored bars showing claims paid ÷ premiums collected per product. Dashed line = industry benchmark (0.70). |
| **Cumulative Payouts Over Time** | Running total of all claims disbursements since 2018 |
| **Unit Economics by Product** | Green = avg annual premium. Red = avg claim when filed. The gap shows which products have the best revenue relationship. |
| **Denial Analysis** | Overall denial rate, denied dollar value, and reasons table |

---

### 👥 Customer Segments
Actuarial and pricing intelligence — which customers are most profitable?

| What you see | What it tells you |
|---|---|
| **Avg Claim vs Avg Premium by Age Band** | Older policyholders typically carry higher-value coverage — and generate larger claims. Shows the revenue relationship per age group. |
| **Premium vs Claim Exposure by Tenure** | Long-term customers: are they generating more premiums than claims? |
| **Age × Tenure Profitability Matrix** | Each cell = Loss Ratio for that customer segment. 🟢 Green = profitable. 🔴 Red = losing money. Immediately shows which segments need pricing review. |

---

### 🏅 Agent Performance
Distribution management — who is building the best book of business?

| What you see | What it tells you |
|---|---|
| **Premium Revenue by Agent — by Product** | Stacked bars show each agent's total revenue and what they're selling (Term Life, Whole Life, Universal Life, Variable Life) |
| **Policies Written vs Claims Filed** | Bubble size = premium revenue. Color = dominant claim type. Identifies high-volume agents and their claims exposure. |
| **Agent Portfolio Mix** | Which products does each agent specialize in? Agents with more permanent products deliver higher long-term value. |
| **Revenue Efficiency** | Annual premium per policy written — who is selling higher-value coverage? |

---

### ⚖️ SLA & Compliance
Regulatory tracking — the page a compliance officer opens every morning.

| What you see | What it tells you |
|---|---|
| **5 SLA KPI cards** | Decision SLA compliance %, claims within 45-day rule, acknowledge breaches, at-risk claims, pending reserve |
| **Open Claims by SLA Status and Product** | Which products are overdue, at risk, or on track. Tells you *what kind* of claims are in trouble. |
| **Decision Time Distribution** | How many claims were decided in 0–10 days, 11–20, 21–30 (green), 31–45 (amber), 46+ (red). Count and % on each bar. |
| **Urgent Claims table** | Every claim past or approaching the 45-day SLA deadline — with color-coded days open |
| **Pending Reserve by Product** | Donut showing reserve allocation by product type + table with exact dollar figures |

---

## 🗄️ How to Deploy (Streamlit Community Cloud — Free)

Anyone with a GitHub account can deploy this for free in about 3 minutes.

### Step 1 — Go to Streamlit Cloud
Visit **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

### Step 2 — Create a New App
Click **"Create app"** and fill in:

| Field | Value |
|---|---|
| **Repository** | `L2LML/professional-portfolio` |
| **Branch** | `main` |
| **Main file path** | `insurance-dashboard/app.py` |
| **App URL** | Choose a custom name (e.g. `lisa-insurance-dashboard`) |

### Step 3 — Deploy
Click **"Deploy!"** — Streamlit Cloud installs dependencies automatically from `requirements.txt` and launches the app. Takes about 2 minutes.

Your dashboard will be live at:
```
https://lisa-insurance-dashboard.streamlit.app
```

Share that URL with anyone — no login, no install, opens instantly in any browser.

---

## 🔗 How This Fits the Portfolio

This dashboard is the **third tier** of a complete data engineering stack:

```
1. 🗄️  Life Insurance Claims Database
        PostgreSQL · 9 tables · 24 SQL queries · window functions
        Triggers · stored procedures · age/tenure segmentation
        → ../life-insurance-claims-db/

2. ☁️  Insurance Claims Cloud Migration Pipeline
        Python ETL: Extract → Transform → Validate → Load
        pandas · SQLAlchemy · pyarrow · boto3 (AWS S3)
        → ../insurance-cloud-migration/

3. 📊  THIS DASHBOARD
        Streamlit · Plotly · 5 pages · central color system
        Loss ratio · SLA compliance · trend arrows · sample data
```

The same data that was modeled in SQL, validated in the ETL pipeline, and loaded to S3 as Parquet is what powers this dashboard.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `streamlit` | Multi-page dashboard framework |
| `plotly` | Interactive charts — bar, scatter, pie, heatmap, line |
| `pandas` | Data loading, filtering, aggregation |
| `pyarrow` | Parquet file reading |
| `matplotlib` | Required for pandas Styler gradient formatting |

---

## Skills Demonstrated

| Category | Detail |
|---|---|
| **Dashboard Design** | 5-page multi-view app, central color system, consistent semantic colors |
| **Data Visualization** | 20+ chart types — each answers a specific business question |
| **Insurance Domain** | Loss ratio, SLA compliance, claims adjudication, reserve estimation |
| **Python** | Modular page architecture, shared color/data modules, `@st.cache_data` |
| **Business Intelligence** | KPI trend arrows, YoY comparison, actionable alerts |
| **UX** | Plain-English explanations on every metric — readable by non-insurance audiences |

---

*Lisa Lewandowski · [GitHub: L2LML](https://github.com/L2LML) · [Full Portfolio](https://github.com/L2LML/professional-portfolio)*
