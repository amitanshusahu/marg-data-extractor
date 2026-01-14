import smtplib
import ssl
from email.message import EmailMessage
from config import DB_FILE, API_ENDPOINT
import os
from plyer import notification
import sqlite3
import requests
import json
from settings_gui import load_config

# You can also store these in a secure config or encrypted vault
SENDER_EMAIL = "varsada9@gmail.com"
SENDER_PASSWORD = "wfojiixiirgbmsrg"
RECEIVER_EMAIL = "amitansusahu@gmail.com" 
# "srikant.panigrahy@gmail.com"

def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # seconds
    )

def send_diagnosis_via_gmail():
    if not os.path.exists(DB_FILE):
        notify("NexInsights", "Database file not found.")
        return

    # Build diagnosis report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("NEXINSIGHTS DIAGNOSIS REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    # 1. Test API with 10 unsent bills
    report_lines.append("1. API TEST - UNSENT BILLS")
    report_lines.append("-" * 60)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM bills WHERE sent_at IS NULL LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            bill_ids = [row[0] for row in rows]
            bill_contents = [row[1] for row in rows]
            
            report_lines.append(f"Bill IDs being sent: {bill_ids}")
            report_lines.append("")
            
            payload = {"bills": bill_contents}
            response = requests.post(API_ENDPOINT, json=payload, timeout=10)
            
            report_lines.append(f"API Endpoint: {API_ENDPOINT}")
            report_lines.append(f"Status Code: {response.status_code}")
            report_lines.append(f"Response: {json.dumps(response.json(), indent=2) if response.headers.get('content-type', '').startswith('application/json') else response.text}")
        else:
            report_lines.append("No unsent bills found in database.")
    except Exception as e:
        report_lines.append(f"ERROR: {str(e)}")
    
    report_lines.append("")
    
    # 2. Current Configuration
    report_lines.append("2. CURRENT CONFIGURATION")
    report_lines.append("-" * 60)
    try:
        config = load_config()
        report_lines.append(json.dumps(config, indent=2))
    except Exception as e:
        report_lines.append(f"ERROR loading config: {str(e)}")
    
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 60)
    
    diagnosis_report = "\n".join(report_lines)

    config = load_config()
    
    # Create email
    msg = EmailMessage()
    msg['Subject'] = f"NexInsights Diagnosis Report {config.get('store_name', 'Unknown Store')}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg.set_content(diagnosis_report)

    # Attach database file
    with open(DB_FILE, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(DB_FILE)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        notify("NexInsights", "Diagnosis report sent successfully via Gmail.")
    except Exception as e:
        notify("NexInsights - Email Error", f"Failed to send diagnosis report: {e}")
