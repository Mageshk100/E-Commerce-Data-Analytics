# UCI Online Retail Dataset — Data Cleaning & Transformation Audit Report

**Execution Timestamp:** 2026-10-01T23:00:02.311434  
**Cleaned Records Generated:** 534,129 rows (98.56% of raw records)  
---

## 1. Cleaning Waterfall & Attrition Accounting

Every removal is tracked and justified below. No records were deleted silently.

| Step | Transformation Stage | Description | Rows Removed | Rows Remaining | Impact Rationale |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1. | **Raw Ingestion** | Original raw transactional records | -0 | **541,909** | Full transaction log loaded |
| 2. | **Exact Deduplication** | Removed duplicate transaction lines identical across all 8 fields | -5,268 | **536,641** | Eliminates network retry and double-click logging artifacts |
| 3. | **Bad Debt Adjustments Filter** | Filtered records with negative unit prices ('Adjust bad debt') | -2 | **536,639** | Internal accounting write-offs, not customer commercial transactions |
| 4. | **Inventory Adjustments Filter** | Filtered negative quantities without 'C' invoice prefix (damaged, lost stock, warehouse checks) | -1,336 | **535,303** | Internal warehouse write-offs; zero customer transaction value |
| 5. | **Zero Unit Price Filter** | Filtered records with UnitPrice == 0.00 (giveaways, administrative checks, unbilled items) | -1,174 | **534,129** | Non-commercial items without transaction value |


## 2. Financial Reconciliation & Integrity

| Revenue Metric | Amount (£) | Analytical Interpretation |
| :--- | :---: | :--- |
| **Gross Commercial Sales** | **£10,642,110.80** | Total value of completed customer purchases (`Quantity > 0`) |
| **Returns & Cancellations** | **-£893,979.73** | Total value of refunded/cancelled transactions (`is_cancellation = True`) |
| **Net Commercial Revenue** | **£9,748,131.07** | Realized net retail revenue (£10,642,110.80 - £893,979.73) |


## 3. Customer Identification Strategy (Guest Checkouts)

- **Guest Checkout Transactions:** **132,565 rows (24.82%)**
- **Guest Revenue Contribution:** **£1,469,611.65 (15.08%)**
- **Methodology Decision:**
  - Instead of discarding missing customer IDs (which would improperly erase 15.6% of real retail revenue), we created explicit segmentation flags (`is_guest_checkout` and `customer_identifier = 'GUEST'`).
  - Macro sales, revenue, geographical, and product analytics include all commercial orders.
  - Customer behavioral metrics (Repeat Rate: **65.09%**, Frequency, CLV) are calculated strictly on the **4,371 registered accounts**.

## 4. Derived Schema & Engineered Attributes

| Field Name | Data Type | Purpose & Business Logic |
| :--- | :--- | :--- |
| `invoice_no` | `string` | Unique invoice identifier; 'C' indicates cancellation |
| `stock_code` | `string` | Product SKU or service indicator |
| `description` | `string` | Cleaned uppercase product description |
| `quantity` | `integer` | Ordered units (positive) or refunded units (negative) |
| `invoice_date` | `datetime` | Timestamp of transaction |
| `unit_price` | `float` | Unit price in GBP (£) |
| `line_total` | `float` | Extended line item amount (`quantity * unit_price`) |
| `customer_id` | `float/null` | Original customer ID where known |
| `customer_identifier`| `string` | Formatted identifier (`CUST_17850` or `'GUEST'`) |
| `is_guest_checkout` | `boolean` | Flag for unregistered transactions |
| `country` | `string` | Customer geographic location |
| `is_cancellation` | `boolean` | Flag for credit notes / refunds |
| `transaction_type` | `string` | `'PURCHASE'` vs `'CANCELLATION'` |
| `year`, `month`, `year_month` | `int/str` | Date partitioning dimensions |
| `day_name`, `hour` | `str/int` | Intraday seasonality dimensions |


## 5. Artifact Validation Summary

- **Cleaned Dataset:** `data/processed/online_retail_cleaned.csv` (534,129 rows)
- **Customer Dataset:** `data/processed/customer_summary.csv` (4,371 customer accounts)
- **Repeat Customer Rate:** 65.09% (2,845 repeat buyers out of 4,371)
- **Cancellation Rate:** 1.73% (9,251 cancellation lines)
