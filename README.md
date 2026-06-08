# Professional Portfolio — Lisa Lewandowski

A collection of professional case studies, software development projects, and applied work demonstrating skills in process improvement, full-stack development, data analysis, and project management.

---

## 📁 Projects

### 📊 Lean Six Sigma Black Belt Case Study
**File:** [`LSSBB_Portfolio_Lewandowski.pptx`](./LSSBB_Portfolio_Lewandowski.pptx)
**Folder:** [`/lssbb-portfolio`](./LSSBB_Portfolio_Lewandowski.pptx)

A **4-week live client engagement** completed through Siena Heights University PDC (Q2 2024). Real operational data from TriCore Reference Laboratories was collected, analyzed, and validated using full DMAIC methodology and statistical tools.

| | |
|---|---|
| **Client** | TriCore Reference Laboratories — 12 labs, ~$1.5B non-profit, Albuquerque NM |
| **Problem** | 141,708 blood draws/year vs. 188,928 potential — $5–6M Cost of Poor Quality |
| **Method** | Full DMAIC · Two-sample T-test · Minitab · C&E Matrix · FMEA · Lean Waste Analysis |
| **Results** | Mean processing time reduced 25–31% across all 3 pilot labs |
| **Impact** | **$894,600+** minimum annual revenue recovery · Sigma: 2.6 → 2.9 |
| **Skills** | Project Management · Lean Six Sigma · Statistical Analysis · Process Improvement · Change Management |

---

### 📊 Insurance Claims BI Dashboard
**Folder:** [`/insurance-dashboard`](./insurance-dashboard)

Interactive, multi-page BI dashboard for life insurance claims operations. Covers Loss Ratio, SLA compliance, examiner workload, customer segment profitability, and agent performance. Pre-built sample data included — runs in 60 seconds locally or deploy free to Streamlit Cloud.

