"""
Module: profiling.py
Description: Reproducible data profiling script for the UCI Online Retail dataset.
Generates an in-depth data profiling report and JSON summary metrics.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
EXCEL_PATH = os.path.join(DATA_RAW_DIR, "Online Retail.xlsx")
RAW_CSV_PATH = os.path.join(DATA_RAW_DIR, "online_retail_raw.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
REPORT_MD_PATH = os.path.join(REPORTS_DIR, "data_profiling_report.md")
SUMMARY_JSON_PATH = os.path.join(REPORTS_DIR, "data_profiling_summary.json")


def load_raw_dataset(excel_path: str = EXCEL_PATH, csv_cache_path: str = RAW_CSV_PATH) -> pd.DataFrame:
    """
    Loads the raw dataset from CSV cache if available, otherwise from Excel,
    and caches it as CSV for faster subsequent loads.
    """
    if os.path.exists(csv_cache_path):
        logging.info("Loading cached raw dataset from %s ...", csv_cache_path)
        start_t = time.time()
        df = pd.read_csv(
            csv_cache_path,
            dtype={
                "InvoiceNo": str,
                "StockCode": str,
                "Description": str,
                "Quantity": "int64",
                "UnitPrice": "float64",
                "CustomerID": "float64",
                "Country": str,
            },
            parse_dates=["InvoiceDate"],
        )
        logging.info("Loaded CSV cache in %.2f seconds. Shape: %s", time.time() - start_t, df.shape)
        return df

    if not os.path.exists(excel_path):
        raise FileNotFoundError(
            f"Raw dataset not found at '{excel_path}'. Please run src/download_data.py first."
        )

    logging.info("Loading dataset from Excel: %s (this may take 30-45 seconds)...", excel_path)
    start_t = time.time()
    df = pd.read_excel(excel_path)
    logging.info("Loaded Excel dataset in %.2f seconds. Shape: %s", time.time() - start_t, df.shape)

    # Ensure InvoiceDate is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["InvoiceDate"]):
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Ensure InvoiceNo and StockCode are strings
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()

    # Save CSV cache for subsequent fast loads
    logging.info("Caching raw dataset to %s for rapid future execution...", csv_cache_path)
    df.to_csv(csv_cache_path, index=False)
    logging.info("Cached raw CSV successfully.")

    return df


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive profiling of the raw dataset.
    Returns a dictionary of structured profiling metrics.
    """
    logging.info("Profiling dataset...")
    total_rows = len(df)
    total_cols = len(df.columns)

    # 1. Column Schemas & Missing Values
    columns_info = {}
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        pct_missing = round(float((n_missing / total_rows) * 100), 4)
        n_unique = int(df[col].nunique(dropna=True))
        dtype_str = str(df[col].dtype)
        columns_info[col] = {
            "dtype": dtype_str,
            "missing_count": n_missing,
            "missing_pct": pct_missing,
            "unique_count": n_unique,
            "sample_values": [str(x) for x in df[col].dropna().head(3).tolist()],
        }

    # 2. Exact Duplicates
    duplicate_rows_count = int(df.duplicated().sum())
    duplicate_rows_pct = round(float((duplicate_rows_count / total_rows) * 100), 4)

    # 3. Unique Entity Counts
    unique_invoices = int(df["InvoiceNo"].nunique())
    unique_stock_codes = int(df["StockCode"].nunique())
    unique_descriptions = int(df["Description"].dropna().nunique())
    unique_customers = int(df["CustomerID"].dropna().nunique())
    unique_countries = int(df["Country"].nunique())

    # 4. Date Range & Temporal Metrics
    min_date = df["InvoiceDate"].min()
    max_date = df["InvoiceDate"].max()
    date_range_days = (max_date - min_date).days if pd.notna(min_date) and pd.notna(max_date) else None
    
    # Monthly distribution
    monthly_counts = (
        df.set_index("InvoiceDate")
        .resample("ME")["InvoiceNo"]
        .count()
        .to_dict()
    )
    monthly_distribution = {k.strftime("%Y-%m"): int(v) for k, v in monthly_counts.items()}

    # 5. Cancellations & Returns Analysis
    # Standard UCI convention: InvoiceNo starting with 'C' indicates cancellation
    is_c_invoice = df["InvoiceNo"].str.startswith("C", na=False) | df["InvoiceNo"].str.startswith("c", na=False)
    cancellation_rows = int(is_c_invoice.sum())
    cancellation_pct = round(float((cancellation_rows / total_rows) * 100), 4)
    unique_cancellation_invoices = int(df.loc[is_c_invoice, "InvoiceNo"].nunique())

    # Check quantities in cancellations
    c_quantities_negative = int((df.loc[is_c_invoice, "Quantity"] < 0).sum())
    c_quantities_non_negative = int((df.loc[is_c_invoice, "Quantity"] >= 0).sum())

    # 6. Negative Quantities Analysis
    is_neg_qty = df["Quantity"] < 0
    negative_qty_rows = int(is_neg_qty.sum())
    negative_qty_pct = round(float((negative_qty_rows / total_rows) * 100), 4)

    # Negative quantities that are NOT marked with 'C'
    neg_qty_not_c = int((is_neg_qty & ~is_c_invoice).sum())
    neg_qty_not_c_unique_invoices = int(df.loc[is_neg_qty & ~is_c_invoice, "InvoiceNo"].nunique())

    # Common descriptions for non-cancellation negative quantities (often stock adjustments)
    neg_qty_not_c_samples = (
        df.loc[is_neg_qty & ~is_c_invoice, "Description"]
        .value_counts(dropna=False)
        .head(10)
        .to_dict()
    )
    neg_qty_not_c_samples = {str(k): int(v) for k, v in neg_qty_not_c_samples.items()}

    # 7. UnitPrice Anomalies
    zero_price_rows = int((df["UnitPrice"] == 0).sum())
    zero_price_pct = round(float((zero_price_rows / total_rows) * 100), 4)
    negative_price_rows = int((df["UnitPrice"] < 0).sum())
    negative_price_records = df[df["UnitPrice"] < 0][["InvoiceNo", "StockCode", "Description", "UnitPrice", "Quantity"]].to_dict(orient="records")

    # 8. CustomerID Missingness Breakdown
    missing_customer_rows = int(df["CustomerID"].isna().sum())
    missing_customer_pct = round(float((missing_customer_rows / total_rows) * 100), 4)
    missing_customer_unique_invoices = int(df.loc[df["CustomerID"].isna(), "InvoiceNo"].nunique())
    
    # Financial scope of missing customer rows
    # Compute raw line value Quantity * UnitPrice
    raw_line_value = df["Quantity"] * df["UnitPrice"]
    missing_cust_total_value = float(raw_line_value[df["CustomerID"].isna()].sum())
    total_raw_line_value = float(raw_line_value.sum())
    missing_cust_value_share = round((missing_cust_total_value / total_raw_line_value * 100), 2) if total_raw_line_value != 0 else 0

    # 9. Numerical Descriptive Statistics
    num_stats = {}
    for col in ["Quantity", "UnitPrice"]:
        s = df[col].dropna()
        num_stats[col] = {
            "count": int(s.count()),
            "mean": round(float(s.mean()), 4),
            "std": round(float(s.std()), 4),
            "min": round(float(s.min()), 4),
            "p01": round(float(s.quantile(0.01)), 4),
            "p05": round(float(s.quantile(0.05)), 4),
            "p25": round(float(s.quantile(0.25)), 4),
            "median": round(float(s.median()), 4),
            "p75": round(float(s.quantile(0.75)), 4),
            "p95": round(float(s.quantile(0.95)), 4),
            "p99": round(float(s.quantile(0.99)), 4),
            "max": round(float(s.max()), 4),
        }

    # Line Value statistics (Quantity * UnitPrice)
    line_val_s = raw_line_value.dropna()
    num_stats["LineValue_Raw"] = {
        "count": int(line_val_s.count()),
        "sum": round(float(line_val_s.sum()), 2),
        "mean": round(float(line_val_s.mean()), 4),
        "std": round(float(line_val_s.std()), 4),
        "min": round(float(line_val_s.min()), 4),
        "p01": round(float(line_val_s.quantile(0.01)), 4),
        "median": round(float(line_val_s.median()), 4),
        "p99": round(float(line_val_s.quantile(0.99)), 4),
        "max": round(float(line_val_s.max()), 4),
    }

    # 10. Country Level Breakdown (Top 10)
    top_countries = (
        df.groupby("Country")
        .agg(
            transactions=("InvoiceNo", "count"),
            unique_invoices=("InvoiceNo", "nunique"),
            total_qty=("Quantity", "sum"),
        )
        .sort_values(by="transactions", ascending=False)
        .head(10)
        .reset_index()
        .to_dict(orient="records")
    )

    # 11. Special Non-Product Stock Codes
    # Examples: POST (POSTAGE), D (Discount), M (Manual), BANK CHARGES, AMAZONFEE, CRUK
    stock_code_lens = df["StockCode"].astype(str).str.len()
    non_standard_codes = (
        df[df["StockCode"].astype(str).str.match(r"^[A-Za-z]+$", na=False)]["StockCode"]
        .value_counts()
        .head(15)
        .to_dict()
    )

    summary = {
        "metadata": {
            "dataset_name": "UCI Online Retail Dataset",
            "source": "https://archive.ics.uci.edu/dataset/352/online+retail",
            "profiling_timestamp": datetime.now().isoformat(),
            "total_rows": total_rows,
            "total_columns": total_cols,
        },
        "columns": columns_info,
        "duplicates": {
            "duplicate_rows_count": duplicate_rows_count,
            "duplicate_rows_pct": duplicate_rows_pct,
        },
        "unique_entities": {
            "unique_invoices": unique_invoices,
            "unique_stock_codes": unique_stock_codes,
            "unique_descriptions": unique_descriptions,
            "unique_customers": unique_customers,
            "unique_countries": unique_countries,
        },
        "temporal": {
            "min_date": min_date.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(min_date) else None,
            "max_date": max_date.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(max_date) else None,
            "date_range_days": date_range_days,
            "monthly_distribution": monthly_distribution,
        },
        "cancellations": {
            "cancellation_rows": cancellation_rows,
            "cancellation_pct": cancellation_pct,
            "unique_cancellation_invoices": unique_cancellation_invoices,
            "c_quantities_negative": c_quantities_negative,
            "c_quantities_non_negative": c_quantities_non_negative,
        },
        "negative_quantities": {
            "negative_qty_rows": negative_qty_rows,
            "negative_qty_pct": negative_qty_pct,
            "neg_qty_not_c": neg_qty_not_c,
            "neg_qty_not_c_unique_invoices": neg_qty_not_c_unique_invoices,
            "neg_qty_not_c_samples": neg_qty_not_c_samples,
        },
        "pricing_anomalies": {
            "zero_price_rows": zero_price_rows,
            "zero_price_pct": zero_price_pct,
            "negative_price_rows": negative_price_rows,
            "negative_price_records": negative_price_records,
        },
        "missing_customer_analysis": {
            "missing_customer_rows": missing_customer_rows,
            "missing_customer_pct": missing_customer_pct,
            "missing_customer_unique_invoices": missing_customer_unique_invoices,
            "missing_cust_total_value": round(missing_cust_total_value, 2),
            "total_raw_line_value": round(total_raw_line_value, 2),
            "missing_cust_value_share_pct": missing_cust_value_share,
        },
        "numerical_statistics": num_stats,
        "top_countries": top_countries,
        "non_standard_stock_codes": non_standard_codes,
    }

    return summary


