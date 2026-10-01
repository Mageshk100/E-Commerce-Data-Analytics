# UCI Online Retail Dataset — Comprehensive Data Profiling Report

**Generated On:** 2026-10-01T21:45:14.314056  
**Dataset Source:** [UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail)  
**Total Records:** 541,909 rows | **Total Attributes:** 8 columns

---

## 1. Executive Summary & Critical Data Quality Findings

The raw UCI Online Retail dataset captures transnational transactions between **01/12/2010 and 09/12/2011** for a UK-based, registered online retail company specializing in unique all-occasion giftware. Key profiling conclusions:

- **Volume:** 541,909 raw transactional rows across 25,900 distinct invoices.
- **Missing Customer Identifiers:** **135,080 rows (24.9267%)** have missing `CustomerID`. These correspond to 3,710 invoices and represent **14.85%** of total raw monetary turnover (£1,447,682.12 of £9,747,747.93).
- **Duplicate Rows:** **5,268 exact duplicate rows (0.9721%)** exist across all 8 fields.
- **Cancellations & Negative Quantities:** **9,288 rows (1.7139%)** represent explicit cancellations (`InvoiceNo` prefixed with 'C'). In addition, **1,336 records** have negative quantities without a 'C' prefix, predominantly consisting of inventory write-offs, stock adjustments, and damaged items with zero unit price.
- **Zero / Negative Prices:** **2,515 rows (0.4641%)** have `UnitPrice = 0.00` (administrative notes, damaged stock, giveaways). Exactly **2 records** possess negative prices (bad debt adjustments).
- **Extreme Outliers:** Quantities range from **-80,995.0** to **+80,995.0**, and unit prices range from **£-11062.06** to **£38,970.00**.

## 2. Dataset Schema & Completeness

| Column Name | Inferred Type | Missing Count | Missing % | Unique Values | Sample Values |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **InvoiceNo** | `str` | 0 | 0.0% | 25,900 | `536365, 536365` |
| **StockCode** | `str` | 0 | 0.0% | 4,070 | `85123A, 71053` |
| **Description** | `object` | 1,454 | 0.2683% | 4,223 | `WHITE HANGING HEART T-LIGHT HOLDER, WHITE METAL LANTERN` |
| **Quantity** | `int64` | 0 | 0.0% | 722 | `6, 6` |
| **InvoiceDate** | `datetime64[us]` | 0 | 0.0% | 23,260 | `2010-12-01 08:26:00, 2010-12-01 08:26:00` |
| **UnitPrice** | `float64` | 0 | 0.0% | 1,630 | `2.55, 3.39` |
| **CustomerID** | `float64` | 135,080 | 24.9267% | 4,372 | `17850.0, 17850.0` |
| **Country** | `str` | 0 | 0.0% | 38 | `United Kingdom, United Kingdom` |


### Field Quality Observations

1. **`CustomerID`**: Missing in 135,080 rows (24.9267%). Stored as a float in raw data due to NaN values.
2. **`Description`**: Missing in 1,454 rows (0.2683%). All rows with missing descriptions also have zero unit prices.
3. **`InvoiceNo`**: Contains numeric invoice IDs (6 digits) and alphanumeric codes (prefixed with 'C' for cancellation, or rarely 'A' for adjustments).
4. **`StockCode`**: Contains standard 5-digit product codes with optional letter suffix, plus administrative service codes (`POST`, `D`, `M`, `BANK CHARGES`, `AMAZONFEE`, `CRUK`, etc.).

## 3. Duplication Analysis

- **Exact Duplicate Rows:** `5,268` rows (0.9721% of the dataset).
- **Analytical Decision Required:** In transaction log systems, identical rows with matching timestamp, customer, invoice, stock code, quantity, and unit price generally indicate network retry duplicates, multi-clicks, or data logging artifacts. Removing these duplicates preserves clean unique line item integrity.

