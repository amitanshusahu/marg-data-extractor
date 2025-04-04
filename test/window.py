import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageOps
import threading

def run():
        root = tk.Tk()
        root.title("Nexinsights")

        # Set window position & size
        window_width, window_height = 450, 300
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
            logo_label = tk.Label(root, image=logo_photo, bg="#F0F8FF")
            logo_label.pack(pady=20)
        except Exception as e:
            print("Logo not found:", e)

        # Header with Logo
        header = tk.Label(root, text="Do you really want to print ?", font=("Arial", 14, "bold"), fg="white", bg="#1E3A8A", pady=10)
        header.pack(fill=tk.X)


        # Button Frame
        button_frame = tk.Frame(root, bg="#F0F8FF")
        button_frame.pack(pady=30)

        # Modern Save Button (Rounded Corners)
        save_button = tk.Button(
            button_frame, text="Print",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2563EB",
            activebackground="#1E40AF",
            padx=15,
            pady=8,
            borderwidth=0,
            relief="flat"
        )
        save_button.pack(side=tk.LEFT, padx=15)

        # Modern Cancel Button (Rounded Corners)
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#DC2626",
            activebackground="#991B1B",
            padx=15,
            pady=8,
            borderwidth=0,
            relief="flat"
        )
        cancel_button.pack(side=tk.RIGHT, padx=15)

        root.mainloop()

threading.Thread(target=run, daemon=True).start()

run()
