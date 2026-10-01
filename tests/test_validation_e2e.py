"""
End-to-End Production Validation and Data Integrity Test Suite (Phase 8).
Verifies strict mathematical reconciliation across CSV files, Pandas transformations,
and SQL tables.
"""

import os
import pytest
import pandas as pd
import numpy as np
from sqlalchemy import text
from src.database import get_engine, CLEANED_CSV_PATH, CUSTOMER_SUMMARY_PATH


def test_production_cleaned_dataset_integrity():
    assert os.path.exists(CLEANED_CSV_PATH), "Cleaned transactions file missing."
    df = pd.read_csv(CLEANED_CSV_PATH)

    # 1. Total row count matches audited number
    assert len(df) == 534129

    # 2. Schema check
    expected_cols = [
        "invoice_no", "stock_code", "description", "quantity",
        "invoice_date", "unit_price", "line_total", "customer_id",
        "customer_identifier", "is_guest_checkout", "country",
        "is_cancellation", "transaction_type", "year", "month",
        "year_month", "day_name", "hour"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"

    # 3. Unit price integrity
    assert (df["unit_price"] <= 0).sum() == 0, "No zero or negative unit prices permitted."

    # 4. Cancellation logic consistency
    canc_slice = df[df["is_cancellation"] == True]
    purchase_slice = df[df["is_cancellation"] == False]
    assert (canc_slice["quantity"] >= 0).sum() == 0, "All cancellations must have negative quantity."
    assert (purchase_slice["quantity"] <= 0).sum() == 0, "All purchases must have positive quantity."

    # 5. Line total precision
    diff = (df["line_total"] - (df["quantity"] * df["unit_price"])).abs()
    assert (diff > 0.05).sum() == 0, "Line total must match quantity * unit_price within 5 cents."


def test_customer_summary_dataset_integrity():
    assert os.path.exists(CUSTOMER_SUMMARY_PATH), "Customer summary file missing."
    df_cust = pd.read_csv(CUSTOMER_SUMMARY_PATH)
    df_trans = pd.read_csv(CLEANED_CSV_PATH)

    # 1. Customer count
    assert len(df_cust) == 4371
    assert df_cust["customer_id"].nunique() == 4371

    # 2. Repeat rate math
    repeat_count = int(df_cust["is_repeat_customer"].sum())
    repeat_rate = round(repeat_count / len(df_cust) * 100, 2)
    assert repeat_rate == 65.09

    # 3. Spend reconciliation with registered transactions
    registered_trans = df_trans[df_trans["is_guest_checkout"] == False]
    reg_trans_net = float(registered_trans["line_total"].sum())
    cust_sum_net = float(df_cust["net_spend"].sum())
    assert abs(cust_sum_net - reg_trans_net) < 1.0


def test_sql_engine_database_integrity():
    engine, _ = get_engine()
    with engine.connect() as conn:
        fact_rows = conn.execute(text("SELECT COUNT(*) FROM fact_transactions;")).fetchone()[0]
        dim_rows = conn.execute(text("SELECT COUNT(*) FROM dim_customers;")).fetchone()[0]
        net_revenue = conn.execute(text("SELECT ROUND(SUM(line_total), 2) FROM fact_transactions;")).fetchone()[0]

    assert fact_rows == 534129
    assert dim_rows == 4371
    assert round(net_revenue, 2) == 9748131.07
