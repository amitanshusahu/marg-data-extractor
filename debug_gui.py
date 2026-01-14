import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import sqlite3
from config import DB_FILE

DEFAULT_PING_API = "https://wekeyar.core.server.nexusinfotech.co/ping"
DEFAULT_BILL_API = "https://wekeyar.core.server.nexusinfotech.co/api/upload/daily/bill"

def open_debug_gui():
    # Main Window
    debug_win = tk.Tk()
    debug_win.title("NexInsight Debug - API Tester")
    debug_win.geometry("900x600")
    debug_win.configure(bg="#f5f5f5")
    debug_win.resizable(True, True)
    
    # Create notebook (tabbed interface)
    notebook = ttk.Notebook(debug_win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # ========== TAB 1: API TEST ==========
    api_test_frame = tk.Frame(notebook, bg="#f5f5f5")
    notebook.add(api_test_frame, text="API Test")
    
    # Main container with padding
    main_frame = tk.Frame(api_test_frame, bg="#f5f5f5", padx=20, pady=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    
    # Request Frame - All in one row
    request_frame = tk.Frame(main_frame, bg="#f5f5f5")
    request_frame.pack(fill=tk.X, pady=(0, 12))
    
    method_var = tk.StringVar(value="GET")
    method_combo = ttk.Combobox(
        request_frame,
        textvariable=method_var,
        values=["GET", "POST"],
        state="readonly",
        width=8,
        font=("Segoe UI", 10)
    )
    method_combo.pack(side=tk.LEFT, padx=(0, 10))
    
    url_entry = tk.Entry(
        request_frame,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        highlightcolor="#0078d4"
    )
    url_entry.insert(0, DEFAULT_PING_API)
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
    
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
        request_frame,
        text="Send",
        command=send_request,
        font=("Segoe UI", 10, "bold"),
        bg="#0078d4",
        fg="white",
        relief=tk.FLAT,
        cursor="hand2",
        padx=20,
        pady=3
    )
    send_button.pack(side=tk.LEFT)
    
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
    
    # ========== TAB 2: BILL SYNC ==========
    bill_sync_frame = tk.Frame(notebook, bg="#f5f5f5")
    notebook.add(bill_sync_frame, text="Bill Sync")
    
    # Main container for bill sync
    bill_main_frame = tk.Frame(bill_sync_frame, bg="#f5f5f5", padx=20, pady=15)
    bill_main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Bill API URL
    bill_api_frame = tk.Frame(bill_main_frame, bg="#f5f5f5")
    bill_api_frame.pack(fill=tk.X, pady=(0, 10))
    
    bill_api_label = tk.Label(
        bill_api_frame,
        text="Bill API:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=10,
        anchor="w"
    )
    bill_api_label.pack(side=tk.LEFT, padx=(0, 10))
    
    bill_api_entry = tk.Entry(
        bill_api_frame,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        highlightcolor="#0078d4"
    )
    bill_api_entry.insert(0, DEFAULT_BILL_API)
    bill_api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
    
    # Bill ID input
    bill_id_frame = tk.Frame(bill_main_frame, bg="#f5f5f5")
    bill_id_frame.pack(fill=tk.X, pady=(0, 10))
    
    bill_id_label = tk.Label(
        bill_id_frame,
        text="Bill ID:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=10,
        anchor="w"
    )
    bill_id_label.pack(side=tk.LEFT, padx=(0, 10))
    
    bill_id_entry = tk.Entry(
        bill_id_frame,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        highlightcolor="#0078d4"
    )
    bill_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
    
    # Send Bills Function
    def send_bills():
        api_url = bill_api_entry.get().strip()
        bill_id = bill_id_entry.get().strip()
        
        bill_response_text.config(state=tk.NORMAL)
        bill_response_text.delete(1.0, tk.END)
        
        if not api_url:
            bill_response_text.insert(tk.END, "Error: Please enter a Bill API URL\n", "error")
            bill_response_text.config(state=tk.DISABLED)
            return
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Fetch bills based on bill_id input
            if bill_id:
                # Send specific bill
                cursor.execute("SELECT id, content FROM bills WHERE id = ? AND sent_at IS NULL", (bill_id,))
                rows = cursor.fetchall()
                if not rows:
                    # Check if bill exists but already sent
                    cursor.execute("SELECT id FROM bills WHERE id = ?", (bill_id,))
                    if cursor.fetchone():
                        bill_response_text.insert(tk.END, f"Bill ID {bill_id} has already been sent.\n", "warning")
                    else:
                        bill_response_text.insert(tk.END, f"Bill ID {bill_id} not found.\n", "error")
                    conn.close()
                    bill_response_text.config(state=tk.DISABLED)
                    return
            else:
                # Send up to 10 unsent bills
                cursor.execute("SELECT id, content FROM bills WHERE sent_at IS NULL LIMIT 10")
                rows = cursor.fetchall()
                
                if not rows:
                    bill_response_text.insert(tk.END, "No unsent bills found in database.\n", "info")
                    conn.close()
                    bill_response_text.config(state=tk.DISABLED)
                    return
            
            bill_ids = [row[0] for row in rows]
            bill_contents = [row[1] for row in rows]
            
            bill_response_text.insert(tk.END, f"Sending {len(bill_ids)} bill(s) (IDs: {bill_ids})...\n\n", "info")
            bill_response_text.insert(tk.END, "Please wait...\n\n", "info")
            bill_response_text.update()
            
            # Send request
            payload = {
                "bills": bill_contents,
            }
            response = requests.post(api_url, json=payload, timeout=30)
            
            # Clear waiting message
            bill_response_text.delete(1.0, tk.END)
            
            # Display status
            status_color = "success" if response.status_code == 200 else "warning"
            bill_response_text.insert(tk.END, f"Status Code: {response.status_code}\n", status_color)
            bill_response_text.insert(tk.END, f"Response Time: {response.elapsed.total_seconds():.2f}s\n", "info")
            bill_response_text.insert(tk.END, f"Bill IDs Sent: {bill_ids}\n\n", "info")
            
            # If successful, update database
            if response.status_code == 200:
                placeholders = ','.join('?' * len(bill_ids))
                cursor.execute(f"UPDATE bills SET sent_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})", bill_ids)
                conn.commit()
                bill_response_text.insert(tk.END, f"✅ {len(bill_ids)} bill(s) marked as sent in database.\n\n", "success")
            
            # Display headers
            bill_response_text.insert(tk.END, "Headers:\n", "header")
            for key, value in response.headers.items():
                bill_response_text.insert(tk.END, f"  {key}: {value}\n")
            bill_response_text.insert(tk.END, "\n")
            
            # Display response body
            bill_response_text.insert(tk.END, "Response Body:\n", "header")
            try:
                # Try to parse and pretty print JSON
                json_data = response.json()
                formatted_json = json.dumps(json_data, indent=2)
                bill_response_text.insert(tk.END, formatted_json)
            except:
                # If not JSON, display as text
                bill_response_text.insert(tk.END, response.text)
            
            conn.close()
                
        except sqlite3.Error as e:
            bill_response_text.delete(1.0, tk.END)
            bill_response_text.insert(tk.END, f"Database Error: {str(e)}\n", "error")
        except requests.exceptions.Timeout:
            bill_response_text.delete(1.0, tk.END)
            bill_response_text.insert(tk.END, "Error: Request timed out\n", "error")
        except requests.exceptions.ConnectionError:
            bill_response_text.delete(1.0, tk.END)
            bill_response_text.insert(tk.END, "Error: Connection failed. Please check the URL and your internet connection.\n", "error")
        except Exception as e:
            bill_response_text.delete(1.0, tk.END)
            bill_response_text.insert(tk.END, f"Error: {str(e)}\n", "error")
        
        bill_response_text.config(state=tk.DISABLED)
    
    # Send Button
    send_bills_button = tk.Button(
        bill_id_frame,
        text="Send",
        command=send_bills,
        font=("Segoe UI", 10, "bold"),
        bg="#0078d4",
        fg="white",
        relief=tk.FLAT,
        cursor="hand2",
        padx=20,
        pady=3
    )
    send_bills_button.pack(side=tk.LEFT)
    
    # Response Frame
    bill_response_label = tk.Label(
        bill_main_frame,
        text="Response:",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )
    bill_response_label.pack(anchor=tk.W, pady=(0, 5))
    
    # Scrollable Text Widget for Response
    bill_response_text = scrolledtext.ScrolledText(
        bill_main_frame,
        wrap=tk.WORD,
        font=("Consolas", 9),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        padx=10,
        pady=10
    )
    bill_response_text.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags for styling
    bill_response_text.tag_config("error", foreground="#d13438", font=("Segoe UI", 10, "bold"))
    bill_response_text.tag_config("success", foreground="#107c10", font=("Segoe UI", 10, "bold"))
    bill_response_text.tag_config("warning", foreground="#ff8c00", font=("Segoe UI", 10, "bold"))
    bill_response_text.tag_config("info", foreground="#0078d4")
    bill_response_text.tag_config("header", foreground="#333333", font=("Segoe UI", 10, "bold"))
    
    bill_response_text.config(state=tk.DISABLED)
    
    # Bind Enter key to send bills
    bill_id_entry.bind('<Return>', lambda e: send_bills())
    
    debug_win.mainloop()