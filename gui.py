import os
import platform
from db import save_to_db
from log_setup import logger
import winsound
import subprocess
import win32print
from pathlib import Path
import sys
from settings_gui import load_config

BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
SUMATRA_PATH = str(BASE_DIR / "SumatraPDF-3.5.2-64.exe")

def list_printers():
    default_printer = win32print.GetDefaultPrinter()
    return default_printer


def play_notification_sound():
    if platform.system() == "Windows":
        winsound.MessageBeep()


def silent_print(pdf_path, printer_name):
    try:
        cmd = f'"{SUMATRA_PATH}" -print-to "{printer_name}" "{pdf_path}"'
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"[Error] Print command failed: {e}")


def open_pdf(pdf_path):
    try:
        os.startfile(pdf_path)
    except Exception as open_err:
        print(f"[Error] Failed to open file as fallback: {open_err}")
        logger.error(f"[Error] Failed to open file as fallback: {open_err}")
        

def handel_bill(pdf_path, bill_text):
    play_notification_sound()
    save_to_db(bill_text, pdf_path)
    config = load_config()
    if config["auto_print"]:
        if config["printer"]:
            silent_print(pdf_path, config["printer"])
        else:
            printerName = list_printers()
            if printerName:
                silent_print(pdf_path, printerName)
            else:
                logger.error(f"[Error] No matching printer found")