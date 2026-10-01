"""
Unit tests for exploratory data analysis module (Phase 4).
"""

import pytest
import pandas as pd
import numpy as np
from src.eda import (
    analyze_monthly_trends,
    analyze_seasonality,
    analyze_product_performance,
    analyze_geography,
    analyze_customer_dynamics,
)


@pytest.fixture
def sample_cleaned_df():
    """
    Creates a clean synthetic dataset for verifying EDA mathematical aggregations.
    """
    data = {
        "invoice_no": ["5001", "5002", "C5003", "5004", "5005"],
        "stock_code": ["SKU_A", "SKU_B", "SKU_A", "SKU_C", "SKU_A"],
        "description": ["Item A", "Item B", "Item A", "Item C", "Item A"],
        "quantity": [10, 5, -2, 20, 15],
        "unit_price": [10.0, 20.0, 10.0, 5.0, 10.0],
        "line_total": [100.0, 100.0, -20.0, 100.0, 150.0],
        "customer_id": [101.0, 102.0, 101.0, np.nan, 101.0],
        "customer_identifier": ["CUST_101", "CUST_102", "CUST_101", "GUEST", "CUST_101"],
        "is_guest_checkout": [False, False, False, True, False],
        "country": ["United Kingdom", "Germany", "United Kingdom", "France", "United Kingdom"],
        "is_cancellation": [False, False, True, False, False],
        "transaction_type": ["PURCHASE", "PURCHASE", "CANCELLATION", "PURCHASE", "PURCHASE"],
        "year": [2011, 2011, 2011, 2011, 2011],
        "month": [1, 1, 1, 2, 2],
        "year_month": ["2011-01", "2011-01", "2011-01", "2011-02", "2011-02"],
        "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "hour": [10, 11, 12, 14, 15],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_customer_summary():
    data = {
        "customer_id": [101.0, 102.0],
        "customer_identifier": ["CUST_101", "CUST_102"],
        "country": ["United Kingdom", "Germany"],
        "total_transactions": [3, 1],
        "unique_orders": [2, 1],
        "cancellation_count": [1, 0],
        "total_units_purchased": [25, 5],
        "total_units_returned": [2, 0],
        "gross_spend": [250.0, 100.0],
        "refunded_amount": [20.0, 0.0],
        "net_spend": [230.0, 100.0],
        "is_repeat_customer": [True, False],
        "lifespan_days": [25.0, 0.0],
    }
    return pd.DataFrame(data)


def test_monthly_trends_math(sample_cleaned_df):
    monthly, fig = analyze_monthly_trends(sample_cleaned_df)
    assert len(monthly) == 2
    # Month 1: 100 + 100 - 20 = 180 Net Revenue
    m1 = monthly[monthly["year_month"] == "2011-01"].iloc[0]
    assert m1["gross_revenue"] == 200.0
    assert m1["refund_amount"] == 20.0
    assert m1["net_revenue"] == 180.0
    assert m1["order_volume"] == 2  # 5001 and 5002


def test_seasonality_aggregations(sample_cleaned_df):
    dow_df, hour_df, fig_dow, fig_hour = analyze_seasonality(sample_cleaned_df)
    assert len(dow_df) == 7
    # Saturday must have 0 orders
    sat = dow_df[dow_df["day_name"] == "Saturday"].iloc[0]
    assert sat["order_count"] == 0
    assert sat["net_revenue"] == 0.0


def test_geography_math(sample_cleaned_df):
    geo_df, fig = analyze_geography(sample_cleaned_df)
    assert len(geo_df) == 3
    total_rev = geo_df["net_revenue"].sum()
    assert round(total_rev, 2) == 430.0
    # Shares must sum to 100%
    assert round(geo_df["revenue_share_pct"].sum(), 1) == 100.0


def test_customer_dynamics_math(sample_cleaned_df, sample_customer_summary):
    metrics, fig = analyze_customer_dynamics(sample_cleaned_df, sample_customer_summary)
    assert metrics["total_registered_customers"] == 2
    assert metrics["repeat_customers"] == 1
    assert metrics["one_time_customers"] == 1
    assert metrics["repeat_rate_pct"] == 50.0
