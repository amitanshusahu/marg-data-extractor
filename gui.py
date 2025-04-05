import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk
import threading
import os
import platform
from db import save_to_db

if platform.system() == "Windows":
    import win32print
    import win32api
    import winsound

def play_notification_sound():
    if platform.system() == "Windows":
        winsound.MessageBeep()
    else:
        print("🔇 Skipping beep: Not on Windows.")

def get_printer_list():
    if platform.system() != "Windows":
        return []
    return [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]

def print_pdf(pdf_path, printer_name):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"Attempting to print PDF: {pdf_path}")
    print(f"Target printer: {printer_name}")

    try:
        win32api.ShellExecute(
            0,
            "print",
            pdf_path,
            f'/d:"{printer_name}"',
            ".",
            0
        )
        print("Print job sent successfully.")
    except Exception as e:
        print(f"[Warning] Printing failed: {e}")
        print("Falling back to opening the file instead.")
        try:
            os.startfile(pdf_path)
        except Exception as open_err:
            print(f"[Error] Failed to open file as fallback: {open_err}")


def confirm(pdf_path, bill_text, printer_name, root):
    print_pdf(pdf_path, printer_name)
    root.destroy()

def cancel(root):
    print("🚫 Print Cancled.")
    root.destroy()

def show_bill_popup(pdf_path, bill_text):
    def run():
        play_notification_sound()
        root = tk.Tk()
        root.title("🧾 Nexus Print Watcher")
        root.geometry("580x500")
        root.configure(bg="#F0F8FF")

        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()

        try:
            logo_img = Image.open("logo.png").resize((192, 62))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=logo_photo, bg="#F0F8FF")
            logo_label.image = logo_photo  # keep reference
            logo_label.pack(pady=10)
        except:
            pass

        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        text_area.insert(tk.END, bill_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(padx=20, pady=10)

        # Dropdown for printers
        printer_label = tk.Label(root, text="🖨 Choose Printer:", bg="#F0F8FF", font=("Arial", 10, "bold"))
        printer_label.pack(pady=(5, 0))

        printers = get_printer_list()
        selected_printer = tk.StringVar(value=win32print.GetDefaultPrinter() if printers else "")

        printer_dropdown = ttk.Combobox(root, values=printers, textvariable=selected_printer, state="readonly", width=60)
        printer_dropdown.pack(pady=(0, 15))

        button_frame = tk.Frame(root, bg="#F0F8FF")
        button_frame.pack(pady=15)

        print_button = tk.Button(
            button_frame, text="✔ Print ",
            command=lambda: confirm(pdf_path, bill_text, selected_printer.get(), root),
            fg="white", bg="#2563EB", width=15
        )
        print_button.pack(side=tk.LEFT, padx=15)

        cancel_button = tk.Button(
            button_frame, text="✘ Cancel",
            command=lambda: cancel(root),
            fg="white", bg="#DC2626", width=15
        )
        cancel_button.pack(side=tk.RIGHT, padx=15)

        root.mainloop()

    save_to_db(bill_text)

    threading.Thread(target=run, daemon=True).start()
