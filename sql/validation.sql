-- =====================================================================
-- E-COMMERCE SALES ANALYTICS — SQL VALIDATION & RECONCILIATION QUERIES
-- Used to systematically cross-validate SQL aggregation results against
-- independent Python / Pandas calculation outputs.
-- =====================================================================

-- 1. Macro Revenue Reconciliation
SELECT
    COUNT(*) AS total_transaction_rows,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    COUNT(DISTINCT CASE WHEN is_cancellation = 0 THEN invoice_no END) AS unique_purchase_invoices,
    COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END) AS unique_cancellation_invoices,
    ROUND(SUM(CASE WHEN is_cancellation = 0 THEN line_total ELSE 0 END), 2) AS sql_gross_revenue,
    ROUND(ABS(SUM(CASE WHEN is_cancellation = 1 THEN line_total ELSE 0 END)), 2) AS sql_refund_total,
    ROUND(SUM(line_total), 2) AS sql_net_revenue,
    SUM(quantity) AS sql_net_units_sold
FROM fact_transactions;

-- 2. Customer Dimension Reconciliation
SELECT
    COUNT(*) AS total_dim_customers,
    SUM(CASE WHEN is_repeat_customer = 1 THEN 1 ELSE 0 END) AS sql_repeat_customers,
    ROUND(SUM(CASE WHEN is_repeat_customer = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS sql_repeat_rate_pct,
    ROUND(SUM(gross_spend), 2) AS sql_dim_gross_spend,
    ROUND(SUM(refunded_amount), 2) AS sql_dim_refunded_amount,
    ROUND(SUM(net_spend), 2) AS sql_dim_net_spend
FROM dim_customers;

-- 3. Guest Checkout Reconciliation
SELECT
    COUNT(*) AS guest_transactions,
    ROUND(SUM(line_total), 2) AS guest_net_revenue,
    ROUND(SUM(line_total) * 100.0 / (SELECT SUM(line_total) FROM fact_transactions), 2) AS guest_revenue_share_pct
FROM fact_transactions
WHERE is_guest_checkout = 1;
