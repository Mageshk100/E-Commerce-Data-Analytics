"""
Unit tests for data cleaning module (Phase 3).
"""

import pytest
import pandas as pd
import numpy as np
from src.cleaning import run_cleaning_pipeline


@pytest.fixture
def synthetic_raw_df():
    """
    Creates a representative edge-case synthetic raw dataframe.
    """
    return pd.DataFrame({
        "InvoiceNo": [
            "536365",       # Normal valid purchase
            "536365",       # Duplicate row (should be removed)
            "C536366",      # Explicit cancellation
            "536367",       # Non-cancellation with negative qty (inventory write-off, should be removed)
            "A563186",      # Accounting debt adjustment (negative price, should be removed)
            "536368",       # Zero price sample (should be removed)
            "536369",       # Guest checkout purchase (missing customer_id, should be kept)
            "536370",       # Repeat purchase from same customer
        ],
        "StockCode": ["85123A", "85123A", "85123A", "22423", "B", "21730", "22900", "22901"],
        "Description": [
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "damaged stock",
            "Adjust bad debt",
            "giveaway sample",
            "SET 3 RETROSPOT TEA TOWELS",
            "POSTAGE STAMP BOX",
        ],
        "Quantity": [6, 6, -2, -10, 1, 5, 2, 4],
        "InvoiceDate": pd.to_datetime([
            "2011-01-05 10:00:00",
            "2011-01-05 10:00:00",
            "2011-01-05 11:00:00",
            "2011-01-06 12:00:00",
            "2011-01-07 13:00:00",
            "2011-01-08 14:00:00",
            "2011-01-09 15:00:00",
            "2011-01-10 16:00:00",
        ]),
        "UnitPrice": [2.50, 2.50, 2.50, 0.00, -11062.06, 0.00, 4.00, 3.00],
        "CustomerID": [12345.0, 12345.0, 12345.0, np.nan, np.nan, 12346.0, np.nan, 12345.0],
        "Country": ["United Kingdom"] * 8,
    })


def test_cleaning_pipeline_filtering(synthetic_raw_df):
    """
    Validates that each filtering step correctly handles edge cases.
    """
    df_cleaned, df_customers, audit = run_cleaning_pipeline(synthetic_raw_df)

    # 1. Row count validation
    # Initial: 8
    # - 1 duplicate (536365)
    # - 1 bad debt (A563186)
    # - 1 inventory adjustment (536367)
    # - 1 zero price (536368)
    # Remaining: 4 rows (536365, C536366, 536369, 536370)
    assert len(df_cleaned) == 4

    # 2. Cancellation validation
    cancellations = df_cleaned[df_cleaned["is_cancellation"]]
    assert len(cancellations) == 1
    assert cancellations.iloc[0]["invoice_no"] == "C536366"
    assert cancellations.iloc[0]["quantity"] == -2
    assert cancellations.iloc[0]["line_total"] == -5.00

    # 3. Guest checkout validation
    guests = df_cleaned[df_cleaned["is_guest_checkout"]]
    assert len(guests) == 1
    assert guests.iloc[0]["invoice_no"] == "536369"
    assert guests.iloc[0]["customer_identifier"] == "GUEST"

    # 4. Financial integrity
    gross = df_cleaned.loc[~df_cleaned["is_cancellation"], "line_total"].sum()
    refund = abs(df_cleaned.loc[df_cleaned["is_cancellation"], "line_total"].sum())
    net = df_cleaned["line_total"].sum()
    assert round(gross - refund, 2) == round(net, 2)

    # 5. Customer summary validation
    # Registered customers: only 12345.0 (had 536365, C536366, 536370)
    assert len(df_customers) == 1
    cust_record = df_customers.iloc[0]
    assert cust_record["customer_id"] == 12345.0
    assert cust_record["unique_orders"] == 2  # 536365 and 536370
    assert cust_record["is_repeat_customer"] is True or cust_record["is_repeat_customer"] == 1
