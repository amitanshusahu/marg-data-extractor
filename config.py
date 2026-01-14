import os
from pathlib import Path
import json

# Writable local app data folder
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", os.getcwd())) / "NexInsights"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# config file path
CONFIG_FILE = APP_DATA_DIR / "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "printer": "",
            "auto_print": True,
            "retry_request_time": 60*10,
            "api_url": "https://wekeyar.core.server.nexusinfotech.co/api/upload/daily/bill"
        }
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


# Database path
DB_FILE = APP_DATA_DIR / "bills.db"

# PDF output folder (inside AppData)
PDF_DIR = APP_DATA_DIR / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)  # make sure it exists

# API endpoint
config = load_config()
API_ENDPOINT = config["api_url"]


print(f"📂 PDF directory: {PDF_DIR}")
print(f"🗃️  Database file: {DB_FILE}")