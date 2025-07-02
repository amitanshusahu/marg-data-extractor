import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from config import CONFIG_FILE , load_config
import win32print

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def open_settings():
    config = load_config()

    def save_and_close():
        try:
            retry_time = int(retry_time_var.get())
            if retry_time <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Retry request time must be a positive integer.")
            return

        config["printer"] = printer_var.get()
        config["auto_print"] = auto_print_var.get()
        config["retry_request_time"] = retry_time
        config["api_url"] = api_url_var.get()
        save_config(config)
        messagebox.showinfo("Settings", "Settings saved successfully.")
        settings_win.destroy()

    # Main Window
    settings_win = tk.Tk()
    settings_win.title("NexInsight Settings")
    settings_win.geometry("450x280")
    settings_win.configure(bg="white")

    # Style Setup
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook", background="white", borderwidth=0)
    style.configure("TNotebook.Tab", background="#f2f2f2", padding=(10, 5), font=("Segoe UI", 10))
    style.map("TNotebook.Tab", background=[("selected", "#ffffff")])
    style.configure("TFrame", background="white")
    style.configure("TLabel", background="white", font=("Segoe UI", 10))
    style.configure("TCheckbutton", background="white", font=("Segoe UI", 10))
    style.configure("TEntry", padding=5)
    style.configure("TButton", font=("Segoe UI", 10, "bold"))

    # Notebook
    notebook = ttk.Notebook(settings_win)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)

    # General Tab
    general_frame = ttk.Frame(notebook)
    notebook.add(general_frame, text="General")

    printer_var = tk.StringVar(value=config.get("printer", ""))

    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = [printer[1] for printer in win32print.EnumPrinters(flags, None, 1)]

    ttk.Label(general_frame, text="Select Printer:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    printer_dropdown = ttk.Combobox(general_frame, textvariable=printer_var, values=printers, state="readonly")
    printer_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    auto_print_var = tk.BooleanVar(value=config.get("auto_print", True))
    auto_print_check = ttk.Checkbutton(general_frame, text="Print Automatically", variable=auto_print_var)
    auto_print_check.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    general_frame.columnconfigure(1, weight=1)

    # Advanced Tab
    advanced_frame = ttk.Frame(notebook)
    notebook.add(advanced_frame, text="Advanced")

    retry_time_var = tk.StringVar(value=str(config.get("retry_request_time", 120)))
    api_url_var = tk.StringVar(value=config.get("api_url", "https://wekeyar-dashboard.onrender.com/api/upload/daily/bill"))

    ttk.Label(advanced_frame, text="Retry Time (seconds):").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    retry_time_entry = ttk.Entry(advanced_frame, textvariable=retry_time_var)
    retry_time_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    ttk.Label(advanced_frame, text="API URL:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    api_url_entry = ttk.Entry(advanced_frame, textvariable=api_url_var)
    api_url_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    advanced_frame.columnconfigure(1, weight=1)

    # Save Button
    save_button = ttk.Button(settings_win, text="Save", command=save_and_close)
    save_button.pack(pady=(5, 10))

    settings_win.mainloop()
