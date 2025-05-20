import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from config import CONFIG_FILE
import win32print

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "printer": "",
            "auto_print": True,
            "retry_request_time": 120
        }
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

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
        save_config(config)
        messagebox.showinfo("Settings", "Settings saved successfully.")
        settings_win.destroy()

    settings_win = tk.Tk()
    settings_win.title("Nexinsight Settings")
    settings_win.resizable(False, False)
    settings_win.geometry("370x200")

    pad = {'padx': 10, 'pady': 10}

    # PRINTER
    tk.Label(settings_win, text="Select Printer:", anchor="w").grid(row=0, column=0, sticky="w", **pad)
    printer_var = tk.StringVar(value=config.get("printer", ""))
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    printer_dropdown = ttk.Combobox(settings_win, textvariable=printer_var, values=printers, state="readonly")
    printer_dropdown.grid(row=0, column=1, sticky="ew", **pad)

    # AUTO PRINT
    auto_print_var = tk.BooleanVar(value=config.get("auto_print", True))
    auto_print_check = ttk.Checkbutton(settings_win, text="Print Automatically", variable=auto_print_var)
    auto_print_check.grid(row=1, column=0, columnspan=2, sticky="w", **pad)

    # RETRY TIME
    tk.Label(settings_win, text="Retry Time (seconds):", anchor="w").grid(row=2, column=0, sticky="w", **pad)
    retry_time_var = tk.StringVar(value=str(config.get("retry_request_time", 120)))
    retry_time_entry = ttk.Entry(settings_win, textvariable=retry_time_var)
    retry_time_entry.grid(row=2, column=1, sticky="ew", **pad)

    # SAVE BUTTON
    save_button = ttk.Button(settings_win, text="Save", command=save_and_close)
    save_button.grid(row=3, column=0, columnspan=2, pady=(0, 10))

    settings_win.columnconfigure(1, weight=1)
    settings_win.mainloop()
