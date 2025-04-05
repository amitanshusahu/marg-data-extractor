import os

# PDF_DIR = "C:\\PrintedBills"
PDF_DIR = "/home/amitanshu/PrintedBills"
DB_FILE = "bills.db"
API_ENDPOINT = ""

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)