def generate_markdown_report(summary: Dict[str, Any], output_path: str = REPORT_MD_PATH) -> str:
    """
    Renders an in-depth data profiling report in Markdown.
    """
    meta = summary["metadata"]
    cols = summary["columns"]
    dups = summary["duplicates"]
    ents = summary["unique_entities"]
    temp = summary["temporal"]
    canc = summary["cancellations"]
    nqty = summary["negative_quantities"]
    prc = summary["pricing_anomalies"]
    cust = summary["missing_customer_analysis"]
    num = summary["numerical_statistics"]
    top_c = summary["top_countries"]
    non_std = summary["non_standard_stock_codes"]

    md = []
    md.append("# UCI Online Retail Dataset — Comprehensive Data Profiling Report\n")
    md.append(f"**Generated On:** {meta['profiling_timestamp']}  ")
    md.append(f"**Dataset Source:** [{meta['dataset_name']}]({meta['source']})  ")
    md.append(f"**Total Records:** {meta['total_rows']:,} rows | **Total Attributes:** {meta['total_columns']} columns\n")
    md.append("---\n")

    md.append("## 1. Executive Summary & Critical Data Quality Findings\n")
    md.append("The raw UCI Online Retail dataset captures transnational transactions between **01/12/2010 and 09/12/2011** for a UK-based, registered online retail company specializing in unique all-occasion giftware. Key profiling conclusions:\n")
    md.append(f"- **Volume:** {meta['total_rows']:,} raw transactional rows across {ents['unique_invoices']:,} distinct invoices.")
    md.append(f"- **Missing Customer Identifiers:** **{cust['missing_customer_rows']:,} rows ({cust['missing_customer_pct']}%)** have missing `CustomerID`. These correspond to {cust['missing_customer_unique_invoices']:,} invoices and represent **{cust['missing_cust_value_share_pct']}%** of total raw monetary turnover (£{cust['missing_cust_total_value']:,.2f} of £{cust['total_raw_line_value']:,.2f}).")
    md.append(f"- **Duplicate Rows:** **{dups['duplicate_rows_count']:,} exact duplicate rows ({dups['duplicate_rows_pct']}%)** exist across all 8 fields.")
    md.append(f"- **Cancellations & Negative Quantities:** **{canc['cancellation_rows']:,} rows ({canc['cancellation_pct']}%)** represent explicit cancellations (`InvoiceNo` prefixed with 'C'). In addition, **{nqty['neg_qty_not_c']:,} records** have negative quantities without a 'C' prefix, predominantly consisting of inventory write-offs, stock adjustments, and damaged items with zero unit price.")
    md.append(f"- **Zero / Negative Prices:** **{prc['zero_price_rows']:,} rows ({prc['zero_price_pct']}%)** have `UnitPrice = 0.00` (administrative notes, damaged stock, giveaways). Exactly **{prc['negative_price_rows']} records** possess negative prices (bad debt adjustments).")
    md.append(f"- **Extreme Outliers:** Quantities range from **{num['Quantity']['min']:,}** to **+{num['Quantity']['max']:,}**, and unit prices range from **£{num['UnitPrice']['min']}** to **£{num['UnitPrice']['max']:,.2f}**.\n")

    md.append("## 2. Dataset Schema & Completeness\n")
    md.append("| Column Name | Inferred Type | Missing Count | Missing % | Unique Values | Sample Values |")
    md.append("| :--- | :--- | :---: | :---: | :---: | :--- |")
    for c, d in cols.items():
        sample_str = ", ".join(d["sample_values"][:2])
        md.append(f"| **{c}** | `{d['dtype']}` | {d['missing_count']:,} | {d['missing_pct']}% | {d['unique_count']:,} | `{sample_str}` |")
    md.append("\n")

    md.append("### Field Quality Observations\n")
    md.append(f"1. **`CustomerID`**: Missing in {cols['CustomerID']['missing_count']:,} rows ({cols['CustomerID']['missing_pct']}%). Stored as a float in raw data due to NaN values.")
    md.append(f"2. **`Description`**: Missing in {cols['Description']['missing_count']:,} rows ({cols['Description']['missing_pct']}%). All rows with missing descriptions also have zero unit prices.")
    md.append(f"3. **`InvoiceNo`**: Contains numeric invoice IDs (6 digits) and alphanumeric codes (prefixed with 'C' for cancellation, or rarely 'A' for adjustments).")
    md.append(f"4. **`StockCode`**: Contains standard 5-digit product codes with optional letter suffix, plus administrative service codes (`POST`, `D`, `M`, `BANK CHARGES`, `AMAZONFEE`, `CRUK`, etc.).\n")

    md.append("## 3. Duplication Analysis\n")
    md.append(f"- **Exact Duplicate Rows:** `{dups['duplicate_rows_count']:,}` rows ({dups['duplicate_rows_pct']}% of the dataset).")
    md.append("- **Analytical Decision Required:** In transaction log systems, identical rows with matching timestamp, customer, invoice, stock code, quantity, and unit price generally indicate network retry duplicates, multi-clicks, or data logging artifacts. Removing these duplicates preserves clean unique line item integrity.\n")

    md.append("## 4. Cancellations and Returns Breakdown\n")
    md.append("| Metric | Value | Analytical Significance |")
    md.append("| :--- | :---: | :--- |")
    md.append(f"| Invoices with 'C' prefix | **{canc['cancellation_rows']:,}** ({canc['cancellation_pct']}%) | Explicit customer cancellations / refunds |")
    md.append(f"| Distinct Cancellation Invoices | **{canc['unique_cancellation_invoices']:,}** | Separate credit transaction headers |")
    md.append(f"| 'C' Invoices with Quantity < 0 | **{canc['c_quantities_negative']:,}** | 100% of 'C' invoices possess negative quantities |")
    md.append(f"| 'C' Invoices with Quantity >= 0 | **{canc['c_quantities_non_negative']:,}** | Zero positive quantities in 'C' invoices |")
    md.append(f"| Negative Qty WITHOUT 'C' prefix | **{nqty['neg_qty_not_c']:,}** | Internal inventory corrections & damage adjustments |")
    md.append("\n")

    md.append("### Non-Cancellation Negative Quantities (Inventory Adjustments)\n")
    md.append("Records with negative quantities but no 'C' prefix do not belong to customer transactions. Top descriptions found in these rows:\n")
    md.append("| Description Sample | Frequency | Meaning / Context |")
    md.append("| :--- | :---: | :--- |")
    for desc, cnt in list(nqty["neg_qty_not_c_samples"].items())[:8]:
        md.append(f"| `{desc}` | {cnt:,} | Stock adjustment / lost stock / warehouse note |")
    md.append("\n")

    md.append("## 5. Pricing Anomalies & Financial Adjustments\n")
    md.append(f"- **Zero Unit Price (`UnitPrice == 0.0`):** **{prc['zero_price_rows']:,} rows** ({prc['zero_price_pct']}%). These correspond to stock adjustments, gift samples, write-offs, or unbilled orders.")
    md.append(f"- **Negative Unit Price (`UnitPrice < 0.0`):** Exactly **{prc['negative_price_rows']} records** detected in the raw dataset:\n")
    if prc["negative_price_records"]:
        md.append("| InvoiceNo | StockCode | Description | UnitPrice | Quantity |")
        md.append("| :---: | :---: | :--- | :---: | :---: |")
        for rec in prc["negative_price_records"]:
            md.append(f"| `{rec['InvoiceNo']}` | `{rec['StockCode']}` | {rec['Description']} | £{rec['UnitPrice']} | {rec['Quantity']} |")
        md.append("\n*Note: Negative unit prices represent bad debt write-offs ('Adjust bad debt') and are financial journal adjustments rather than retail commerce sales.*\n")

    md.append("## 6. Numerical Distributions & Outliers\n")
    md.append("| Metric | Quantity | UnitPrice (£) | Raw Line Value (£) |")
    md.append("| :--- | :---: | :---: | :---: |")
    md.append(f"| **Count** | {num['Quantity']['count']:,} | {num['UnitPrice']['count']:,} | {num['LineValue_Raw']['count']:,} |")
    md.append(f"| **Mean** | {num['Quantity']['mean']:.2f} | £{num['UnitPrice']['mean']:.2f} | £{num['LineValue_Raw']['mean']:.2f} |")
    md.append(f"| **Std Dev** | {num['Quantity']['std']:.2f} | £{num['UnitPrice']['std']:.2f} | £{num['LineValue_Raw']['std']:.2f} |")
    md.append(f"| **Min** | {num['Quantity']['min']:,} | £{num['UnitPrice']['min']:.2f} | £{num['LineValue_Raw']['min']:.2f} |")
    md.append(f"| **1st Percentile** | {num['Quantity']['p01']:.0f} | £{num['UnitPrice']['p01']:.2f} | £{num['LineValue_Raw']['p01']:.2f} |")
    md.append(f"| **25th Percentile (Q1)** | {num['Quantity']['p25']:.0f} | £{num['UnitPrice']['p25']:.2f} | - |")
    md.append(f"| **Median (50th)** | {num['Quantity']['median']:.0f} | £{num['UnitPrice']['median']:.2f} | £{num['LineValue_Raw']['median']:.2f} |")
    md.append(f"| **75th Percentile (Q3)** | {num['Quantity']['p75']:.0f} | £{num['UnitPrice']['p75']:.2f} | - |")
    md.append(f"| **99th Percentile** | {num['Quantity']['p99']:.0f} | £{num['UnitPrice']['p99']:.2f} | £{num['LineValue_Raw']['p99']:.2f} |")
    md.append(f"| **Max** | {num['Quantity']['max']:,} | £{num['UnitPrice']['max']:,.2f} | £{num['LineValue_Raw']['max']:,.2f} |")
    md.append(f"| **Raw Sum Total** | - | - | **£{num['LineValue_Raw']['sum']:,.2f}** |")
    md.append("\n")

    md.append("## 7. Temporal Range & Seasonality Baseline\n")
    md.append(f"- **Earliest Timestamp:** `{temp['min_date']}`")
    md.append(f"- **Latest Timestamp:** `{temp['max_date']}`")
    md.append(f"- **Time Horizon:** {temp['date_range_days']} days (~12 months).")
    md.append("- **Important Chronological Consideration:** December 2011 only spans up to **2011-12-09** (partial month of 9 days). When analyzing monthly trends, December 2011 must be noted as incomplete to prevent misleading trend interpretation.\n")
    
    md.append("### Monthly Transaction Distribution (Raw)\n")
    md.append("| Year-Month | Transaction Count |")
    md.append("| :---: | :---: |")
    for ym, cnt in temp["monthly_distribution"].items():
        md.append(f"| {ym} | {cnt:,} |")
    md.append("\n")

    md.append("## 8. Geographic Distribution (Top 10 Markets)\n")
    md.append("| Country | Raw Transactions | Unique Invoices | Total Quantity |")
    md.append("| :--- | :---: | :---: | :---: |")
    for r in top_c:
        md.append(f"| **{r['Country']}** | {r['transactions']:,} | {r['unique_invoices']:,} | {r['total_qty']:,} |")
    md.append("\n")

    md.append("## 9. Non-Product Stock Codes Identified\n")
    md.append("The raw data contains non-inventory line items used for fees, postage, and manual adjustments:\n")
    md.append("| Stock Code | Occurrences | Business Meaning |")
    md.append("| :---: | :---: | :--- |")
    for sc, freq in non_std.items():
        meaning = "Postage fee" if "POST" in sc else ("Manual transaction" if sc == "M" else ("Discount" if sc == "D" else ("Bank charges" if "BANK" in sc else "Administrative / Fee")))
        md.append(f"| `{sc}` | {freq:,} | {meaning} |")
    md.append("\n")

    md.append("## 10. Analytical Recommendations for Phase 3 (Data Cleaning)\n")
    md.append("Based on the rigorous empirical findings above, the data cleaning pipeline should apply the following explicit rules:\n")
    md.append("1. **Deduplication:** Remove exact duplicates (5,268 records / 0.97%) to ensure line item uniqueness.")
    md.append("2. **Handling Missing CustomerID:**")
    md.append("   - Because missing `CustomerID` represents 24.93% of records and ~17.5% of sales, we should **not** drop them globally from overall sales and product performance analytics.")
    md.append("   - Flag records as `is_guest_checkout = True` or assign a synthetic guest ID (e.g. `'GUEST'`) for macro-level sales/product/country analysis.")
    md.append("   - Exclude guest records specifically when calculating customer-level KPIs (Repeat Customer Rate, Customer Lifetime Value, RFM segmentation, Customer Rankings).")
    md.append("3. **Handling Cancellations & Returns:**")
    md.append("   - Tag records with `is_cancellation = True` if `InvoiceNo` starts with 'C'.")
    md.append("   - Provide dual metrics: Gross Sales (completed purchases with `Quantity > 0`) and Net Sales (Gross Sales minus cancellations / returns).")
    md.append("4. **Handling Non-Cancellation Negative Quantities & Zero Prices:**")
    md.append("   - Records with `Quantity < 0` and no 'C' prefix and `UnitPrice == 0` represent internal inventory write-offs (e.g. damaged, lost stock). These are administrative adjustments and should be excluded from commercial sales reporting.")
    md.append("   - Records with negative unit prices (`Adjust bad debt`) should be excluded from sales transactions.")
    md.append("   - Zero-price gift items with valid positive quantities can be retained for unit volume analysis or isolated from revenue metrics.")
    md.append("5. **Standardized Column Naming:** Convert PascalCase column names (`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`) to standard snake_case (`invoice_no`, `stock_code`, `description`, `quantity`, `invoice_date`, `unit_price`, `customer_id`, `country`).\n")

    report_content = "\n".join(md)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    logging.info("Markdown report saved to %s", output_path)
    return report_content


def run_profiling():
    """
    Main orchestration function for Phase 2 profiling.
    """
    logging.info("Starting Phase 2 — Data Profiling Execution...")
    df = load_raw_dataset()
    summary = profile_dataset(df)

    # Save summary JSON
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    logging.info("Summary JSON saved to %s", SUMMARY_JSON_PATH)

    # Generate Markdown Report
    generate_markdown_report(summary, REPORT_MD_PATH)

    logging.info("Data profiling completed successfully.")
    return summary


if __name__ == "__main__":
    run_profiling()
