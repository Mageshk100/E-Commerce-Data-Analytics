# E-Commerce Sales Analytics Platform & Interactive Dashboard

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0-150458.svg)](https://pandas.pydata.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-red.svg)](https://www.sqlalchemy.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-7.1-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-15%20Passed-brightgreen.svg)]()
[![Reconciliation](https://img.shields.io/badge/SQL%20vs%20Python-100%25%20Reconciled-success.svg)]()

An end-to-end, portfolio-ready business intelligence and analytics solution transforming 540,000+ raw transnational e-commerce transaction records from the **UCI Online Retail** repository into audit-ready financial insights, advanced SQL data models, and an interactive executive Streamlit dashboard.

---

## 📌 Executive Summary & Business Context

A UK-based registered online giftware retailer specializing in unique, all-occasion gift items primarily sells wholesale to international and domestic commercial clients. Operating without a unified analytics layer, executive leadership faced critical data blind spots:
1. **Unclear Revenue vs. Refund Dynamics:** High cancellation volumes distorted top-line sales figures.
2. **Missing Customer Identity Leakage:** 24.9% of transactions lacked customer identifiers; standard naive analytics pipelines dropped these records, inadvertently erasing **~£1.47M (15.1%)** in real commercial turnover.
3. **Operational Rhythm & Stock Imbalances:** The catalog suffered from severe inventory concentration, with no visibility into hourly order surges or day-of-week operations.

This project delivers an enterprise-grade analytics pipeline that preserves raw data integrity, establishes dual-engine SQL/Python parity, calculates precise business KPIs, and surfaces strategic insights through a 5-page interactive dashboard.

---

## 🏗️ System Architecture & Technology Stack

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION & AUDIT                          │
│   UCI Online Retail Repository (Excel / Automated Python Downloader)    │
│              541,909 raw records | 8 original attributes               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DATA PROFILING & QUALITY AUDIT                     │
│    src/profiling.py ──▶ reports/data_profiling_report.md & .json       │
│  - Duplication audit (5,268 exact duplicates identified)               │
│  - Anomaly detection: 2 bad debt adjustments, 1,336 inventory notes    │
│  - 9,288 cancellations & 135,080 missing customer records audited      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   PRODUCTION CLEANING & NORMALIZATION                  │
│    src/cleaning.py ──▶ data/processed/online_retail_cleaned.csv        │
│  - Waterfall attrition tracking: 541,909 ──▶ 534,129 clean rows (98.6%)│
│  - Guest Checkout Strategy: Flagged via is_guest_checkout (No data loss│
│  - Customer Dimension: 1-to-1 customer aggregation (4,371 accounts)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
┌──────────────────────────────────┐ ┌───────────────────────────────────┐
│     SQL ANALYTICS & WAREHOUSE    │ │      EXPLORATORY DATA ENGINE      │
│  src/database.py & sql/*.sql     │ │   src/eda.py & reports/figures/   │
│  - MySQL 8.0+ / SQLite 3.50+ OLAP│ │  - Monthly, daily & hourly trends │
│  - CTEs, Window Functions (LAG,  │ │  - Pareto catalog curve (80/20)   │
│    DENSE_RANK, NTILE, SUM OVER)  │ │  - Geographic export market analysis│
│  - 100% Dual-Engine Reconciliation│ │  - Customer loyalty segmentation  │
└─────────────────┬────────────────┘ └─────────────────┬─────────────────┘
                  │                                    │
                  └─────────────────┬──────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               INTERACTIVE STREAMLIT ANALYTICS DASHBOARD                │
│       app.py (Executive, Products, Geography, Customers, Audit)        │
└────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Data Engineering & Manipulation:** Python 3.14, Pandas 3.0, NumPy 2.4
- **Relational Storage & Modeling:** MySQL 8.0+ / SQLite 3.50+ (OLAP indexing)
- **Database Connectivity & ORM:** SQLAlchemy 2.1, PyMySQL 1.2, Cryptography
- **Visualizations & Frontend:** Streamlit 1.64, Plotly 7.1
- **Quality Assurance & CI/CD:** Pytest 9.1 (15 unit & integration tests)

---

## 📁 Repository Structure

```text
sales-dashboard/
├── data/
│   ├── raw/
│   │   ├── Online Retail.xlsx          # Raw UCI dataset (23.7 MB, 541,909 rows)
│   │   └── online_retail_raw.csv       # Fast cached raw CSV
│   └── processed/
│       ├── online_retail_cleaned.csv   # Cleaned transactional fact data (534,129 rows)
│       ├── customer_summary.csv        # 1-to-1 Customer dimension table (4,371 accounts)
│       └── ecommerce.db                # Indexed SQLite OLAP analytical database
├── src/
│   ├── __init__.py
│   ├── download_data.py                # Reproducible dataset downloader
│   ├── profiling.py                    # Data profiling & anomaly audit script
│   ├── cleaning.py                     # Waterfall cleaning & normalization pipeline
│   ├── eda.py                          # Exploratory analysis & Plotly figure generator
│   ├── database.py                     # Database manager, ETL & reconciliation engine
│   └── metrics.py                      # Multi-dimensional business KPI engine
├── sql/
│   ├── schema.sql                      # DDL schema definitions (fact & dim tables + indexes)
│   ├── queries.sql                     # Production analytical SQL queries (CTEs, Window Funcs)
│   └── validation.sql                  # Dual-engine reconciliation SQL scripts
├── reports/
│   ├── figures/                        # Standalone interactive Plotly HTML visualizations
│   ├── data_profiling_report.md        # Comprehensive pre-cleaning quality audit
│   ├── data_profiling_summary.json     # Machine-readable profiling metrics
│   ├── data_cleaning_audit.md          # Row-by-row cleaning waterfall report
│   ├── exploratory_data_analysis.md    # Detailed empirical findings report
│   └── sql_validation_report.md        # Python vs. SQL parity verification matrix
├── tests/
│   ├── __init__.py
│   ├── test_profiling.py               # Profiling module tests
│   ├── test_cleaning.py                # Data cleaning pipeline tests
│   ├── test_eda.py                     # Statistical and aggregation tests
│   ├── test_database.py                # Database connection & query tests
│   ├── test_metrics.py                 # Business KPI calculation tests
│   └── test_validation_e2e.py          # End-to-end mathematical reconciliation tests
├── .gitignore
├── requirements.txt
├── app.py                              # 5-Page interactive Streamlit Dashboard
└── README.md                           # Project documentation
```

---

## 🧹 Data Cleaning Methodology & Waterfall Audit

The raw dataset contains **541,909 transactions**. Rather than performing undocumented or silent deletions, every transformation step is tracked in an attrition waterfall:

| Step | Transformation Stage | Description | Rows Removed | Rows Remaining | Impact Rationale |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1.** | **Raw Ingestion** | Full UCI Online Retail transactional log | 0 | **541,909** | Baseline source data |
| **2.** | **Exact Deduplication** | Identical values across all 8 fields | -5,268 | **536,641** | Eliminates multi-click retries & logging artifacts |
| **3.** | **Bad Debt Adjustments** | Negative unit prices (`Adjust bad debt`) | -2 | **536,639** | Accounting journal write-offs, not retail commerce |
| **4.** | **Inventory Adjustments** | Negative quantities without `'C'` prefix | -1,336 | **535,303** | Warehouse damaged/lost stock notes (`UnitPrice = 0`) |
| **5.** | **Zero Unit Price Filter** | Promotional giveaways / administrative rows | -1,174 | **534,129** | Zero commercial revenue value |

### 🔑 Critical Analytical Strategy: Guest Checkouts
- **The Problem:** 132,565 rows (24.8% of commercial transactions) have missing `CustomerID`.
- **Naive Trap:** Many pipelines drop missing `CustomerID` rows, erasing **£1,469,611.65 (15.1%)** of actual revenue.
- **Analytical Solution:** Flag rows with `is_guest_checkout = True` and `customer_identifier = 'GUEST'`.
  - All commercial revenue, country, and product analytics include guest checkouts.
  - Customer cohort, retention, and frequency metrics are isolated to the **4,371 registered customer accounts**.

---

## 📊 Business Metrics & KPI Definitions

> [!IMPORTANT]
> **Revenue vs. Profit Distinction:** The UCI dataset records retail transaction values but **does not provide Product Cost of Goods Sold (COGS)**. In strict accordance with professional analytical integrity, turnover is labeled **Net Commercial Revenue** and is never falsely represented as Gross Profit or Net Margin.

| Business Metric | Mathematical Formulation | Cleaned Value (£ / Count) | Business Interpretation |
| :--- | :--- | :---: | :--- |
| **Gross Commercial Sales** | $\sum (\text{Quantity} \times \text{UnitPrice})$ for $\text{Qty} > 0$ | **£10,642,110.80** | Total value of completed outbound orders |
| **Returns & Cancellations** | $\sum |\text{Quantity} \times \text{UnitPrice}|$ for $\text{InvoiceNo} \sim \text{'C'}^*$ | **-£893,979.73** | Value of refunds and cancelled merchandise |
| **Net Commercial Revenue** | $\text{Gross Sales} - \text{Returns}$ | **£9,748,131.07** | Realized net turnover |
| **Completed Orders** | $\text{CountDistinct}(\text{InvoiceNo})$ where $\text{Qty} > 0$ | **19,960** | Unique outbound shipments |
| **Cancelled Orders** | $\text{CountDistinct}(\text{InvoiceNo})$ where $\text{InvoiceNo} \sim \text{'C'}^*$ | **3,836** | Unique credit note transactions |
| **Average Order Value (AOV)**| $\text{Net Revenue} / \text{Completed Orders}$ | **£488.38** | Average commercial basket size |
| **Repeat Customer Rate** | $\text{Repeat Customers} / \text{Total Registered Customers}$ | **65.09%** | 2,845 of 4,371 registered buyers ordered $\ge 2$ times |
| **Cancellation Rate** | $\text{Cancelled Orders} / \text{Total Invoices}$ | **16.12%** (Orders) / **1.73%** (Lines) | Order-level return frequency |

---

## 🗄️ SQL Analytics Suite & Dual-Engine Reconciliation

Cleaned data is loaded into a relational OLAP schema (`fact_transactions` and `dim_customers`). Analytical queries in [sql/queries.sql](file:///c:/Users/91636/OneDrive/Desktop/sales%20dashboard/sql/queries.sql) implement:
- **Window Functions:** `LAG()` for MoM revenue delta, `DENSE_RANK()` for product and customer rankings, `SUM() OVER ()` for running cumulative Pareto shares, and `NTILE(5)` for customer quintile segmentation.
- **Common Table Expressions (CTEs):** Multi-stage aggregation pipelines isolating purchases from refunds.

### Dual-Engine Reconciliation Matrix (SQL vs. Python)
All KPIs were independently computed via both the Python vectorized engine and the SQL relational engine to guarantee **zero calculation drift**:

| Metric | Python Engine | SQL Relational Engine | Variance | Audit Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Commercial Rows** | 534,129 | 534,129 | `0` | ✅ PASS |
| **Gross Sales (£)** | £10,642,110.80 | £10,642,110.80 | `£0.00` | ✅ PASS |
| **Refunds & Cancellations (£)** | -£893,979.73 | -£893,979.73 | `£0.00` | ✅ PASS |
| **Net Commercial Revenue (£)** | £9,748,131.07 | £9,748,131.07 | `£0.00` | ✅ PASS |
| **Completed Order Count** | 19,960 | 19,960 | `0` | ✅ PASS |
| **Registered Customers** | 4,371 | 4,371 | `0` | ✅ PASS |
| **Repeat Customer Rate (%)** | 65.09% | 65.09% | `0.00%` | ✅ PASS |

---

## 📈 Key Analytical Insights & Strategic Findings

1. **Fourth-Quarter Holiday Acceleration:**
   - Monthly turnover scaled from £558k in Jan 2011 to a peak of **£1.46M in November 2011 (+161% expansion)**, reflecting intense B2B wholesale gift procurement ahead of the Christmas season.
2. **6-Day Trading Rhythm & Saturday Zero Operations:**
   - Exactly **0 transactions** occur on Saturdays throughout the entire 373-day recording window, confirming the warehouse adheres to a strict 6-day dispatch schedule. Thursdays generate the highest volume (£2.20M).
   - **Intraday Concentration:** Over **81.4% of orders** are placed between **10:00 and 15:00 UTC**, peaking at 12:00 PM.
3. **Pareto Catalog Imbalance (80/20 Rule):**
   - The top **21.5% of product SKUs** generate **80% of total catalog net revenue**.
   - Top revenue driver: `REGENCY CAKESTAND 3 TIER` (£164,459 across 13,851 units).
4. **Export Wholesale Dynamics (High AOV Markets):**
   - While the **UK generates 84.0% of Net Revenue (£8.19M)**, international markets exhibit dramatically larger basket sizes:
   - **Netherlands:** £3,028 AOV (£284.6k net revenue across 94 bulk orders).
   - **Australia:** £2,404 AOV (£137.0k net revenue across 57 bulk orders).
5. **Customer Concentration & Loyalty:**
   - **65.09% of registered customers** are repeat buyers.
   - Repeat buyers generate **93.8% of registered revenue** (£7.76M).
   - **Extreme Top-Tier Concentration:** The top 1% of customers (43 accounts) drive **29.8% of registered spend**, and the top 5% drive **48.6% of spend**.

---

## 💻 Streamlit Interactive Dashboard

The Streamlit web application ([app.py](file:///c:/Users/91636/OneDrive/Desktop/sales%20dashboard/app.py)) provides a modern, responsive dashboard with 5 specialized analytical views:

1. **Executive Overview:** High-level KPI cards, dual-axis monthly revenue and order volume trends, day-of-week and hourly trading heatmaps.
2. **Product Analysis:** Interactive Pareto curve, top 15 revenue products, catalog concentration metrics, and a searchable SKU performance table.
3. **Geographic Analysis:** Domestic vs. export split, international market bar charts with AOV color grading, side-by-side country comparison tool.
4. **Customer Analytics:** Order frequency loyalty segmentation (1, 2, 3-5, 6-10, 11-20, 21-50, 50+ orders), customer concentration tiers, and VIP wholesaler leaderboard.
5. **Data Quality & Audit:** Interactive cleaning waterfall table, guest checkout financial breakdown, and live SQL vs. Python reconciliation badges.

**Global Filters:** Dynamic date range picker, country multi-select, customer type selector (All, Registered Only, Guest Only), and one-click filtered CSV export.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites & Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd "sales dashboard"

# Install required dependencies
pip install -r requirements.txt
```

### 2. Download Raw Dataset
```bash
python src/download_data.py
```

### 3. Run Data Profiling Audit
```bash
python src/profiling.py
```

### 4. Execute Data Cleaning Pipeline
```bash
python src/cleaning.py
```

### 5. Run Exploratory Data Analysis & Visualization Generation
```bash
python src/eda.py
```

### 6. Initialize Database & Run SQL Validation
```bash
python src/database.py
```

### 7. Run Full Automated Test Suite (15 Tests)
```bash
pytest tests/ -v
```

### 8. Launch Streamlit Interactive Dashboard
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing Suite (Phase 8)

The test suite covers data ingestion, profiling, cleaning transformations, exploratory mathematics, database connectivity, and end-to-end reconciliation:

```text
tests/test_cleaning.py::test_cleaning_pipeline_filtering PASSED          [  6%]
tests/test_database.py::test_database_connectivity PASSED                [ 13%]
tests/test_database.py::test_sql_reconciliation PASSED                   [ 20%]
tests/test_eda.py::test_monthly_trends_math PASSED                       [ 26%]
tests/test_eda.py::test_seasonality_aggregations PASSED                  [ 33%]
tests/test_eda.py::test_geography_math PASSED                            [ 40%]
tests/test_eda.py::test_customer_dynamics_math PASSED                    [ 46%]
tests/test_metrics.py::test_calculate_business_kpis PASSED               [ 53%]
tests/test_metrics.py::test_empty_dataframe_handling PASSED              [ 60%]
tests/test_metrics.py::test_filter_transactions PASSED                   [ 66%]
tests/test_profiling.py::test_profiling_logic PASSED                     [ 73%]
tests/test_profiling.py::test_report_generation PASSED                   [ 80%]
tests/test_validation_e2e.py::test_production_cleaned_dataset_integrity PASSED [ 86%]
tests/test_validation_e2e.py::test_customer_summary_dataset_integrity PASSED [ 93%]
tests/test_validation_e2e.py::test_sql_engine_database_integrity PASSED  [100%]

============================= 15 passed in 10.37s =============================
```

---

## ⚠️ Analytical Limitations & Future Enhancements

### Limitations
1. **Absence of Unit Cost (COGS):** As product acquisition costs are not present in the UCI dataset, gross margin and net operating profit cannot be determined without introducing fabricated data.
2. **Truncated December 2011 Window:** The dataset concludes on December 9, 2011 (9 days). Trend visualizations explicitly annotate December 2011 as a partial month to avoid false signals of business contraction.

### Future Improvements
1. **Predictive Churn Modeling:** Train a machine learning classifier (e.g., XGBoost) on customer recency, frequency, and monetary tenure to flag churn risk.
2. **Dynamic RFM Cohort Heatmaps:** Expand customer analytics with month-by-month retention grids.
3. **Automated Data Drift Monitoring:** Integrate Great Expectations for continuous schema contract enforcement upon fresh transaction uploads.
