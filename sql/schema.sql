-- =====================================================================
-- E-COMMERCE SALES ANALYTICS DATABASE SCHEMA
-- Target Engine: MySQL 8.0+ / SQLite 3.35+ compatible
-- =====================================================================

-- 1. ANALYTICAL FACT TABLE (Denormalized for OLAP performance)
CREATE TABLE IF NOT EXISTS fact_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no VARCHAR(20) NOT NULL,
    stock_code VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    quantity INT NOT NULL,
    invoice_date DATETIME NOT NULL,
    unit_price DECIMAL(10, 4) NOT NULL,
    line_total DECIMAL(12, 2) NOT NULL,
    customer_id DECIMAL(12, 1),
    customer_identifier VARCHAR(30) NOT NULL,
    is_guest_checkout BOOLEAN NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_cancellation BOOLEAN NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    hour INT NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_trans_invoice ON fact_transactions(invoice_no);
CREATE INDEX IF NOT EXISTS idx_trans_date ON fact_transactions(invoice_date);
CREATE INDEX IF NOT EXISTS idx_trans_cust ON fact_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_trans_stock ON fact_transactions(stock_code);
CREATE INDEX IF NOT EXISTS idx_trans_country ON fact_transactions(country);
CREATE INDEX IF NOT EXISTS idx_trans_canc ON fact_transactions(is_cancellation);

-- 2. NORMALIZED DIMENSION: CUSTOMERS
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id DECIMAL(12, 1) PRIMARY KEY,
    customer_identifier VARCHAR(30) NOT NULL,
    country VARCHAR(100) NOT NULL,
    first_purchase DATETIME,
    last_purchase DATETIME,
    total_transactions INT,
    unique_orders INT,
    cancellation_count INT,
    total_units_purchased INT,
    total_units_returned INT,
    gross_spend DECIMAL(12, 2),
    refunded_amount DECIMAL(12, 2),
    net_spend DECIMAL(12, 2),
    is_repeat_customer BOOLEAN,
    lifespan_days DECIMAL(10, 1)
);

-- Performance Index
CREATE INDEX IF NOT EXISTS idx_dim_cust_spend ON dim_customers(net_spend);
CREATE INDEX IF NOT EXISTS idx_dim_cust_repeat ON dim_customers(is_repeat_customer);