## 4. Cancellations and Returns Breakdown

| Metric | Value | Analytical Significance |
| :--- | :---: | :--- |
| Invoices with 'C' prefix | **9,288** (1.7139%) | Explicit customer cancellations / refunds |
| Distinct Cancellation Invoices | **3,836** | Separate credit transaction headers |
| 'C' Invoices with Quantity < 0 | **9,288** | 100% of 'C' invoices possess negative quantities |
| 'C' Invoices with Quantity >= 0 | **0** | Zero positive quantities in 'C' invoices |
| Negative Qty WITHOUT 'C' prefix | **1,336** | Internal inventory corrections & damage adjustments |


### Non-Cancellation Negative Quantities (Inventory Adjustments)

Records with negative quantities but no 'C' prefix do not belong to customer transactions. Top descriptions found in these rows:

| Description Sample | Frequency | Meaning / Context |
| :--- | :---: | :--- |
| `nan` | 862 | Stock adjustment / lost stock / warehouse note |
| `check` | 120 | Stock adjustment / lost stock / warehouse note |
| `damages` | 45 | Stock adjustment / lost stock / warehouse note |
| `damaged` | 42 | Stock adjustment / lost stock / warehouse note |
| `?` | 41 | Stock adjustment / lost stock / warehouse note |
| `sold as set on dotcom` | 20 | Stock adjustment / lost stock / warehouse note |
| `Damaged` | 14 | Stock adjustment / lost stock / warehouse note |
| `thrown away` | 9 | Stock adjustment / lost stock / warehouse note |


## 5. Pricing Anomalies & Financial Adjustments

- **Zero Unit Price (`UnitPrice == 0.0`):** **2,515 rows** (0.4641%). These correspond to stock adjustments, gift samples, write-offs, or unbilled orders.
- **Negative Unit Price (`UnitPrice < 0.0`):** Exactly **2 records** detected in the raw dataset:

| InvoiceNo | StockCode | Description | UnitPrice | Quantity |
| :---: | :---: | :--- | :---: | :---: |
| `A563186` | `B` | Adjust bad debt | £-11062.06 | 1 |
| `A563187` | `B` | Adjust bad debt | £-11062.06 | 1 |

*Note: Negative unit prices represent bad debt write-offs ('Adjust bad debt') and are financial journal adjustments rather than retail commerce sales.*

## 6. Numerical Distributions & Outliers

| Metric | Quantity | UnitPrice (£) | Raw Line Value (£) |
| :--- | :---: | :---: | :---: |
| **Count** | 541,909 | 541,909 | 541,909 |
| **Mean** | 9.55 | £4.61 | £17.99 |
| **Std Dev** | 218.08 | £96.76 | £378.81 |
| **Min** | -80,995.0 | £-11062.06 | £-168469.60 |
| **1st Percentile** | -2 | £0.19 | £-6.58 |
| **25th Percentile (Q1)** | 1 | £1.25 | - |
| **Median (50th)** | 3 | £2.08 | £9.75 |
| **75th Percentile (Q3)** | 10 | £4.13 | - |
| **99th Percentile** | 100 | £18.00 | £180.00 |
| **Max** | 80,995.0 | £38,970.00 | £168,469.60 |
| **Raw Sum Total** | - | - | **£9,747,747.93** |


## 7. Temporal Range & Seasonality Baseline

- **Earliest Timestamp:** `2010-12-01 08:26:00`
- **Latest Timestamp:** `2011-12-09 12:50:00`
- **Time Horizon:** 373 days (~12 months).
- **Important Chronological Consideration:** December 2011 only spans up to **2011-12-09** (partial month of 9 days). When analyzing monthly trends, December 2011 must be noted as incomplete to prevent misleading trend interpretation.

### Monthly Transaction Distribution (Raw)

