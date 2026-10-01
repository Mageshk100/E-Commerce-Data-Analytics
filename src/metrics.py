"""
Module: metrics.py
Description: Production Business KPI Engine.
Computes standardized e-commerce business metrics with explicit handling of
cancellations, guest checkouts, and dynamic multi-dimensional filtering.
Note: In accordance with data integrity guidelines, revenue is NEVER labeled profit,
as unit cost (COGS) is not provided in the UCI Online Retail dataset.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


def filter_transactions(
    df: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    countries: Optional[List[str]] = None,
    customer_mode: str = "ALL",  # "ALL", "REGISTERED_ONLY", "GUEST_ONLY"
) -> pd.DataFrame:
    """
    Applies multi-dimensional filters to the transaction DataFrame.
    """
    filtered = df.copy()

    if start_date is not None:
        filtered = filtered[filtered["invoice_date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["invoice_date"] <= pd.to_datetime(end_date)]
    if countries and len(countries) > 0 and "ALL" not in countries:
        filtered = filtered[filtered["country"].isin(countries)]

    if customer_mode == "REGISTERED_ONLY":
        filtered = filtered[~filtered["is_guest_checkout"]]
    elif customer_mode == "GUEST_ONLY":
        filtered = filtered[filtered["is_guest_checkout"]]

    return filtered


def calculate_business_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes core portfolio-grade business KPIs from a (filtered) transaction DataFrame.
    """
    if df.empty:
        return {
            "gross_revenue": 0.0,
            "refund_amount": 0.0,
            "net_revenue": 0.0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "total_orders": 0,
            "units_sold": 0,
            "units_returned": 0,
            "net_units": 0,
            "aov": 0.0,
            "cancellation_rate_pct": 0.0,
            "refund_rate_pct": 0.0,
            "active_customers": 0,
            "repeat_customers": 0,
            "repeat_customer_rate_pct": 0.0,
            "guest_orders": 0,
            "guest_revenue": 0.0,
            "guest_revenue_share_pct": 0.0,
        }

    # Purchases vs Cancellations masks
    is_purchase = ~df["is_cancellation"]
    is_canc = df["is_cancellation"]

    gross_revenue = float(df.loc[is_purchase, "line_total"].sum())
    refund_amount = float(abs(df.loc[is_canc, "line_total"].sum()))
    net_revenue = float(df["line_total"].sum())

    completed_orders = int(df.loc[is_purchase, "invoice_no"].nunique())
    cancelled_orders = int(df.loc[is_canc, "invoice_no"].nunique())
    total_distinct_invoices = int(df["invoice_no"].nunique())

    units_sold = int(df.loc[is_purchase, "quantity"].sum())
    units_returned = int(abs(df.loc[is_canc, "quantity"].sum()))
    net_units = int(df["quantity"].sum())

    aov = round(net_revenue / completed_orders, 2) if completed_orders > 0 else 0.0
    cancellation_rate = (
        round(cancelled_orders / total_distinct_invoices * 100, 2) if total_distinct_invoices > 0 else 0.0
    )
    refund_rate = round(refund_amount / gross_revenue * 100, 2) if gross_revenue > 0 else 0.0

    # Registered Customer Analysis
    registered_df = df[~df["is_guest_checkout"]]
    active_customers = int(registered_df["customer_id"].nunique())
    
    # Calculate repeat customer rate in this slice
    if active_customers > 0:
        cust_orders = registered_df[~registered_df["is_cancellation"]].groupby("customer_id")["invoice_no"].nunique()
        repeat_customers = int((cust_orders > 1).sum())
        repeat_customer_rate = round((repeat_customers / active_customers) * 100, 2)
    else:
        repeat_customers = 0
        repeat_customer_rate = 0.0

    # Guest checkouts
    guest_df = df[df["is_guest_checkout"]]
    guest_orders = int(guest_df.loc[is_purchase, "invoice_no"].nunique())
    guest_revenue = float(guest_df["line_total"].sum())
    guest_revenue_share = round((guest_revenue / net_revenue) * 100, 2) if net_revenue > 0 else 0.0

    return {
        "gross_revenue": round(gross_revenue, 2),
        "refund_amount": round(refund_amount, 2),
        "net_revenue": round(net_revenue, 2),
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_orders": total_distinct_invoices,
        "units_sold": units_sold,
        "units_returned": units_returned,
        "net_units": net_units,
        "aov": aov,
        "cancellation_rate_pct": cancellation_rate,
        "refund_rate_pct": refund_rate,
        "active_customers": active_customers,
        "repeat_customers": repeat_customers,
        "repeat_customer_rate_pct": repeat_customer_rate,
        "guest_orders": guest_orders,
        "guest_revenue": round(guest_revenue, 2),
        "guest_revenue_share_pct": guest_revenue_share,
    }


def compute_monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly KPI summary with Month-over-Month growth rates.
    """
    monthly = (
        df.groupby("year_month")
        .agg(
            gross_revenue=("line_total", lambda x: float(x[x > 0].sum())),
            refund_amount=("line_total", lambda x: abs(float(x[x < 0].sum()))),
            net_revenue=("line_total", "sum"),
            completed_orders=("invoice_no", lambda x: x[~x.str.startswith(("C", "c"))].nunique()),
            cancelled_orders=("invoice_no", lambda x: x[x.str.startswith(("C", "c"))].nunique()),
            units_sold=("quantity", lambda x: int(x[x > 0].sum())),
        )
        .reset_index()
    )

    monthly["gross_revenue"] = monthly["gross_revenue"].round(2)
    monthly["refund_amount"] = monthly["refund_amount"].round(2)
    monthly["net_revenue"] = monthly["net_revenue"].round(2)
    monthly["aov"] = (monthly["net_revenue"] / monthly["completed_orders"]).round(2)
    monthly["cancellation_rate_pct"] = (
        monthly["cancelled_orders"] / (monthly["completed_orders"] + monthly["cancelled_orders"]) * 100
    ).round(2)
    monthly["mom_revenue_growth_pct"] = (monthly["net_revenue"].pct_change() * 100).round(2)

    return monthly
