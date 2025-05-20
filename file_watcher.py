import time
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdf_processing import extract_text_from_pdf
from gui import handel_bill
from config import PDF_DIR

# Tracks last event time for each file to debounce multiple triggers
file_event_times = defaultdict(float)

def recently_triggered(path: str, threshold: float = 5.0) -> bool:
    now = time.time()
    if now - file_event_times[path] < threshold:
        return True
    file_event_times[path] = now
    return False


class PDFHandler(FileSystemEventHandler):
    def process_pdf(self, path):
        if not path.endswith(".pdf"):
            return

        if recently_triggered(path):
            return

        time.sleep(0.5)  # Wait a bit for file to finish writing

        # Retry opening the file if it's still being written
        for _ in range(5):
            try:
                with open(path, "rb"):
                    break
            except IOError:
                time.sleep(3)

        print(f"📄 PDF ready: {path}")
        extracted_text = extract_text_from_pdf(path)

        if extracted_text.strip():
            handel_bill(path, extracted_text)

    def on_created(self, event):
        if not event.is_directory:
            self.process_pdf(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_pdf(event.src_path)


def monitor_folder():
    observer = Observer()
    observer.schedule(PDFHandler(), PDF_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
