"""
Unit tests for data profiling module (Phase 2).
"""

import os
import json
import pytest
import pandas as pd
from src.profiling import (
    load_raw_dataset,
    profile_dataset,
    generate_markdown_report,
    BASE_DIR,
    SUMMARY_JSON_PATH,
    REPORT_MD_PATH,
)


@pytest.fixture(scope="session")
def sample_test_df():
    """
    Creates a representative synthetic subset mirroring the UCI Online Retail schema
    for rapid unit testing.
    """
    data = {
        "InvoiceNo": ["536365", "536365", "C536379", "536380", "536381", "536381"],
        "StockCode": ["85123A", "71053", "D", "84406B", "22728", "22728"],
        "Description": [
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "WHITE METAL LANTERN",
            "Discount",
            "CREAM CUPID HEARTS COAT HANGER",
            "ALARM CLOCK BAKELIKE PINK",
            "ALARM CLOCK BAKELIKE PINK",
        ],
        "Quantity": [6, 6, -1, 8, 24, 24],
        "InvoiceDate": pd.to_datetime([
            "2010-12-01 08:26:00",
            "2010-12-01 08:26:00",
            "2010-12-01 09:41:00",
            "2010-12-01 09:45:00",
            "2010-12-01 09:49:00",
            "2010-12-01 09:49:00",
        ]),
        "UnitPrice": [2.55, 3.39, 27.50, 2.75, 3.75, 3.75],
        "CustomerID": [17850.0, 17850.0, 14527.0, None, 15311.0, 15311.0],
        "Country": [
            "United Kingdom",
            "United Kingdom",
            "United Kingdom",
            "France",
            "Germany",
            "Germany",
        ],
    }
    return pd.DataFrame(data)


def test_profiling_logic(sample_test_df):
    """
    Validates that the profile_dataset function correctly identifies
    row counts, missing values, duplicates, and cancellations.
    """
    summary = profile_dataset(sample_test_df)

    assert summary["metadata"]["total_rows"] == 6
    assert summary["metadata"]["total_columns"] == 8

    # Check duplicates: row 4 and row 5 are exact duplicates
    assert summary["duplicates"]["duplicate_rows_count"] == 1

    # Check missing CustomerID: 1 row missing
    assert summary["columns"]["CustomerID"]["missing_count"] == 1

    # Check cancellations: 1 invoice starting with 'C'
    assert summary["cancellations"]["cancellation_rows"] == 1
    assert summary["cancellations"]["unique_cancellation_invoices"] == 1

    # Check unique entities
    assert summary["unique_entities"]["unique_invoices"] == 4
    assert summary["unique_entities"]["unique_customers"] == 3


def test_report_generation(sample_test_df, tmp_path):
    """
    Validates markdown report generation without writing to production report dir.
    """
    summary = profile_dataset(sample_test_df)
    test_report_path = str(tmp_path / "test_report.md")
    report_content = generate_markdown_report(summary, test_report_path)

    assert os.path.exists(test_report_path)
    assert "# UCI Online Retail Dataset — Comprehensive Data Profiling Report" in report_content
    assert "C536379" not in report_content or "cancellation" in report_content.lower()