| | |
|---|---|
| **Type** | Solo Project — Business Intelligence / Data Visualization |
| **Stack** | Python · Streamlit · Plotly · pandas · pyarrow |
| **Pages** | Executive Summary · Claims Operations · Financial Analysis · Customer Segments · Agent Performance · SLA & Compliance |
| **Key metrics** | Loss Ratio · SLA compliance · Pending reserve · YoY trend arrows · Age × Tenure profitability heatmap |
| **Live Demo** | 👉 **[lisa-insurance-claims.streamlit.app](https://lisa-insurance-claims.streamlit.app)** — opens in any browser, no install |
| **Skills** | Dashboard Design · Streamlit · Plotly · Insurance Domain · Data Storytelling · pandas |

---

### 🗄️ Life Insurance Claims Database
**Folder:** [`/life-insurance-claims-db`](./life-insurance-claims-db)

A PostgreSQL relational database modeling the full lifecycle of life insurance policies, claims, and beneficiary payments — from policy issuance through payment disbursement.

| | |
|---|---|
| **Type** | Solo Project — Database Design & SQL Analytics |
| **Stack** | PostgreSQL · SQL |
| **Schema** | 9 tables · check constraints · indexes · 4 views · ERD diagram |
| **Queries** | 21 queries — INNER/LEFT/FULL OUTER JOINs, UNION, EXCEPT, window functions, multi-step CTEs, EXPLAIN ANALYZE |
| **Triggers** | 4 triggers — audit trail, auto-timestamp, beneficiary validation, policy active check |
| **Stored Procs** | 4 PL/pgSQL functions — full claims workflow from filing through payment |
| **Domain** | Life insurance · claims adjudication · beneficiary management · risk reporting |
| **Skills** | Relational Modeling · Advanced SQL · PostgreSQL · PL/pgSQL · Insurance Domain Knowledge |

---

### ☁️ Insurance Claims Cloud Migration Pipeline
**Folder:** [`/insurance-cloud-migration`](./insurance-cloud-migration)

A Python ETL pipeline that migrates the life insurance claims database from PostgreSQL to AWS S3 as a Parquet data lake. Direct continuation of the SQL project above.

| | |
|---|---|
| **Type** | Solo Project — Data Engineering / Cloud Migration |
| **Stack** | Python · pandas · SQLAlchemy · pyarrow · boto3 · matplotlib · seaborn |
| **Pipeline** | Extract → Transform → Validate (20+ checks) → Visualize → Load |
| **Output** | Snappy-compressed Parquet · 5 audit charts · Validation JSON report |
| **Cloud** | AWS S3 data lake with versioned, partitioned keys; BigQuery + Snowflake patterns included |
| **Skills** | ETL Design · Data Quality · Parquet · AWS S3 · pandas · Data Visualization |

---

### ⚖️ Legal Exhibit PDF Builder
**Folder:** [`/legal-exhibit-pdf-builder`](./legal-exhibit-pdf-builder)

A Python automation tool that compiles evidence documents, photos, and receipts from an Excel tracker into a single paginated PDF exhibit package — cover page, exhibit headers, page numbers, and mixed media (images + PDFs). Built for administrative and legal filings.

| | |
|---|---|
| **Type** | Solo Project — Python Automation Tool |
| **Stack** | Python · ReportLab · Pillow · pillow-heif · OpenCV · openpyxl |
| **Highlight** | Excel-driven build; writes page numbers back to tracker automatically |
| **Use Cases** | Legal filings · Insurance claims · Tax appeals · Administrative hearings |
| **Skills** | Python Scripting · PDF Generation · Excel Integration · CLI Tool Design · File Automation |

---

### 📈 Virtual Stock Market
**Folder:** [`/virtual-stock-market`](./virtual-stock-market)

A real-time stock trading simulation game (Market 25) where users can buy and sell stocks using current market data within customized time intervals.

| | |
|---|---|
| **Type** | Team Capstone Project — Tech Elevator Full-Stack Development Bootcamp |
| **Stack** | Java · Spring Boot · Vue.js · PostgreSQL · REST API |
| **Method** | Agile/Scrum · Full-stack architecture · API integration |
| **Skills** | Full-Stack Development · Team Collaboration · Agile · Database Design · REST APIs |

---

### 🎮 Guess the Number
**Folder:** [`/guess-the-number`](./guess-the-number)

A command-line number guessing game built with comprehensive unit testing demonstrating test-driven development (TDD) practices.

| | |
|---|---|
| **Type** | Solo Project — Tech Elevator Module 1 |
| **Stack** | C# · .NET · xUnit |
| **Highlight** | 96% test coverage |
| **Skills** | Test-Driven Development · Object-Oriented Programming · Unit Testing |

---

### 🏠 Tax Assessor Document Skill
**Folder:** [`/tax-assessor-docs`](./tax-assessor-docs)

A Claude AI skill for scanning, organizing, and logging property tax assessment appeal documents into a structured tracker for administrative and legal filing purposes.

| | |
|---|---|
| **Type** | AI Automation · Document Processing |
| **Stack** | Claude AI · Prompt Engineering · Excel Integration |
| **Skills** | AI Tool Development · Process Automation · Document Management |

---

## 🛠 Skills Summary

### Languages
| Language | Proficiency | Used In |
|----------|-------------|---------|
| **Python** | Intermediate | Cloud migration pipeline, PDF builder, AI automation |
| **SQL** | Advanced | Life insurance claims DB — 24 queries, triggers, stored procedures |
| **Java** | Intermediate | Virtual Stock Market capstone, vending machine CLI |
| **C#** | Intermediate | Guess the Number — TDD with xUnit |
| **JavaScript / Vue.js** | Intermediate | Virtual Stock Market frontend |

---

### Python Libraries
| Library | Purpose | Project |
|---------|---------|---------|
| `pandas` | DataFrame transformation, enrichment, binning | Cloud migration pipeline |
| `numpy` | Vectorized operations, computed fields | Cloud migration pipeline |
| `sqlalchemy` | Database connection, ORM, query execution | Cloud migration pipeline |
| `psycopg2` | PostgreSQL driver | Cloud migration pipeline |
| `pyarrow` | Parquet read/write, Snappy compression | Cloud migration pipeline |
| `boto3` | AWS S3 upload, cloud data lake delivery | Cloud migration pipeline |
| `matplotlib` | Business charts, audit visualizations | Cloud migration pipeline |
| `seaborn` | Statistical visualization styling | Cloud migration pipeline |
| `reportlab` | PDF generation and layout | Legal Exhibit PDF Builder |
| `Pillow` | Image processing, format conversion | Legal Exhibit PDF Builder |
| `pillow-heif` | iPhone HEIC/HEIF photo support | Legal Exhibit PDF Builder |
| `opencv-python` | Image preprocessing | Legal Exhibit PDF Builder |
| `python-dotenv` | Secure credential management via `.env` | Cloud migration pipeline |

---

### Database & SQL
| Skill | Detail |
|-------|--------|
| **PostgreSQL** | Schema design, indexes, check constraints, comments |
| **Advanced SQL** | INNER / LEFT / FULL OUTER JOIN · UNION · EXCEPT |
| **Window Functions** | `SUM() OVER`, `RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`, `LAG()`, `PARTITION BY` |
| **CTEs** | Single-step, multi-step chained, CTE with window functions |
| **Triggers** | BEFORE/AFTER · INSERT/UPDATE · audit trail · validation |
| **Stored Procedures** | PL/pgSQL · exception handling · status transition logic |
| **Views** | Reusable reporting views for operations and analytics |

---

### Data Engineering & Cloud
| Skill | Detail |
|-------|--------|
| **ETL Pipeline Design** | Extract → Transform → Validate → Visualize → Load |
| **Parquet / pyarrow** | Columnar storage, Snappy compression, schema-aware writes |
| **AWS S3** | `boto3` upload, versioned partitioned data lake key design |
| **Data Quality Validation** | Null checks, referential integrity, business rule enforcement, JSON reports |
| **Cloud Patterns** | Google BigQuery (`pandas-gbq`), Snowflake (`snowflake-connector`) reference implementations |
| **Data Lake Architecture** | Raw → Transformed → Analytical layering |

---

### Other Technical Skills
| Category | Skills |
|----------|--------|
| **Full-Stack Development** | Java · Spring Boot · Vue.js · PostgreSQL · REST APIs · C# · .NET |
| **Testing** | TDD · xUnit · Unit Testing (96% coverage) |
| **AI & Automation** | Claude AI · Prompt Engineering · Document Processing |
| **Version Control** | Git · GitHub |

---

### Business & Domain Skills
| Category | Skills |
|----------|--------|
| **Lean Six Sigma** | DMAIC · FMEA · C&E Matrix · 5S · VSM · SWI · Gage R&R · LSSBB Certified |
| **Statistical Analysis** | Minitab · Two-Sample T-Test · Hypothesis Testing · Confidence Intervals |
| **Project Management** | Charter · Stakeholder Management · Milestone Planning · Change Management |
| **Insurance Domain** | Policy types · Claims adjudication · Beneficiary management · Contestability · Audit compliance |
| **Process Improvement** | NVA analysis · Swim lane mapping · Waste elimination · Root cause analysis |

---

*Lisa Lewandowski · [GitHub: L2LML](https://github.com/L2LML)*
