import os
import platform
from db import save_to_db
from log_setup import logger
import winsound

def play_notification_sound():
    if platform.system() == "Windows":
        winsound.MessageBeep()
    else:
        print("🔇 Skipping beep: Not on Windows.")


def print_pdf(pdf_path):
    try:
        os.startfile(pdf_path)
    except Exception as open_err:
        print(f"[Error] Failed to open file as fallback: {open_err}")
        logger.error(f"[Error] Failed to open file as fallback: {open_err}")
        

def show_bill_popup(pdf_path, bill_text):
    # play_notification_sound()
    save_to_db(bill_text, pdf_path)
    print_pdf(pdf_path)