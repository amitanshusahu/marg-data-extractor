import os

# PDF_DIR = "C:\\PrintedBills"
PDF_DIR = "/home/amitanshu/PrintedBills"
DB_FILE = "bills.db"
API_ENDPOINT = "https://wekeyar-dashboard.onrender.com/api/upload/daily/bill"

# just to prevent duplicates
processed_files = set()

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)
