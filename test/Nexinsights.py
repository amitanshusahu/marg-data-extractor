import os
import time
import fitz
import sqlite3
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageOps
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


# PDF_DIR = "C:\\PrintedBills"
PDF_DIR = "/home/amitanshu/PrintedBills"

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

processed_files = set()  # Track processed files to avoid duplicates


DB_FILE = "bills.db"

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(bill_text):
    """Save extracted bill text to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bills (content) VALUES (?)", (bill_text,))
    conn.commit()
    conn.close()
    print("✅ Data saved to database.")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return text.strip() or "⚠ No readable text found in PDF."
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return ""

def confirm(pdf_path, bill_text, root):
    save_to_db(bill_text)  # Save extracted data

    # Try to delete the file with retries
    for _ in range(5):  # Try up to 5 times
        try:
            os.remove(pdf_path)
            print(f"🗑 Deleted: {pdf_path}")
            break  # Stop retrying if deletion succeeds
        except PermissionError:
            print("⏳ File is in use, retrying...")
            time.sleep(1)
        except FileNotFoundError:
            print("⚠ File not found, might have been removed manually.")
            break

    root.destroy()  # Close the popup

def cancel(pdf_path, root):
    """User cancels saving; keep the file and close the popup."""
    print("🚫 Data NOT saved.")
    root.destroy()


def show_bill_popup(pdf_path, bill_text):
    """Show extracted print job details in a GUI popup with a modern UI & images."""
    def run():
        root = tk.Tk()
        root.title("Nexus Print Watcher")

        # Set window position & size
        window_width, window_height = 550, 480
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.configure(bg="#F0F8FF")  # Light Blue Background

        # Load and Display Logo (Use a 100x100 PNG)
        try:
            logo_img = Image.open("logo.png").resize((192, 62), resample=Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=logo_photo, bg="#F0F8FF")  # Removed border background
            logo_label.image = logo_photo  # Keep reference
            logo_label.pack(pady=5)
        except Exception as e:
            print("Logo not found:", e)

        # Header with Logo
        header = tk.Label(root, text="♚ Nexus Print Watcher", font=("Arial", 14, "bold"), fg="white", bg="#1E3A8A", pady=10)
        header.pack(fill=tk.X)

        # Extracted Text Label
        tk.Label(root, text="Extracted Bill Details:", font=("Arial", 12, "bold"), bg="#F0F8FF").pack(pady=5)

        # Scrollable Text Area
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=65, height=15, font=("Arial", 10), bg="white", fg="black", borderwidth=2, relief="solid")
        text_area.insert(tk.END, bill_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(padx=10, pady=5)

        # Button Frame
        button_frame = tk.Frame(root, bg="#F0F8FF")
        button_frame.pack(pady=15)

        # Modern Save Button (Rounded Corners)
        save_button = tk.Button(
            button_frame, text="✔ Save to Database", command=lambda: confirm(pdf_path, bill_text, root),
            font=("Arial", 12, "bold"), fg="white", bg="#2563EB", activebackground="#1E40AF",
            padx=15, pady=8, borderwidth=0, relief="flat"
        )
        save_button.pack(side=tk.LEFT, padx=15)

        # Modern Cancel Button (Rounded Corners)
        cancel_button = tk.Button(
            button_frame, text="✘ Cancel", command=lambda: cancel(pdf_path, root),
            font=("Arial", 12, "bold"), fg="white", bg="#DC2626", activebackground="#991B1B",
            padx=15, pady=8, borderwidth=0, relief="flat"
        )
        cancel_button.pack(side=tk.RIGHT, padx=15)

        root.mainloop()

    threading.Thread(target=run, daemon=True).start()


class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".pdf"):
            pdf_path = event.src_path
            if pdf_path in processed_files:
                return  # Ignore if already processed

            time.sleep(3)  # Ensure the file is fully written

            # Check if the file is available for reading
            for _ in range(5):  # Try for a few seconds
                try:
                    with open(pdf_path, "rb"):
                        break
                except Exception:
                    time.sleep(1)  # Wait and retry

            print(f"📄 New bill detected: {pdf_path}")
            extracted_text = extract_text_from_pdf(pdf_path)

            if extracted_text.strip():  # Only show popup if text is extracted
                print("\n--- Extracted Bill Details ---\n")
                

                processed_files.add(pdf_path)  # Mark as processed
                show_bill_popup(pdf_path, extracted_text)

def monitor_folder():
    
    initialize_db()  # Ensure DB exists

    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, PDF_DIR, recursive=False)
    observer.start()
    print(f"👀 Monitoring {PDF_DIR} for new bills...")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Run the monitoring process
monitor_folder()
