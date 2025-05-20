import os
from pathlib import Path
from log_setup import logger

# Writable local app data folder
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", os.getcwd())) / "NexInsights"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# config file path
CONFIG_FILE = APP_DATA_DIR / "config.json"

# Database path
DB_FILE = APP_DATA_DIR / "bills.db"

# PDF output folder (inside AppData)
PDF_DIR = APP_DATA_DIR / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)  # make sure it exists

# API endpoint
API_ENDPOINT = "https://wekeyar-dashboard.onrender.com/api/upload/daily/bill"


print(f"📂 PDF directory: {PDF_DIR}")
print(f"🗃️  Database file: {DB_FILE}")