import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import sqlite3
import tempfile
import os
import subprocess
import win32print
import win32api
from pathlib import Path
import sys
from config import DB_FILE
from settings_gui import load_config

BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
SUMATRA_PATH = str(BASE_DIR / "SumatraPDF-3.5.2-64.exe")

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
    
    # ========== TAB 3: PRINTER TEST ==========
    printer_test_frame = tk.Frame(notebook, bg="#f5f5f5")
    notebook.add(printer_test_frame, text="Printer Test")
    
    # Main container for printer test
    printer_main_frame = tk.Frame(printer_test_frame, bg="#f5f5f5", padx=20, pady=15)
    printer_main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Printer Info Section
    printer_info_frame = tk.LabelFrame(
        printer_main_frame,
        text="Printer Information",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#333333",
        padx=15,
        pady=10
    )
    printer_info_frame.pack(fill=tk.X, pady=(0, 15))
    
    # Load config to get printer
    config = load_config()
    configured_printer = config.get("printer", "")
    default_printer = win32print.GetDefaultPrinter()
    
    # Configured Printer
    config_printer_frame = tk.Frame(printer_info_frame, bg="#f5f5f5")
    config_printer_frame.pack(fill=tk.X, pady=(0, 5))
    
    tk.Label(
        config_printer_frame,
        text="Configured Printer:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=18,
        anchor="w"
    ).pack(side=tk.LEFT)
    
    configured_printer_label = tk.Label(
        config_printer_frame,
        text=configured_printer if configured_printer else "(Not set - will use default)",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#0078d4" if configured_printer else "#666666"
    )
    configured_printer_label.pack(side=tk.LEFT)
    
    # Default Printer
    default_printer_frame = tk.Frame(printer_info_frame, bg="#f5f5f5")
    default_printer_frame.pack(fill=tk.X, pady=(0, 5))
    
    tk.Label(
        default_printer_frame,
        text="Default Printer:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=18,
        anchor="w"
    ).pack(side=tk.LEFT)
    
    tk.Label(
        default_printer_frame,
        text=default_printer,
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(side=tk.LEFT)
    
    # Effective Printer (what will be used)
    effective_printer = configured_printer if configured_printer else default_printer
    
    effective_printer_frame = tk.Frame(printer_info_frame, bg="#f5f5f5")
    effective_printer_frame.pack(fill=tk.X)
    
    tk.Label(
        effective_printer_frame,
        text="Effective Printer:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=18,
        anchor="w"
    ).pack(side=tk.LEFT)
    
    tk.Label(
        effective_printer_frame,
        text=effective_printer,
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#107c10"
    ).pack(side=tk.LEFT)
    
    # Refresh printer info
    def refresh_printer_info():
        nonlocal effective_printer
        config = load_config()
        configured_printer = config.get("printer", "")
        default_printer = win32print.GetDefaultPrinter()
        effective_printer = configured_printer if configured_printer else default_printer
        
        configured_printer_label.config(
            text=configured_printer if configured_printer else "(Not set - will use default)",
            fg="#0078d4" if configured_printer else "#666666"
        )
        printer_response_text.config(state=tk.NORMAL)
        printer_response_text.delete(1.0, tk.END)
        printer_response_text.insert(tk.END, "Printer info refreshed.\n", "info")
        printer_response_text.insert(tk.END, f"Effective printer: {effective_printer}\n", "success")
        printer_response_text.config(state=tk.DISABLED)
    
    refresh_btn = tk.Button(
        printer_info_frame,
        text="🔄 Refresh",
        command=refresh_printer_info,
        font=("Segoe UI", 9),
        bg="#e0e0e0",
        relief=tk.FLAT,
        cursor="hand2",
        padx=10
    )
    refresh_btn.pack(anchor=tk.E, pady=(10, 0))
    
    # Test Options Section
    test_options_frame = tk.LabelFrame(
        printer_main_frame,
        text="Print Test Options",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#333333",
        padx=15,
        pady=10
    )
    test_options_frame.pack(fill=tk.X, pady=(0, 15))
    
    # Custom test message
    test_msg_frame = tk.Frame(test_options_frame, bg="#f5f5f5")
    test_msg_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(
        test_msg_frame,
        text="Test Message:",
        font=("Segoe UI", 10),
        bg="#f5f5f5",
        width=12,
        anchor="w"
    ).pack(side=tk.LEFT, padx=(0, 10))
    
    test_message_entry = tk.Entry(
        test_msg_frame,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        highlightcolor="#0078d4"
    )
    test_message_entry.insert(0, "NexInsights Printer Test - If you see this, your printer is working!")
    test_message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
    
    # Buttons Frame
    buttons_frame = tk.Frame(test_options_frame, bg="#f5f5f5")
    buttons_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Windows Native Print Test
    def test_windows_print():
        printer_response_text.config(state=tk.NORMAL)
        printer_response_text.delete(1.0, tk.END)
        
        test_msg = test_message_entry.get().strip()
        if not test_msg:
            test_msg = "NexInsights Printer Test"
        
        printer_response_text.insert(tk.END, f"Testing Windows Native Print...\n", "info")
        printer_response_text.insert(tk.END, f"Printer: {effective_printer}\n\n", "info")
        printer_response_text.update()
        
        try:
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("=" * 50 + "\n")
                f.write("       NEXINSIGHTS PRINTER TEST\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Test Message:\n{test_msg}\n\n")
                f.write(f"Printer: {effective_printer}\n")
                f.write(f"Test Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("=" * 50 + "\n")
                f.write("If you see this page, your printer is working!\n")
                f.write("=" * 50 + "\n")
                temp_file = f.name
            
            # Print using Windows ShellExecute
            win32api.ShellExecute(
                0,
                "print",
                temp_file,
                f'/d:"{effective_printer}"',
                ".",
                0
            )
            
            printer_response_text.insert(tk.END, "✅ Print job sent successfully!\n\n", "success")
            printer_response_text.insert(tk.END, "Check your printer for the test page.\n", "info")
            printer_response_text.insert(tk.END, f"Temporary file: {temp_file}\n", "info")
            
            # Schedule file deletion after a delay
            debug_win.after(5000, lambda: os.unlink(temp_file) if os.path.exists(temp_file) else None)
            
        except Exception as e:
            printer_response_text.insert(tk.END, f"❌ Print failed: {str(e)}\n", "error")
        
        printer_response_text.config(state=tk.DISABLED)
    
    # SumatraPDF Print Test
    def test_sumatra_print():
        printer_response_text.config(state=tk.NORMAL)
        printer_response_text.delete(1.0, tk.END)
        
        test_msg = test_message_entry.get().strip()
        if not test_msg:
            test_msg = "NexInsights Printer Test"
        
        printer_response_text.insert(tk.END, f"Testing SumatraPDF Print...\n", "info")
        printer_response_text.insert(tk.END, f"Printer: {effective_printer}\n", "info")
        printer_response_text.insert(tk.END, f"SumatraPDF: {SUMATRA_PATH}\n\n", "info")
        printer_response_text.update()
        
        # Check if SumatraPDF exists
        if not os.path.exists(SUMATRA_PATH):
            printer_response_text.insert(tk.END, f"❌ SumatraPDF not found at:\n{SUMATRA_PATH}\n\n", "error")
            printer_response_text.insert(tk.END, "Please ensure SumatraPDF-3.5.2-64.exe is in the application directory.\n", "warning")
            printer_response_text.config(state=tk.DISABLED)
            return
        
        try:
            # Create a simple PDF for testing using reportlab if available, otherwise use a text file approach
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
                    temp_pdf = f.name
                
                c = canvas.Canvas(temp_pdf, pagesize=letter)
                c.setFont("Helvetica-Bold", 24)
                c.drawString(100, 700, "NEXINSIGHTS PRINTER TEST")
                c.setFont("Helvetica", 12)
                c.drawString(100, 650, f"Test Message: {test_msg[:50]}")
                c.drawString(100, 630, f"Printer: {effective_printer}")
                c.drawString(100, 610, f"Method: SumatraPDF")
                c.drawString(100, 590, f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 550, "If you see this page, SumatraPDF printing is working!")
                c.save()
                
                printer_response_text.insert(tk.END, "Created test PDF using reportlab.\n", "info")
                
            except ImportError:
                # Fallback: Look for any existing PDF in the PDF_DIR
                from config import PDF_DIR
                pdf_files = list(PDF_DIR.glob("*.pdf"))
                
                if pdf_files:
                    temp_pdf = str(pdf_files[0])
                    printer_response_text.insert(tk.END, f"Using existing PDF: {temp_pdf}\n", "info")
                else:
                    # Create a minimal PDF manually
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
                        # Minimal valid PDF
                        pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 128 >> stream
BT
/F1 24 Tf
100 700 Td
(NEXINSIGHTS PRINTER TEST) Tj
0 -50 Td
/F1 12 Tf
(If you see this, SumatraPDF is working!) Tj
ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000446 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
525
%%EOF"""
                        f.write(pdf_content)
                        temp_pdf = f.name
                    printer_response_text.insert(tk.END, "Created minimal test PDF.\n", "info")
            
            # Print using SumatraPDF
            cmd = f'"{SUMATRA_PATH}" -print-to "{effective_printer}" "{temp_pdf}"'
            printer_response_text.insert(tk.END, f"\nExecuting: {cmd}\n\n", "info")
            printer_response_text.update()
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                printer_response_text.insert(tk.END, "✅ SumatraPDF print job sent successfully!\n\n", "success")
                printer_response_text.insert(tk.END, "Check your printer for the test page.\n", "info")
            else:
                printer_response_text.insert(tk.END, f"⚠️ SumatraPDF returned code: {result.returncode}\n", "warning")
                if result.stderr:
                    printer_response_text.insert(tk.END, f"Stderr: {result.stderr}\n", "error")
                if result.stdout:
                    printer_response_text.insert(tk.END, f"Stdout: {result.stdout}\n", "info")
            
            # Clean up temp file after delay
            if 'temp_pdf' in dir() and temp_pdf.startswith(tempfile.gettempdir()):
                debug_win.after(5000, lambda: os.unlink(temp_pdf) if os.path.exists(temp_pdf) else None)
            
        except subprocess.TimeoutExpired:
            printer_response_text.insert(tk.END, "❌ Print command timed out.\n", "error")
        except Exception as e:
            printer_response_text.insert(tk.END, f"❌ Print failed: {str(e)}\n", "error")
        
        printer_response_text.config(state=tk.DISABLED)
    
    # List all printers
    def list_all_printers():
        printer_response_text.config(state=tk.NORMAL)
        printer_response_text.delete(1.0, tk.END)
        
        printer_response_text.insert(tk.END, "Available Printers:\n\n", "header")
        
        try:
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            
            for i, printer in enumerate(printers, 1):
                printer_name = printer[2]
                is_default = " (DEFAULT)" if printer_name == default_printer else ""
                is_configured = " (CONFIGURED)" if printer_name == configured_printer else ""
                
                if is_default or is_configured:
                    printer_response_text.insert(tk.END, f"{i}. {printer_name}{is_default}{is_configured}\n", "success")
                else:
                    printer_response_text.insert(tk.END, f"{i}. {printer_name}\n")
            
            printer_response_text.insert(tk.END, f"\nTotal: {len(printers)} printer(s) found.\n", "info")
            
        except Exception as e:
            printer_response_text.insert(tk.END, f"Error listing printers: {str(e)}\n", "error")
        
        printer_response_text.config(state=tk.DISABLED)
    
    # Test buttons
    windows_print_btn = tk.Button(
        buttons_frame,
        text="🖨️ Test Windows Print",
        command=test_windows_print,
        font=("Segoe UI", 10, "bold"),
        bg="#0078d4",
        fg="white",
        relief=tk.FLAT,
        cursor="hand2",
        padx=15,
        pady=5
    )
    windows_print_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    sumatra_print_btn = tk.Button(
        buttons_frame,
        text="📄 Test SumatraPDF Print",
        command=test_sumatra_print,
        font=("Segoe UI", 10, "bold"),
        bg="#107c10",
        fg="white",
        relief=tk.FLAT,
        cursor="hand2",
        padx=15,
        pady=5
    )
    sumatra_print_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    list_printers_btn = tk.Button(
        buttons_frame,
        text="📋 List All Printers",
        command=list_all_printers,
        font=("Segoe UI", 10),
        bg="#e0e0e0",
        relief=tk.FLAT,
        cursor="hand2",
        padx=15,
        pady=5
    )
    list_printers_btn.pack(side=tk.LEFT)
    
    # Response Frame
    printer_response_label = tk.Label(
        printer_main_frame,
        text="Output:",
        font=("Segoe UI", 10, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    )
    printer_response_label.pack(anchor=tk.W, pady=(0, 5))
    
    # Scrollable Text Widget for Response
    printer_response_text = scrolledtext.ScrolledText(
        printer_main_frame,
        wrap=tk.WORD,
        font=("Consolas", 9),
        relief=tk.FLAT,
        bg="white",
        highlightthickness=1,
        highlightbackground="#cccccc",
        padx=10,
        pady=10
    )
    printer_response_text.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags for styling
    printer_response_text.tag_config("error", foreground="#d13438", font=("Segoe UI", 10, "bold"))
    printer_response_text.tag_config("success", foreground="#107c10", font=("Segoe UI", 10, "bold"))
    printer_response_text.tag_config("warning", foreground="#ff8c00", font=("Segoe UI", 10, "bold"))
    printer_response_text.tag_config("info", foreground="#0078d4")
    printer_response_text.tag_config("header", foreground="#333333", font=("Segoe UI", 10, "bold"))
    
    printer_response_text.config(state=tk.DISABLED)
    
    debug_win.mainloop()