"""
Unit tests for business metrics module (Phase 6).
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import filter_transactions, calculate_business_kpis, compute_monthly_kpis


@pytest.fixture
def sample_metrics_df():
    data = {
        "invoice_no": ["1001", "1002", "C1003", "1004"],
        "stock_code": ["P1", "P2", "P1", "P3"],
        "description": ["Prod 1", "Prod 2", "Prod 1", "Prod 3"],
        "quantity": [10, 5, -2, 4],
        "invoice_date": pd.to_datetime(["2011-03-01", "2011-03-15", "2011-03-20", "2011-04-05"]),
        "unit_price": [10.0, 20.0, 10.0, 25.0],
        "line_total": [100.0, 100.0, -20.0, 100.0],
        "customer_id": [201.0, 202.0, 201.0, np.nan],
        "customer_identifier": ["CUST_201", "CUST_202", "CUST_201", "GUEST"],
        "is_guest_checkout": [False, False, False, True],
        "country": ["United Kingdom", "Germany", "United Kingdom", "United Kingdom"],
        "is_cancellation": [False, False, True, False],
        "transaction_type": ["PURCHASE", "PURCHASE", "CANCELLATION", "PURCHASE"],
        "year": [2011, 2011, 2011, 2011],
        "month": [3, 3, 3, 4],
        "year_month": ["2011-03", "2011-03", "2011-03", "2011-04"],
        "day_name": ["Tuesday", "Tuesday", "Sunday", "Tuesday"],
        "hour": [10, 12, 14, 16],
    }
    return pd.DataFrame(data)


def test_calculate_business_kpis(sample_metrics_df):
    kpis = calculate_business_kpis(sample_metrics_df)
    # Gross: 100 + 100 + 100 = 300.0
    # Refund: 20.0
    # Net: 280.0
    assert kpis["gross_revenue"] == 300.0
    assert kpis["refund_amount"] == 20.0
    assert kpis["net_revenue"] == 280.0
    assert kpis["completed_orders"] == 3
    assert kpis["cancelled_orders"] == 1
    assert kpis["aov"] == round(280.0 / 3, 2)
    assert kpis["guest_orders"] == 1
    assert kpis["active_customers"] == 2


def test_empty_dataframe_handling():
    empty_df = pd.DataFrame(columns=["line_total", "quantity", "invoice_no", "is_cancellation", "is_guest_checkout"])
    kpis = calculate_business_kpis(empty_df)
    assert kpis["net_revenue"] == 0.0
    assert kpis["completed_orders"] == 0
    assert kpis["aov"] == 0.0


def test_filter_transactions(sample_metrics_df):
    # Test date filter
    filtered_date = filter_transactions(sample_metrics_df, start_date="2011-04-01")
    assert len(filtered_date) == 1
    assert filtered_date.iloc[0]["invoice_no"] == "1004"

    # Test country filter
    filtered_country = filter_transactions(sample_metrics_df, countries=["Germany"])
    assert len(filtered_country) == 1
    assert filtered_country.iloc[0]["country"] == "Germany"

    # Test guest filter
    filtered_guest = filter_transactions(sample_metrics_df, customer_mode="GUEST_ONLY")
    assert len(filtered_guest) == 1
    assert filtered_guest.iloc[0]["is_guest_checkout"] is True or filtered_guest.iloc[0]["is_guest_checkout"] == 1
