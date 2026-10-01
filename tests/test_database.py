"""
Unit tests for database and SQL analytics engine (Phase 5).
"""

import pytest
from sqlalchemy import text
from src.database import get_engine, run_sql_query, validate_sql_vs_python


def test_database_connectivity():
    engine, db_type = get_engine()
    assert engine is not None
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).fetchone()
        assert result[0] == 1


def test_sql_reconciliation():
    engine, _ = get_engine()
    val_data = validate_sql_vs_python(engine)
    assert val_data["all_passed"] is True
    for item in val_data["reconciliation"]:
        assert item["status"] == "PASS"
