"""
Module: download_data.py
Description: Reproducible automated downloader for the UCI Online Retail dataset.
"""

import os
import urllib.request
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

UCI_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
ZIP_TARGET = os.path.join(RAW_DATA_DIR, "online_retail.zip")
EXCEL_TARGET = os.path.join(RAW_DATA_DIR, "Online Retail.xlsx")


def download_and_extract(url: str = UCI_URL, target_dir: str = RAW_DATA_DIR) -> str:
    """
    Downloads the online retail zip file from UCI and extracts the Excel dataset.
    Returns path to the extracted Excel file.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    if os.path.exists(EXCEL_TARGET):
        logging.info("Excel dataset already exists at: %s", EXCEL_TARGET)
        return EXCEL_TARGET

    logging.info("Downloading dataset from: %s", url)
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(ZIP_TARGET, "wb") as out_file:
        out_file.write(response.read())
    logging.info("Downloaded %d bytes to %s", os.path.getsize(ZIP_TARGET), ZIP_TARGET)

    logging.info("Extracting zip archive...")
    with zipfile.ZipFile(ZIP_TARGET, "r") as zip_ref:
        zip_ref.extractall(target_dir)
        logging.info("Extracted files: %s", zip_ref.namelist())

    if not os.path.exists(EXCEL_TARGET):
        raise FileNotFoundError(f"Expected extracted file '{EXCEL_TARGET}' not found.")

    logging.info("Dataset successfully downloaded and verified.")
    return EXCEL_TARGET


if __name__ == "__main__":
    download_and_extract()
