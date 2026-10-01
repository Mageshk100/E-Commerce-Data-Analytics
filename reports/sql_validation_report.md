# SQL vs. Python Analytics — Dual-Engine Reconciliation Report

**Execution Timestamp:** 2026-10-01T23:13:48.663481  
**Database Engine Tested:** `SQLite`  
**Status:** ✅ **ALL TESTS PASSED (100% RECONCILED)**

---

## 1. Methodology & Purpose

To ensure complete analytical credibility, all business KPIs were independently computed via two isolated pathways:

1. **Python / Pandas Dataframe Engine**: vectorized transformations and groupby aggregations.

2. **SQL Relational Engine**: Common Table Expressions (CTEs), window functions, and indexed SQL aggregations.

Any variance between the two engines indicates calculation drift, silent rounding error, or inconsistent handling of cancellations or guest accounts.

## 2. Reconciliation Matrix

| Metric | Python / Pandas Output | SQL Engine Output | Variance | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Commercial Rows** | 534,129 | 534,129 | `0` | ✅ PASS |
| **Gross Revenue (£)** | £10,642,110.80 | £10,642,110.80 | `0.0` | ✅ PASS |
| **Refunds & Cancellations (£)** | -£893,979.73 | -£893,979.73 | `0.0` | ✅ PASS |
| **Net Revenue (£)** | £9,748,131.07 | £9,748,131.07 | `0.0` | ✅ PASS |
| **Completed Order Count** | 19,960 | 19,960 | `0` | ✅ PASS |
| **Registered Customers** | 4,371 | 4,371 | `0` | ✅ PASS |
| **Repeat Customer Rate (%)** | 65.09% | 65.09% | `0.0` | ✅ PASS |


## 3. SQL Query Features Validated

- **Window Functions**: `LAG()` for MoM revenue delta, `DENSE_RANK()` for product and customer rankings, `SUM() OVER ()` for cumulative Pareto distribution.
- **CTEs**: Multi-stage CTE pipelines for customer quintiles and monthly order metrics.
- **Cancellations Logic**: Filtered via `is_cancellation = 0` for purchases and `is_cancellation = 1` for refunds across both engines.
- **Zero Silent Drift**: Confirmed exact decimal parity on all commercial turnover (£9,748,131.07).
