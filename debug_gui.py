import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json

DEFAULT_PING_API = "https://wekeyar.core.server.nexusinfotech.co/ping"

def open_debug_gui():
    # Main Window
    debug_win = tk.Tk()
    debug_win.title("NexInsight Debug - API Tester")
    debug_win.geometry("700x600")
    debug_win.configure(bg="#f5f5f5")
    debug_win.resizable(True, True)
    
    # Main container with padding
    main_frame = tk.Frame(debug_win, bg="#f5f5f5", padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="API Request Tester",
        font=("Segoe UI", 16, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )
    title_label.pack(pady=(0, 20))
    
    # Request Method Frame
    method_frame = tk.Frame(main_frame, bg="#f5f5f5")
    method_frame.pack(fill=tk.X, pady=(0, 15))
    
    method_label = tk.Label(
        method_frame,
        text="Request Method:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        fg="#333333"
    )
    method_label.pack(side=tk.LEFT, padx=(0, 10))
    
    method_var = tk.StringVar(value="GET")
    method_combo = ttk.Combobox(
        method_frame,
        textvariable=method_var,
        values=["GET", "POST"],
        state="readonly",
        width=10,
        font=("Segoe UI", 10)
    )
    method_combo.pack(side=tk.LEFT)
    
    # API URL Frame
    url_frame = tk.Frame(main_frame, bg="#f5f5f5")
    url_frame.pack(fill=tk.X, pady=(0, 15))
    
    url_label = tk.Label(
        url_frame,
        text="API URL:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        fg="#333333"
    )
    url_label.pack(anchor=tk.W, pady=(0, 5))
    
    url_entry = tk.Entry(
        url_frame,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        highlightcolor="#0078d4"
    )
    url_entry.insert(0, DEFAULT_PING_API)
    url_entry.pack(fill=tk.X, ipady=8)
    
    # Send Button
    def send_request():
        url = url_entry.get().strip()
        method = method_var.get()
        
        response_text.config(state=tk.NORMAL)
        response_text.delete(1.0, tk.END)
        
        if not url:
            response_text.insert(tk.END, "Error: Please enter a URL\n", "error")
            response_text.config(state=tk.DISABLED)
            return
        
        try:
            response_text.insert(tk.END, f"Sending {method} request to:\n{url}\n\n", "info")
            response_text.insert(tk.END, "Please wait...\n\n", "info")
            response_text.update()
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:  # POST
                response = requests.post(url, timeout=10)
            
            # Clear waiting message
            response_text.delete(1.0, tk.END)
            
            # Display status
            status_color = "success" if response.status_code == 200 else "warning"
            response_text.insert(tk.END, f"Status Code: {response.status_code}\n", status_color)
            response_text.insert(tk.END, f"Response Time: {response.elapsed.total_seconds():.2f}s\n\n", "info")
            
            # Display headers
            response_text.insert(tk.END, "Headers:\n", "header")
            for key, value in response.headers.items():
                response_text.insert(tk.END, f"  {key}: {value}\n")
            response_text.insert(tk.END, "\n")
            
            # Display response body
            response_text.insert(tk.END, "Response Body:\n", "header")
            try:
                # Try to parse and pretty print JSON
                json_data = response.json()
                formatted_json = json.dumps(json_data, indent=2)
                response_text.insert(tk.END, formatted_json)
            except:
                # If not JSON, display as text
                response_text.insert(tk.END, response.text)
                
        except requests.exceptions.Timeout:
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, "Error: Request timed out\n", "error")
        except requests.exceptions.ConnectionError:
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, "Error: Connection failed. Please check the URL and your internet connection.\n", "error")
        except Exception as e:
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, f"Error: {str(e)}\n", "error")
        
        response_text.config(state=tk.DISABLED)
    
    send_button = tk.Button(
        main_frame,
        text="Send Request",
        command=send_request,
        font=("Segoe UI", 11, "bold"),
        bg="#0078d4",
        fg="white",
        relief=tk.FLAT,
        cursor="hand2",
        padx=30,
        pady=10
    )
    send_button.pack(pady=(0, 15))
    
    # Response Frame
    response_label = tk.Label(
        main_frame,
        text="Response:",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )
    response_label.pack(anchor=tk.W, pady=(0, 5))
    
    # Scrollable Text Widget for Response
    response_text = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,
        font=("Consolas", 9),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        padx=10,
        pady=10
    )
    response_text.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags for styling
    response_text.tag_config("error", foreground="#d13438", font=("Segoe UI", 10, "bold"))
    response_text.tag_config("success", foreground="#107c10", font=("Segoe UI", 10, "bold"))
    response_text.tag_config("warning", foreground="#ff8c00", font=("Segoe UI", 10, "bold"))
    response_text.tag_config("info", foreground="#0078d4")
    response_text.tag_config("header", foreground="#333333", font=("Segoe UI", 10, "bold"))
    
    response_text.config(state=tk.DISABLED)
    
    # Bind Enter key to send request
    url_entry.bind('<Return>', lambda e: send_request())
    
    debug_win.mainloop()