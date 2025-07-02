import smtplib
import ssl
from email.message import EmailMessage
from config import DB_FILE
import os

# You can also store these in a secure config or encrypted vault
SENDER_EMAIL = "varsada9@gmail.com"
SENDER_PASSWORD = "wfojiixiirgbmsrg"
RECEIVER_EMAIL = "amitansusahu@gmail.com"

def send_db_via_gmail():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return

    msg = EmailMessage()
    msg['Subject'] = "NexInsights DB Backup"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg.set_content("Attached is the current bills database file from NexInsights.")

    with open(DB_FILE, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(DB_FILE)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print("Database sent successfully via Gmail.")
    except Exception as e:
        print(f"Failed to send email: {e}")