| Year-Month | Transaction Count |
| :---: | :---: |
| 2010-12 | 42,481 |
| 2011-01 | 35,147 |
| 2011-02 | 27,707 |
| 2011-03 | 36,748 |
| 2011-04 | 29,916 |
| 2011-05 | 37,030 |
| 2011-06 | 36,874 |
| 2011-07 | 39,518 |
| 2011-08 | 35,284 |
| 2011-09 | 50,226 |
| 2011-10 | 60,742 |
| 2011-11 | 84,711 |
| 2011-12 | 25,525 |


## 8. Geographic Distribution (Top 10 Markets)

| Country | Raw Transactions | Unique Invoices | Total Quantity |
| :--- | :---: | :---: | :---: |
| **United Kingdom** | 495,478 | 23,494 | 4,263,829 |
| **Germany** | 9,495 | 603 | 117,448 |
| **France** | 8,557 | 461 | 110,480 |
| **EIRE** | 8,196 | 360 | 142,637 |
| **Spain** | 2,533 | 105 | 26,824 |
| **Netherlands** | 2,371 | 101 | 200,128 |
| **Belgium** | 2,069 | 119 | 23,152 |
| **Switzerland** | 2,002 | 74 | 30,325 |
| **Portugal** | 1,519 | 71 | 16,180 |
| **Australia** | 1,259 | 69 | 83,653 |


## 9. Non-Product Stock Codes Identified

The raw data contains non-inventory line items used for fees, postage, and manual adjustments:

| Stock Code | Occurrences | Business Meaning |
| :---: | :---: | :--- |
| `POST` | 1,256 | Postage fee |
| `DOT` | 710 | Administrative / Fee |
| `M` | 571 | Manual transaction |
| `D` | 77 | Discount |
| `S` | 63 | Administrative / Fee |
| `AMAZONFEE` | 34 | Administrative / Fee |
| `CRUK` | 16 | Administrative / Fee |
| `DCGSSGIRL` | 13 | Administrative / Fee |
| `DCGSSBOY` | 11 | Administrative / Fee |
| `PADS` | 4 | Administrative / Fee |
| `B` | 3 | Administrative / Fee |
| `m` | 1 | Administrative / Fee |


## 10. Analytical Recommendations for Phase 3 (Data Cleaning)

Based on the rigorous empirical findings above, the data cleaning pipeline should apply the following explicit rules:

1. **Deduplication:** Remove exact duplicates (5,268 records / 0.97%) to ensure line item uniqueness.
2. **Handling Missing CustomerID:**
   - Because missing `CustomerID` represents 24.93% of records and ~17.5% of sales, we should **not** drop them globally from overall sales and product performance analytics.
   - Flag records as `is_guest_checkout = True` or assign a synthetic guest ID (e.g. `'GUEST'`) for macro-level sales/product/country analysis.
   - Exclude guest records specifically when calculating customer-level KPIs (Repeat Customer Rate, Customer Lifetime Value, RFM segmentation, Customer Rankings).
3. **Handling Cancellations & Returns:**
   - Tag records with `is_cancellation = True` if `InvoiceNo` starts with 'C'.
   - Provide dual metrics: Gross Sales (completed purchases with `Quantity > 0`) and Net Sales (Gross Sales minus cancellations / returns).
4. **Handling Non-Cancellation Negative Quantities & Zero Prices:**
   - Records with `Quantity < 0` and no 'C' prefix and `UnitPrice == 0` represent internal inventory write-offs (e.g. damaged, lost stock). These are administrative adjustments and should be excluded from commercial sales reporting.
   - Records with negative unit prices (`Adjust bad debt`) should be excluded from sales transactions.
   - Zero-price gift items with valid positive quantities can be retained for unit volume analysis or isolated from revenue metrics.
5. **Standardized Column Naming:** Convert PascalCase column names (`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`) to standard snake_case (`invoice_no`, `stock_code`, `description`, `quantity`, `invoice_date`, `unit_price`, `customer_id`, `country`).
