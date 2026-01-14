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

        config["store_name"] = store_name_var.get()
        config["printer"] = printer_var.get()
        config["auto_print"] = auto_print_var.get()
        config["retry_request_time"] = retry_time
        config["api_url"] = api_url_var.get()
        save_config(config)
        messagebox.showinfo("Success", "Settings saved successfully.")
        settings_win.destroy()

    # Main Window
    settings_win = tk.Tk()
    settings_win.title("Nexinsights - Settings")
    settings_win.geometry("480x400")
    settings_win.configure(bg="#f5f5f5")
    settings_win.resizable(False, False)

    # Main Container
    main_container = tk.Frame(settings_win, bg="#f5f5f5")
    main_container.pack(fill='both', expand=True, padx=15, pady=15)

    # Content Frame with white background
    content_frame = tk.Frame(main_container, bg="white", relief="flat", bd=0)
    content_frame.pack(fill='both', expand=True)

    # Variables
    store_name_var = tk.StringVar(value=config.get("store_name", ""))
    printer_var = tk.StringVar(value=config.get("printer", ""))
    auto_print_var = tk.BooleanVar(value=config.get("auto_print", True))
    retry_time_var = tk.StringVar(value=str(config.get("retry_request_time", 600)))
    api_url_var = tk.StringVar(value=config.get("api_url", "https://wekeyar.core.server.nexusinfotech.co/api/upload/daily/bill"))

    # Get printers
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = [printer[1] for printer in win32print.EnumPrinters(flags, None, 1)]

    # Store Name Field
    tk.Label(content_frame, text="Store Name", font=("Segoe UI", 9), 
            bg="white", fg="#666", anchor="w").pack(fill='x', padx=20, pady=(15, 3))
    store_entry = tk.Entry(content_frame, textvariable=store_name_var, 
                          font=("Segoe UI", 10), relief="solid", bd=1)
    store_entry.pack(fill='x', padx=20, pady=(0, 10))

    # Printer Field
    tk.Label(content_frame, text="Printer", font=("Segoe UI", 9), 
            bg="white", fg="#666", anchor="w").pack(fill='x', padx=20, pady=(0, 3))
    printer_combo = ttk.Combobox(content_frame, textvariable=printer_var, 
                                values=printers, state="readonly", font=("Segoe UI", 10))
    printer_combo.pack(fill='x', padx=20, pady=(0, 10))

    # Auto Print Checkbox
    auto_print_check = tk.Checkbutton(content_frame, text="Enable automatic printing", 
                                     variable=auto_print_var, font=("Segoe UI", 9), 
                                     bg="white", fg="#333", selectcolor="white", 
                                     activebackground="white", activeforeground="#007acc")
    auto_print_check.pack(fill='x', padx=20, pady=(0, 10))

    # Separator
    separator = tk.Frame(content_frame, height=1, bg="#e0e0e0")
    separator.pack(fill='x', padx=20, pady=8)

    # Retry Time Field
    tk.Label(content_frame, text="Retry Time (seconds)", font=("Segoe UI", 9), 
            bg="white", fg="#666", anchor="w").pack(fill='x', padx=20, pady=(0, 3))
    retry_entry = tk.Entry(content_frame, textvariable=retry_time_var, 
                          font=("Segoe UI", 10), relief="solid", bd=1)
    retry_entry.pack(fill='x', padx=20, pady=(0, 10))

    # API URL Field
    tk.Label(content_frame, text="API URL", font=("Segoe UI", 9), 
            bg="white", fg="#666", anchor="w").pack(fill='x', padx=20, pady=(0, 3))
    api_entry = tk.Entry(content_frame, textvariable=api_url_var, 
                        font=("Segoe UI", 10), relief="solid", bd=1)
    api_entry.pack(fill='x', padx=20, pady=(0, 15))

    # Button Frame
    button_frame = tk.Frame(main_container, bg="#f5f5f5")
    button_frame.pack(fill='x', pady=(8, 0))

    # Save Button
    save_button = tk.Button(button_frame, text="Save Settings", command=save_and_close,
                           font=("Segoe UI", 9), bg="#007acc", fg="white",
                           relief="flat", padx=20, pady=6, cursor="hand2",
                           activebackground="#005a9e", activeforeground="white")
    save_button.pack()

    settings_win.mainloop()
