import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from config import CONFIG_FILE
import win32print

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"printer": "", "ask_before_print": False, "auto_print": True}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def open_settings():
    config = load_config()

    def save_and_close():
        config["printer"] = printer_var.get()
        config["ask_before_print"] = ask_before_var.get()
        config["auto_print"] = auto_print_var.get()
        save_config(config)
        messagebox.showinfo("Settings", "Saved successfully!")
        settings_win.destroy()

    settings_win = tk.Tk()
    settings_win.title("App Settings")

    tk.Label(settings_win, text="Printer:").grid(row=0, column=0, sticky="w")
    printer_var = tk.StringVar(value=config["printer"])
    printers = [printer[2] for printer in win32print.EnumPrinters(2)]
    printer_dropdown = ttk.Combobox(settings_win, textvariable=printer_var, values=printers)
    printer_dropdown.grid(row=0, column=1)

    ask_before_var = tk.BooleanVar(value=config["ask_before_print"])
    tk.Checkbutton(settings_win, text="Ask before print", variable=ask_before_var).grid(row=1, columnspan=2, sticky="w")

    auto_print_var = tk.BooleanVar(value=config["auto_print"])
    tk.Checkbutton(settings_win, text="Print automatically", variable=auto_print_var).grid(row=2, columnspan=2, sticky="w")

    tk.Button(settings_win, text="Save", command=save_and_close).grid(row=3, columnspan=2)

    settings_win.mainloop()
