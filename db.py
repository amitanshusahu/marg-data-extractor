import requests
import sqlite3
import time
from config import DB_FILE, API_ENDPOINT, processed_files

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

def save_to_db(bill_text):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bills (content) VALUES (?)", (bill_text,))
    conn.commit()
    conn.close()
    print("✅ Data saved to database.")
    # TODO: check how to empty a set
    processed_files = set()


def retry_unsent():
    while True:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, content FROM bills WHERE sent_at IS NULL LIMIT 10")
        rows = cursor.fetchall()

        for row_id, content in rows:
            try:
                response = requests.post(API_ENDPOINT, json={"bill": content}, timeout=10)
                if response.status_code == 200:
                    cursor.execute("UPDATE bills SET sent_at = CURRENT_TIMESTAMP WHERE id = ?", (row_id,))
                    print(f"✅ Bill ID {row_id} synced with server.")
                else:
                    print(f"❌ Failed to sync bill ID {row_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Network/API error for bill ID {row_id}: {e}")

        conn.commit()
        conn.close()

        time.sleep(30)  # Wait before next retry
