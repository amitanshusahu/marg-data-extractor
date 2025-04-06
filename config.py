import os

# PDF_DIR = "C:\\PrintedBills"
PDF_DIR = "/home/amitanshu/PrintedBills"
DB_FILE = "bills.db"
API_ENDPOINT = "http://localhost:4000/api/upload/daily/bill"

# just to prevent duplicates
processed_files = set()

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)
