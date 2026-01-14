import requests
import sqlite3
import time
from config import DB_FILE, API_ENDPOINT
from log_setup import logger
from settings_gui import load_config

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sent_at DATETIME
        );
    """)
    conn.commit()
    conn.close()

def save_to_db(bill_text, pdf_path):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bills (content) VALUES (?)", (bill_text,))
    conn.commit()
    conn.close()
    print("✅ Data saved to local database.")

def is_online():
    try:
        requests.head("https://1.1.1.1", timeout=5)
        return True
    except requests.RequestException:
        return False

def retry_unsent():
    print("✅ Network Queue Started")
    logger.info("Network Queue Started")

    previous_error_response = None

    while True:
        if not is_online():
            print("⚠️ Offline. Skipping sync cycle.")
            time.sleep(load_config()["retry_request_time"])
            continue

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, content FROM bills WHERE sent_at IS NULL LIMIT 10")
        rows = cursor.fetchall()

        if rows:
            try:
                bill_ids = [row[0] for row in rows]
                bill_contents = [row[1] for row in rows]
                
                payload = {
                    "bills": bill_contents,
                }
                response = requests.post(API_ENDPOINT, json=payload, timeout=10)
                print(f"Syncing {len(bill_ids)} bills (IDs: {bill_ids})...", response)
                
                if response.status_code == 200:
                    placeholders = ','.join('?' * len(bill_ids))
                    cursor.execute(f"UPDATE bills SET sent_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})", bill_ids)
                    print(f"✅ {len(bill_ids)} bills synced with server.")
                    logger.info(f"{len(bill_ids)} bills synced with server (IDs: {bill_ids}).")
                    previous_error_response = None
                else:
                    current_error = f"{response.status_code}, {response.json()}"
                    if current_error != previous_error_response:
                        print(f"❌ Failed to sync {len(bill_ids)} bills: {current_error}")
                        logger.error(f"Failed to sync {len(bill_ids)} bills (IDs: {bill_ids}): {current_error}")
                        previous_error_response = current_error

            except Exception as e:
                current_error = str(e)
                if current_error != previous_error_response:
                    print(f"⚠️ Network/API error for bills: {e}")
                    logger.exception(f"Network/API error for bills: {e}")
                    previous_error_response = current_error

        conn.commit()
        conn.close()

        config = load_config()
        sleep_time = config.get("retry_request_time", 600)
        if sleep_time < 600:
            sleep_time = 600
        time.sleep(config["retry_request_time"])
