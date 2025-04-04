import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdf_processing import extract_text_from_pdf
from gui import show_bill_popup
from config import PDF_DIR

processed_files = set()

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".pdf") and event.src_path not in processed_files:
            time.sleep(3)  # Ensure file is fully written

            for _ in range(5):
                try:
                    with open(event.src_path, "rb"):
                        break
                except:
                    time.sleep(1)

            print(f"📄 New bill detected: {event.src_path}")
            extracted_text = extract_text_from_pdf(event.src_path)

            if extracted_text.strip():
                processed_files.add(event.src_path)
                show_bill_popup(event.src_path, extracted_text)

def monitor_folder():
    observer = Observer()
    observer.schedule(PDFHandler(), PDF_DIR, recursive=False)
    observer.start()
    print(f"👀 Monitoring {PDF_DIR} for new bills...")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
