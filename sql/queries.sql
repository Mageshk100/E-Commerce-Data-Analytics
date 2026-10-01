-- =====================================================================
-- E-COMMERCE SALES ANALYTICS — ADVANCED ANALYTICAL SQL SUITE
-- Features: CTEs, Window Functions (LAG, DENSE_RANK, SUM OVER, NTILE),
-- Aggregations, Joins, and Trend Analysis.
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Monthly Financial & Growth Dynamics
-- Calculates Gross Revenue, Refunds, Net Revenue, Completed Orders,
-- Average Order Value (AOV), and Month-over-Month (MoM) Growth Rate.
-- ---------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT
        year_month,
        ROUND(SUM(CASE WHEN is_cancellation = 0 THEN line_total ELSE 0 END), 2) AS gross_revenue,
        ROUND(ABS(SUM(CASE WHEN is_cancellation = 1 THEN line_total ELSE 0 END)), 2) AS refund_amount,
        ROUND(SUM(line_total), 2) AS net_revenue,
        COUNT(DISTINCT CASE WHEN is_cancellation = 0 THEN invoice_no END) AS completed_orders,
        COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END) AS cancelled_orders,
        SUM(CASE WHEN is_cancellation = 0 THEN quantity ELSE 0 END) AS units_sold
    FROM fact_transactions
    GROUP BY year_month
)
SELECT
    year_month,
    gross_revenue,
    refund_amount,
    net_revenue,
    completed_orders,
    ROUND(net_revenue / NULLIF(completed_orders, 0), 2) AS aov,
    LAG(net_revenue, 1) OVER (ORDER BY year_month) AS prev_month_net_revenue,
    ROUND(
        (net_revenue - LAG(net_revenue, 1) OVER (ORDER BY year_month)) 
        / NULLIF(LAG(net_revenue, 1) OVER (ORDER BY year_month), 0) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_metrics
ORDER BY year_month ASC;


-- ---------------------------------------------------------------------
-- QUERY 2: Product Performance, Ranking & Cumulative Revenue Share
-- Excludes service codes; ranks products by Net Revenue using DENSE_RANK()
-- and computes running cumulative share of total catalog revenue.
-- ---------------------------------------------------------------------
WITH product_sales AS (
    SELECT
        stock_code,
        MAX(description) AS product_name,
        SUM(CASE WHEN is_cancellation = 0 THEN quantity ELSE 0 END) AS units_sold,
        ROUND(SUM(line_total), 2) AS net_revenue,
        COUNT(DISTINCT invoice_no) AS total_orders
    FROM fact_transactions
    WHERE stock_code NOT IN ('POST', 'DOT', 'M', 'D', 'S', 'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'B')
    GROUP BY stock_code
),
ranked_products AS (
    SELECT
        stock_code,
        product_name,
        units_sold,
        net_revenue,
        total_orders,
        DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS revenue_rank,
        SUM(net_revenue) OVER (ORDER BY net_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_net_revenue,
        SUM(net_revenue) OVER () AS total_catalog_revenue
    FROM product_sales
    WHERE net_revenue > 0
)
SELECT
    revenue_rank,
    stock_code,
    product_name,
    units_sold,
    net_revenue,
    total_orders,
    ROUND((running_net_revenue / total_catalog_revenue) * 100, 2) AS cumulative_revenue_pct
FROM ranked_products
WHERE revenue_rank <= 20
ORDER BY revenue_rank ASC;


-- ---------------------------------------------------------------------
-- QUERY 3: Customer Value Segmentation & Quintile Ranking
-- Segments registered customers into 5 spending tiers using NTILE(5)
-- and evaluates VIP customer revenue contribution.
-- ---------------------------------------------------------------------
WITH customer_ranks AS (
    SELECT
        customer_id,
        customer_identifier,
        country,
        unique_orders,
        net_spend,
        DENSE_RANK() OVER (ORDER BY net_spend DESC) AS spend_rank,
        NTILE(5) OVER (ORDER BY net_spend DESC) AS spend_quintile,
        SUM(net_spend) OVER () AS total_registered_spend
    FROM dim_customers
    WHERE net_spend > 0
)
SELECT
    spend_quintile,
    COUNT(customer_id) AS customer_count,
    ROUND(MIN(net_spend), 2) AS min_spend_in_quintile,
    ROUND(MAX(net_spend), 2) AS max_spend_in_quintile,
    ROUND(SUM(net_spend), 2) AS total_quintile_spend,
    ROUND((SUM(net_spend) / MAX(total_registered_spend)) * 100, 2) AS quintile_spend_share_pct
FROM customer_ranks
GROUP BY spend_quintile
ORDER BY spend_quintile ASC;


-- ---------------------------------------------------------------------
-- QUERY 4: Geographic Market Performance & Average Order Value
-- Analyzes country performance, total revenue, global share %, and AOV.
-- ---------------------------------------------------------------------
WITH country_summary AS (
    SELECT
        country,
        COUNT(invoice_no) AS transaction_lines,
        COUNT(DISTINCT CASE WHEN is_cancellation = 0 THEN invoice_no END) AS completed_orders,
        ROUND(SUM(line_total), 2) AS net_revenue,
        SUM(quantity) AS net_units,
        COUNT(DISTINCT customer_id) AS unique_registered_customers
    FROM fact_transactions
    GROUP BY country
)
SELECT
    country,
    transaction_lines,
    completed_orders,
    net_revenue,
    net_units,
    unique_registered_customers,
    ROUND(net_revenue / NULLIF(completed_orders, 0), 2) AS aov,
    ROUND((net_revenue / SUM(net_revenue) OVER ()) * 100, 2) AS global_revenue_share_pct,
    DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS market_rank
FROM country_summary
ORDER BY market_rank ASC
LIMIT 15;


-- ---------------------------------------------------------------------
-- QUERY 5: Repeat Customer Rate & Loyalty Behavior
-- Measures customer order frequency distribution and retention rate.
-- ---------------------------------------------------------------------
SELECT
    is_repeat_customer,
    CASE WHEN is_repeat_customer = 1 THEN 'Repeat Buyer (2+ Orders)' ELSE 'One-Time Buyer (1 Order)' END AS customer_segment,
    COUNT(customer_id) AS customer_count,
    ROUND((COUNT(customer_id) * 100.0 / (SELECT COUNT(*) FROM dim_customers)), 2) AS customer_pct,
    ROUND(SUM(net_spend), 2) AS total_net_spend,
    ROUND((SUM(net_spend) * 100.0 / (SELECT SUM(net_spend) FROM dim_customers)), 2) AS revenue_pct,
    ROUND(AVG(unique_orders), 1) AS avg_orders_per_customer,
    ROUND(AVG(net_spend), 2) AS avg_spend_per_customer
FROM dim_customers
GROUP BY is_repeat_customer;


-- ---------------------------------------------------------------------
-- QUERY 6: Cancellation and Return Dynamics
-- Evaluates monthly refund rates relative to gross revenue.
-- ---------------------------------------------------------------------
SELECT
    year_month,
    COUNT(DISTINCT CASE WHEN is_cancellation = 0 THEN invoice_no END) AS purchase_orders,
    COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END) AS return_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END) * 100.0 
        / NULLIF(COUNT(DISTINCT invoice_no), 0), 
        2
    ) AS return_order_rate_pct,
    ROUND(SUM(CASE WHEN is_cancellation = 0 THEN line_total ELSE 0 END), 2) AS gross_sales,
    ROUND(ABS(SUM(CASE WHEN is_cancellation = 1 THEN line_total ELSE 0 END)), 2) AS refund_value,
    ROUND(
        ABS(SUM(CASE WHEN is_cancellation = 1 THEN line_total ELSE 0 END)) * 100.0 
        / NULLIF(SUM(CASE WHEN is_cancellation = 0 THEN line_total ELSE 0 END), 0), 
        2
    ) AS refund_value_ratio_pct
FROM fact_transactions
GROUP BY year_month
ORDER BY year_month ASC;
